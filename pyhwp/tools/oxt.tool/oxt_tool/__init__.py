# -*- coding: utf-8 -*-
import logging


def console(soffice='soffice'):
    import uno
    import unokit.contexts
    import unokit.services
    import oxt_tool.remote

    with oxt_tool.remote.new_remote_context(soffice=soffice) as context:
        desktop = unokit.services.css.frame.Desktop()
        def new_textdoc():
            return desktop.loadComponentFromURL('private:factory/swriter',
                                                '_blank', 0, tuple())
        from unokit.util import dump, dumpdir
        local = dict(uno=uno, context=context,
                     css=unokit.services.css, dump=dump, dumpdir=dumpdir,
                     desktop=desktop, new_textdoc=new_textdoc)
        __import__('code').interact(banner='oxt-console', local=local)


def dict_to_namedvalue(d):
    import uno
    nv = list()
    for n, v in d.items():
        if isinstance(v, dict):
            v = dict_to_namedvalue(v)
        item = uno.createUnoStruct('com.sun.star.beans.NamedValue')
        item.Name = n
        item.Value = v
        nv.append(item)
    return tuple(nv)


def test_remotely(soffice, discover_dirs, extra_path, logconf_path):
    import sys
    import os
    import os.path
    import discover
    import oxt_tool.remote

    logger = logging.getLogger('unokit')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    logfmt = logging.Formatter(('frontend %5d ' % os.getpid())
                               +'%(message)s')
    logchn = logging.StreamHandler()
    logchn.setFormatter(logfmt)
    logger = logging.getLogger('frontend')
    logger.addHandler(logchn)
    logger.setLevel(logging.INFO)

    working_dir = sys.argv[1]
    working_dir = os.path.abspath(working_dir)

    for path in sys.path:
        logger.info('sys.path: %s', path)

    if logconf_path:
        logconf_path = os.path.abspath(logconf_path)

    backend_path = sys.modules['oxt_tool'].__file__
    backend_path = os.path.dirname(backend_path)
    backend_path = os.path.join(backend_path, 'backend.py')
    backend_name = 'backend.TestRunnerJob'

    tss = []
    for d in discover_dirs:
        d = os.path.abspath(d)
        logger.info('discover tests: %s', d)
        testloader = discover.DiscoveringTestLoader()
        testsuite = testloader.discover(d)
        tss.append(testsuite)
    import unittest
    testsuite = unittest.TestSuite(tss)

    with oxt_tool.remote.new_remote_context(soffice=soffice) as context:
        logger.info('remote context created')
        factory = load_component(backend_path, backend_name)
        if factory:
            backendjob = factory.createInstanceWithContext(context)
            if backendjob:
                import cPickle
                from unokit.adapters import OutputStreamToFileLike
                pickled_testsuite = cPickle.dumps(testsuite)
                outputstream = OutputStreamToFileLike(sys.stderr)
                logstream = OutputStreamToFileLike(sys.stderr)
                args = dict(outputstream=outputstream,
                            logstream=logstream,
                            pickled_testsuite=pickled_testsuite,
                            extra_path=tuple(extra_path),
                            logconf_path=logconf_path,
                            working_dir=working_dir)
                args = dict_to_namedvalue(args)
                result = backendjob.execute(args)
                result = str(result)
                result = cPickle.loads(result)
                return 0 if result['successful'] else 1
    return -1


def load_component(component_path, component_name):
    import os
    import os.path
    import uno
    from unokit.services import css
    loader = css.loader.Python()
    if loader:
        component_path = os.path.abspath(component_path)
        component_url = uno.systemPathToFileUrl(component_path)

        return loader.activate(component_name, '',
                               component_url, None)


