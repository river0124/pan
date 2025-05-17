# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from io import BytesIO
from unittest import TestCase
import sys

from six import add_metaclass

from hwp5.bintype import read_type
from hwp5.dataio import ARRAY, N_ARRAY
from hwp5.dataio import BSTR
from hwp5.dataio import BYTE
from hwp5.dataio import Enum
from hwp5.dataio import EnumType
from hwp5.dataio import Flags
from hwp5.dataio import INT8
from hwp5.dataio import INT16
from hwp5.dataio import INT32
from hwp5.dataio import UINT8
from hwp5.dataio import UINT16
from hwp5.dataio import UINT32
from hwp5.dataio import ParseError
from hwp5.dataio import Struct
from hwp5.dataio import StructType
from hwp5.dataio import decode_utf16le_with_hypua
from hwp5.dataio import typed_struct_attributes
from hwp5.dataio import _parse_flags_args


PY3 = sys.version_info.major == 3
if PY3:
    long = int
    unicode = str


class TestArray(TestCase):
    def test_new(self):
        t1 = ARRAY(INT32, 3)
        t2 = ARRAY(INT32, 3)
        assert t1 is t2

        assert N_ARRAY(INT32, INT32) is N_ARRAY(INT32, INT32)

    def test_BSTR(self):
        assert type(BSTR(u'abc')) is unicode

    def test_hello(self):
        assert INT32.basetype is int

    def test_slots(self):
        a = INT32()
        self.assertRaises(Exception, setattr, a, 'randomattr', 1)


class TestTypedAttributes(TestCase):

    def test_typed_struct_attributes(self):

        class SomeRandomStruct(Struct):
            @staticmethod
            def attributes():
                yield INT32, 'a'
                yield BSTR, 'b'
                yield ARRAY(INT32, 3), 'c'

        attributes = dict(a=1, b=u'abc', c=(4, 5, 6))
        typed_attributes = typed_struct_attributes(
            SomeRandomStruct, attributes, dict()
        )
        typed_attributes = list(typed_attributes)
        expected = [dict(name='a', type=INT32, value=1),
                    dict(name='b', type=BSTR, value='abc'),
                    dict(name='c', type=ARRAY(INT32, 3), value=(4, 5, 6))]
        self.assertEqual(expected, typed_attributes)

    def test_typed_struct_attributes_inherited(self):

        class Hello(Struct):
            @staticmethod
            def attributes():
                yield INT32, 'a'

        class Hoho(Hello):
            @staticmethod
            def attributes():
                yield BSTR, 'b'

        attributes = dict(a=1, b=u'abc', c=(2, 2))
        result = typed_struct_attributes(Hoho, attributes, dict())
        result = list(result)
        expected = [dict(name='a', type=INT32, value=1),
                    dict(name='b', type=BSTR, value='abc'),
                    dict(name='c', type=tuple, value=(2, 2))]
        self.assertEqual(expected, result)