def console_in_proc(soffice='soffice'):
    import os
    import unohelper
    from com.sun.star.task import XJob
    import oxt_tool.remote

    logfmt = logging.Formatter(('frontend %5d ' % os.getpid())
                               +'%(message)s')
    logchn = logging.StreamHandler()
    logchn.setFormatter(logfmt)
    logger = logging.getLogger('frontend')
    logger.addHandler(logchn)
    logger.setLevel(logging.INFO)

    class ConsoleInput(unohelper.Base, XJob):

        def __init__(self, context):
            self.context = context

        def execute(self, arguments):
            prompt, = arguments
            try:
                return raw_input(prompt.Value)
            except EOFError:
                return None

    import sys
    import os.path
    backend_path = sys.modules['oxt_tool'].__file__
    backend_path = os.path.dirname(backend_path)
    backend_path = os.path.join(backend_path, 'backend.py')
    backend_name = 'backend.ConsoleJob'

    with oxt_tool.remote.new_remote_context(soffice=soffice) as context:
        logger.info('remote context created')
        factory = load_component(backend_path, backend_name)
        if factory:
            backendjob = factory.createInstanceWithContext(context)
            if backendjob:
                from unokit.adapters import OutputStreamToFileLike
                outstream = OutputStreamToFileLike(sys.stderr)
                args = dict(inp=ConsoleInput(context),
                            outstream=outstream)
                args = dict_to_namedvalue(args)
                backendjob.execute(args)


class LoEnviron(object):

    def __init__(self, program_dir):
        self.program_dir = program_dir

    @property
    def rc_ext(self):
        import sys
        if sys.platform == 'win32':
            return '.ini'
        else:
            return 'rc'


    @property
    def fundamentalrc(self):
        import os.path
        filename = 'fundamental' + self.rc_ext
        return os.path.join(self.program_dir, filename)


    @property
    def ure_bootstrap(self):
        return 'vnd.sun.star.pathname:' + self.fundamentalrc


def run_in_lo(soffice='soffice'):
    import os
    import sys
    import os.path

    uno_pythonpath = os.environ['UNO_PYTHONPATH'].split(os.pathsep)
    sys.path.extend(uno_pythonpath)

    loenv = LoEnviron(os.environ['LO_PROGRAM'])
    os.environ['URE_BOOTSTRAP'] = loenv.ure_bootstrap

    import oxt_tool.remote

    logger = logging.getLogger('unokit')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    logger = logging.getLogger('oxt_tool')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    logfmt = logging.Formatter(('frontend %5d ' % os.getpid())
                               +'%(message)s')
    logchn = logging.StreamHandler()
    logchn.setFormatter(logfmt)
    logger = logging.getLogger('frontend')
    logger.addHandler(logchn)
    logger.setLevel(logging.INFO)

    for path in sys.path:
        logger.info('sys.path: %s', path)

    working_dir = os.getcwd()
    working_dir = os.path.abspath(working_dir)
    argv = list(sys.argv[1:])

    if argv[0].startswith('--logfile='):
        logfile = argv[0][len('--logfile='):]
        argv = argv[1:]
    else:
        logfile = None
    argv[0] = os.path.abspath(argv[0])
    print argv

    backend_path = sys.modules['oxt_tool'].__file__
    backend_path = os.path.dirname(backend_path)
    backend_path = os.path.join(backend_path, 'backend.py')
    backend_name = 'backend.RemoteRunJob'

    with oxt_tool.remote.new_remote_context(soffice=soffice) as context:
        logger.info('remote context created')
        factory = load_component(backend_path, backend_name)
        if factory:
            backendjob = factory.createInstanceWithContext(context)
            if backendjob:
                import cPickle
                from unokit.adapters import OutputStreamToFileLike
                from unokit.adapters import InputStreamFromFileLike
                stdin = InputStreamFromFileLike(sys.stdin)
                stdout = OutputStreamToFileLike(sys.stdout)
                stderr = OutputStreamToFileLike(sys.stderr)
                path = cPickle.dumps(sys.path)
                argv = cPickle.dumps(argv)
                args = dict(logfile=logfile,
                            working_dir=working_dir,
                            path=path,
                            argv=argv,
                            stdin=stdin,
                            stdout=stdout,
                            stderr=stderr)
                args = dict_to_namedvalue(args)
                return backendjob.execute(args)
    return -1


def install(unopkg='unopkg'):
    import sys
    cmd = [unopkg, 'add', '-v', '-s']
    cmd.extend(sys.argv[1:])
    cmd = [('"%s"' % x) if ' ' not in x else x
            for x in cmd]
    cmd = ' '.join(cmd)
    import os
    return os.system(cmd)


class Console(object):
    def __init__(self, buildout, name, options):
        import os.path
        self.__name = name
        self.__logger = logging.getLogger(name)
        self.__bindir = buildout['buildout']['bin-directory']

        soffice = options.get('soffice', 'soffice').strip()
        if not os.path.exists(soffice):
            self.__skip = True
            self.__logger.info('soffice not found at: %s', soffice)
            self.__logger.info('installation will be skipped')
            return

        in_proc = options.get('in_proc', 'true').strip().lower()
        in_proc = in_proc in ['true', 'yes', '1']

        self.__python = options.get('python', '').strip()
        self.__soffice = soffice
        self.__in_proc = in_proc
        self.__skip = False

    def install(self):
        if self.__skip:
            self.__logger.info('skipped')
            return []

        from zc.buildout import easy_install
        import pkg_resources
        import sys
        ws = [pkg_resources.get_distribution(dist)
              for dist in ['unokit', 'oxt.tool']]
        if self.__in_proc:
            func = 'console_in_proc'
        else:
            func = 'console'
        entrypoints = [(self.__name, 'oxt_tool', func)]
        arguments = '%r' % self.__soffice
        if self.__python:
            python = self.__python
        else:
            python = sys.executable
        return easy_install.scripts(entrypoints,
                                    ws, python, self.__bindir,
                                    arguments=arguments)

    update = install


class TestRunner(object):
    def __init__(self, buildout, name, options):
        import os.path
        self.__name = name
        self.__logger = logging.getLogger(name)
        self.__bindir = buildout['buildout']['bin-directory']
        self.__skip = False
        self.__python = options.get('python', '').strip()

        self.__soffice = options.get('soffice', 'soffice').strip()
        if not os.path.exists(self.__soffice):
            self.__skip = True
            self.__logger.info('soffice not found at: %s', self.__soffice)
            self.__logger.info('installation will be skipped')
            return
        self.__discover = options['discover'].split()
        self.__extra_path = options['extra_path'].split()
        self.__logconf_path = options.get('logconf_path')

    def install(self):
        if self.__skip:
            self.__logger.info('skipped')
            return []

        from zc.buildout import easy_install
        import pkg_resources
        import sys
        ws = [pkg_resources.get_distribution(dist)
              for dist in ['unokit', 'oxt.tool', 'discover']]
        entrypoints = [(self.__name, 'oxt_tool', 'test_remotely')]
        arguments = '%r, %r, %r, %r'
        arguments = arguments % (self.__soffice,
                                 self.__discover,
                                 self.__extra_path,
                                 self.__logconf_path)
        if self.__python:
            python = self.__python
        else:
            python = sys.executable
        return easy_install.scripts(entrypoints,
                                    ws, python, self.__bindir,
                                    arguments=arguments)

    update = install


class Installer(object):
    def __init__(self, buildout, name, options):
        import os.path
        self.__name = name
        self.__logger = logging.getLogger(name)
        self.__bindir = buildout['buildout']['bin-directory']

        unopkg = options.get('unopkg', 'unopkg').strip()
        if not os.path.exists(unopkg):
            self.__skip = True
            self.__logger.info('unopkg not found at: %s', unopkg)
            self.__logger.info('installation will be skipped')
            return

        self.__unopkg = unopkg
        self.__skip = False

    def install(self):
        if self.__skip:
            self.__logger.info('skipped')
            return []

        from zc.buildout import easy_install
        import pkg_resources
        import sys
        ws = [pkg_resources.get_distribution(dist)
              for dist in ['unokit', 'oxt.tool']]
        entrypoints = [(self.__name, 'oxt_tool', 'install')]
        arguments = '%r' % self.__unopkg
        return easy_install.scripts(entrypoints,
                                    ws, sys.executable, self.__bindir,
                                    arguments=arguments)

    update = install