class TestStructType(TestCase):
    def test_assign_enum_flags_name(self):

        @add_metaclass(StructType)
        class Foo(object):
            bar = Enum()
            baz = Flags(UINT16)
        self.assertEqual('bar', Foo.bar.__name__)
        self.assertEqual(Foo, Foo.bar.scoping_struct)
        self.assertEqual('baz', Foo.baz.__name__)

    def test_parse_members(self):

        @add_metaclass(StructType)
        class A(object):

            @classmethod
            def attributes(cls):
                yield UINT8, 'uint8'
                yield UINT16, 'uint16'
                yield UINT32, 'uint32'

        values = dict(uint8=8, uint16=16, uint32=32)

        def getvalue(member):
            return values[member['name']]

        context = dict()
        result = list(A.parse_members(context, getvalue))
        self.assertEqual([dict(name='uint8', type=UINT8, value=8),
                          dict(name='uint16', type=UINT16, value=16),
                          dict(name='uint32', type=UINT32, value=32)], result)

    def test_parse_members_condition(self):

        def uint32_is_32(context, values):
            return values['uint32'] == 32

        @add_metaclass(StructType)
        class A(object):

            @classmethod
            def attributes(cls):
                yield UINT8, 'uint8'
                yield UINT16, 'uint16'
                yield UINT32, 'uint32'
                yield dict(type=UINT32, name='extra', condition=uint32_is_32)

        values = dict(uint8=8, uint16=16, uint32=32, extra=666)

        def getvalue(member):
            return values[member['name']]

        context = dict()
        result = list(A.parse_members(context, getvalue))
        self.assertEqual([dict(name='uint8', type=UINT8, value=8),
                          dict(name='uint16', type=UINT16, value=16),
                          dict(name='uint32', type=UINT32, value=32),
                          dict(name='extra', type=UINT32, value=666,
                               condition=uint32_is_32)],
                         result)

    def test_parse_members_empty(self):

        @add_metaclass(StructType)
        class A(object):
            pass

        value = dict()

        def getvalue(member):
            return value[member['name']]

        context = dict()
        result = list(A.parse_members_with_inherited(context, getvalue))
        self.assertEqual([], result)

    def test_parse_members_inherited(self):

        @add_metaclass(StructType)
        class A(object):

            @classmethod
            def attributes(cls):
                yield UINT8, 'uint8'
                yield UINT16, 'uint16'
                yield UINT32, 'uint32'

        class B(A):
            @classmethod
            def attributes(cls):
                yield INT8, 'int8'
                yield INT16, 'int16'
                yield INT32, 'int32'

        value = dict(uint8=8, uint16=16, uint32=32,
                     int8=-1, int16=-16, int32=-32)

        def getvalue(member):
            return value[member['name']]

        context = dict()
        result = list(B.parse_members_with_inherited(context, getvalue))
        self.assertEqual([dict(name='uint8', type=UINT8, value=8),
                          dict(name='uint16', type=UINT16, value=16),
                          dict(name='uint32', type=UINT32, value=32),
                          dict(name='int8', type=INT8, value=-1),
                          dict(name='int16', type=INT16, value=-16),
                          dict(name='int32', type=INT32, value=-32)],
                         result)


class TestEnumType(TestCase):
    def test_enum(self):
        Foo = EnumType(
            str('Foo'),
            (int,),
            dict(items=['a', 'b', 'c'], moreitems=dict(d=1, e=4))
        )

        self.assertRaises(AttributeError, getattr, Foo, 'items')
        self.assertRaises(AttributeError, getattr, Foo, 'moreitems')

        # class members
        self.assertEqual(0, Foo.a)
        self.assertEqual(1, Foo.b)
        self.assertEqual(2, Foo.c)
        self.assertEqual(1, Foo.d)
        self.assertEqual(4, Foo.e)
        self.assertTrue(isinstance(Foo.a, Foo))

        # same instances
        self.assertTrue(Foo(0) is Foo(0))
        self.assertTrue(Foo(0) is Foo.a)

        # not an instance of int
        self.assertTrue(Foo(0) is not 0)

        # instance names
        self.assertEqual('a', Foo.a.name)
        self.assertEqual('b', Foo.b.name)

        # aliases
        self.assertEqual('b', Foo.d.name)
        self.assertTrue(Foo.b is Foo.d)

        # repr
        self.assertEqual('Foo.a', repr(Foo(0)))
        self.assertEqual('Foo.b', repr(Foo(1)))
        self.assertEqual('Foo.e', repr(Foo(4)))

        # frozen attribute set
        self.assertRaises(AttributeError, setattr, Foo(0), 'bar', 0)
        if sys.platform.startswith('java'):  # Jython 2.5.3
            self.assertRaises(TypeError, setattr, Foo(0), 'name', 'a')
        else:
            self.assertRaises(AttributeError, setattr, Foo(0), 'name', 'a')

        # undefined value
        # self.assertRaises(ValueError, Foo, 5)

        # undefined value: warning but not error
        undefined = Foo(5)
        self.assertTrue(isinstance(undefined, Foo))
        self.assertEqual(None, undefined.name)
        self.assertEqual('Foo(5)', repr(undefined))

        # can't define anymore
        self.assertRaises(TypeError, Foo, 5, 'f')

        # duplicate names
        self.assertRaises(Exception, Enum, 'a', a=1)


class TestFlags(TestCase):
    def test_parse_args(self):
        x = list(_parse_flags_args([0, 1, long, 'bit01']))
        bit01 = ('bit01', (0, 1, long))
        self.assertEqual([bit01], x)

        x = list(_parse_flags_args([2, 3, 'bit23']))
        bit23 = ('bit23', (2, 3, int))
        self.assertEqual([bit23], x)

        x = list(_parse_flags_args([4, long, 'bit4']))
        bit4 = ('bit4', (4, 4, long))
        self.assertEqual([bit4], x)

        x = list(_parse_flags_args([5, 'bit5']))
        bit5 = ('bit5', (5, 5, int))

        x = list(_parse_flags_args([0, 1, long, 'bit01',
                                    2, 3, 'bit23',
                                    4, long, 'bit4',
                                    5, 'bit5']))
        self.assertEqual([bit01, bit23, bit4, bit5], x)

    def test_basetype(self):
        MyFlags = Flags(UINT32)
        self.assertEqual(UINT32, MyFlags.basetype)

    def test_bitfields(self):
        MyEnum = Enum(a=1, b=2)
        MyFlags = Flags(
            UINT32,
            0, 1, 'field0',
            2, 4, MyEnum, 'field2'
        )
        bitfields = MyFlags.bitfields
        f = bitfields['field0']
        self.assertEqual((0, 1, int),
                         (f.lsb, f.msb, f.valuetype))
        f = bitfields['field2']
        self.assertEqual((2, 4, MyEnum),
                         (f.lsb, f.msb, f.valuetype))

    @property
    def ByteFlags(self):
        return Flags(BYTE,
                     0, 3, 'low',
                     4, 7, 'high')

    def test_dictvalue(self):
        flags = self.ByteFlags(0xf0)
        self.assertEqual(dict(low=0, high=0xf),
                         flags.dictvalue())


class TestReadStruct(TestCase):

    def test_read_parse_error(self):

        class Foo(Struct):

            def attributes():
                yield INT16, 'a'
            attributes = staticmethod(attributes)

        stream = BytesIO()

        record = dict()
        context = dict(record=record)
        try:
            read_type(Foo, context, stream)
            assert False, 'ParseError expected'
        except ParseError as e:
            self.assertEqual(Foo, e.binevents[0][1]['type'])
            self.assertEqual('a', e.binevents[-1][1]['name'])
            self.assertEqual(0, e.offset)


class TestBSTR(TestCase):

    def test_read(self):
        f = BytesIO(b'\x03\x00' + u'가나다'.encode('utf-16le'))

        s = BSTR.read(f)
        self.assertEqual(u'가나다', s)

        pua = u'\ub098\ub78f\u302e\ub9d0\u302f\uebd4\ubbf8\u302e'
        pua_utf16le = pua.encode('utf-16le')
        if PY3:
            lengthbyte = bytes([len(pua)])
        else:
            lengthbyte = chr(len(pua))
        f = BytesIO(lengthbyte + b'\x00' + pua_utf16le)

        jamo = BSTR.read(f)
        expected = u'\ub098\ub78f\u302e\ub9d0\u302f\uebd4\ubbf8\u302e'
        self.assertEqual(expected, jamo)


class TestDecodeUTF16LEPUA(TestCase):

    def test_decode(self):
        expected = u'가나다'
        bytes = expected.encode('utf-16le')
        u = decode_utf16le_with_hypua(bytes)
        self.assertEqual(expected, u)
