#!/bin/sh

# exit if any statement returns non-true return value
set -e

# exit on uninitialized variable
set -u

error() {
    echo $*;
    exit 1
}

SAMPLES_DIR=$1
SAMPLE=$SAMPLES_DIR/sample-5017.hwp

[ -e "$SAMPLES_DIR" ] || error "$SAMPLES_DIR is not found"
[ -e "$SAMPLE" ] || error "$SAMPLE is not found"

echo '--------------------------------------'
echo '* Testing hwp5proc ---help / --version'
echo '--------------------------------------'
hwp5proc | head -n 1 | grep 'Do various'
hwp5proc --help | head -n 1 | grep 'Do various'
hwp5proc --help-commands | grep 'Available <command> values'
hwp5proc --version | grep 'Copyright' | grep 'mete0r'
hwp5proc --version | grep 'License' | grep 'GNU Affero GPL version 3 or any later'
hwp5proc --version | grep 'HWP Binary Specification 1.1' | grep 'Hancom Inc.'

echo '--------------------------'
echo '* Testing hwp5proc version'
echo '--------------------------'
hwp5proc version 2>&1 | head -n 3 | grep 'Usage:'
hwp5proc version --help | head -n 1 | grep 'Print HWP file format version'
hwp5proc version $SAMPLE | grep '5\.0\.1\.7'

echo '-------------------------'
echo '* Testing hwp5proc header'
echo '-------------------------'
hwp5proc header 2>&1 | head -n 3 | grep 'Usage:'
hwp5proc header --help | head -n 1 | grep 'Print HWP file header'
hwp5proc header $SAMPLE | grep 'HWP Document File'

echo '------------------------------'
echo '* Testing hwp5proc summaryinfo'
echo '------------------------------'
hwp5proc summaryinfo 2>&1 | head -n 3 | grep 'Usage:'
hwp5proc summaryinfo --help | head -n 1 | grep 'Print summary'
hwp5proc summaryinfo $SAMPLE | grep 'clsid: 9fa2'

echo '---------------------'
echo '* Testing hwp5proc ls'
echo '---------------------'
hwp5proc ls 2>&1 | head -n 3 | grep 'Usage:'
hwp5proc ls --help | head -n 1 | grep 'List streams'
hwp5proc ls $SAMPLE | grep 'PrvText'
hwp5proc ls --vstreams $SAMPLE | grep 'PrvText.utf8'

echo '----------------------'
echo '* Testing hwp5proc cat'
echo '----------------------'
hwp5proc cat 2>&1 | head -n 3 | grep 'Usage:'
hwp5proc cat --help | head -n 1 | grep 'Extract out the specified stream'
hwp5proc cat $SAMPLE BinData/BIN0002.jpg | file - | grep 'JPEG image data'
hwp5proc cat --vstreams $SAMPLE FileHeader.txt | grep 'HWP Document File'
hwp5proc cat $SAMPLE BodyText/Section0 | wc -c | grep '^4770$' || error 'Its output size should be 4770 bytes.'

echo '-------------------------'
echo '* Testing hwp5proc unpack'
echo '-------------------------'
hwp5proc unpack 2>&1 | head -n 3 | grep 'Usage:'
hwp5proc unpack --help | head -n 1 | grep 'Extract out streams'
rm -rf sample-5017 || echo
hwp5proc unpack $SAMPLE
ls sample-5017 | grep 'FileHeader'
hwp5proc unpack --vstreams $SAMPLE
ls sample-5017 | grep 'FileHeader.txt'
rm -rf sample-5017 || echo

echo '--------------------------'
echo '* Testing hwp5proc records'
echo '--------------------------'
hwp5proc records --help | head -n 1 | grep 'Print the record structure'
hwp5proc records $SAMPLE DocInfo | grep '"seqno": 66,'
hwp5proc records --simple $SAMPLE DocInfo --range=0-2 | grep '0001  HWPTAG_ID_MAPPINGS'
hwp5proc records --simple $SAMPLE DocInfo --range=0-2 | wc -l | grep '^2$'
hwp5proc records --raw $SAMPLE DocInfo --range=0-2 | hwp5proc records --simple | grep '0001  HWPTAG_ID_MAPPINGS'
hwp5proc records --json $SAMPLE DocInfo --range=1

echo '-------------------------'
echo '* Testing hwp5proc models'
echo '-------------------------'
hwp5proc models 2>&1 | head -n 3 | grep 'Usage:'
hwp5proc models --help | head -n 1 | grep 'Print parsed binary models'
hwp5proc models $SAMPLE DocInfo | grep '"Memo"'
hwp5proc models $SAMPLE docinfo | grep '"Memo"'
hwp5proc models $SAMPLE BodyText/Section0 | grep 'ShapePicture'
hwp5proc models $SAMPLE bodytext/0 | grep 'ShapePicture'
hwp5proc models $SAMPLE bodytext/0 --seqno=4 | grep 'seqno' | grep '4' | wc -l | grep '^1$'
hwp5proc models $SAMPLE bodytext/0 --seqno=4 | grep 'tagname' | grep 'HWPTAG_CTRL_HEADER'
hwp5proc models $SAMPLE bodytext/0 --seqno=4 | grep 'type' | grep 'SectionDef'
hwp5proc models --simple $SAMPLE bodytext/0 | grep '^0127 '
hwp5proc models --treegroup=1 --simple $SAMPLE bodytext/0 | wc -l | grep '^3$'
hwp5proc models $SAMPLE bodytext/0 --format='%(seqno)s %(level)s %(tagname)s\n' | wc -l | grep '^128$'
hwp5proc cat $SAMPLE BodyText/Section0 > sec0
cat sec0 | hwp5proc models --simple -V 5.0.1.7 | grep '0127 *ShapePicture'

echo '-----------------------'
echo '* Testing hwp5proc find'
echo '-----------------------'
hwp5proc find 2>&1 | head -n 3 | grep 'Usage:'
hwp5proc find --help | head -n 1 | grep 'Find record models'
hwp5proc find --model=Paragraph $SAMPLES_DIR/charshape.hwp $SAMPLES_DIR/parashape.hwp | wc -l | grep '^16$'
hwp5proc find --tag=HWPTAG_PARA_HEADER $SAMPLES_DIR/charshape.hwp $SAMPLES_DIR/parashape.hwp | wc -l | grep '^16$'
hwp5proc find --tag=66 $SAMPLES_DIR/charshape.hwp $SAMPLES_DIR/parashape.hwp | wc -l | grep '^16$'
hwp5proc find --incomplete $SAMPLES_DIR/shapeline.hwp | grep 'ShapeComponent'
hwp5proc find --incomplete --dump $SAMPLES_DIR/shapeline.hwp | grep 'STARTEVENT: ShapeComponent'
echo "$SAMPLE" | hwp5proc find --from-stdin | wc -l | grep '^195$'
hwp5proc find "$SAMPLE" 2> /dev/null | head -n 1 | awk '{print $1}' | grep "^$SAMPLE$"
hwp5proc find "$SAMPLE" 2> /dev/null | head -n 1 | awk '{print $2}' | grep "^DocInfo$"
hwp5proc find "$SAMPLE" 2> /dev/null | head -n 1 | awk '{print $3}' | grep "^0$"
hwp5proc find "$SAMPLE" 2> /dev/null | head -n 1 | awk '{print $4}' | grep "^HWPTAG_DOCUMENT_PROPERTIES$"
hwp5proc find "$SAMPLE" 2> /dev/null | head -n 1 | awk '{print $5}' | grep "^DocumentProperties$"
hwp5proc find --format='%(stream)s' "$SAMPLE" 2> /dev/null | head -n 1 | grep '^DocInfo$'
hwp5proc find --format='%(size)s' "$SAMPLE" 2> /dev/null | head -n 1 | grep '^26$'
hwp5proc find --format='%(payload)s' "$SAMPLE" 2> /dev/null | head -n 1 | head -c -1 | wc -c | grep '^26$'

echo '----------------------'
echo '* Testing hwp5proc xml'
echo '----------------------'
hwp5proc xml 2>&1 | head -n 3 | grep 'Usage:'
hwp5proc xml --help | head -n 1 | grep 'Transform'
hwp5proc xml $SAMPLE | xmllint --format - | grep 'BinDataEmbedding' | grep 'inline' | wc -l | grep '^0$'
hwp5proc xml --embedbin $SAMPLE | xmllint --format - | grep 'BinDataEmbedding' | grep 'inline' | wc -l | grep '^2$'
hwp5proc xml $SAMPLE | head -n 1 | grep '[<][?]xml' && echo ok
hwp5proc xml --no-xml-decl $SAMPLE | head -n 1 | grep -v '[<][?]xml' && echo ok

echo '-----------------'
echo '* Testing hwp5odt'
echo '-----------------'
hwp5odt 2>&1 | head -n 3 | grep 'Usage:'
hwp5odt --help | head -n 1 | grep 'HWPv5 to ODT converter'
hwp5odt $SAMPLE
unzip -l sample-5017.odt | grep 'styles.xml'
unzip -l sample-5017.odt | grep 'content.xml'
unzip -l sample-5017.odt | grep 'BIN0002.jpg'
unzip -p sample-5017.odt content.xml | xmllint --format - | grep 'office:binary-data' | wc -l | head -n 1 | grep '^0$'
hwp5odt --embed-image $SAMPLE
unzip -p sample-5017.odt content.xml | xmllint --format - | grep 'office:binary-data' | wc -l | head -n 1 | grep '^4$'
rm -f sample-5017.odt

echo '========='
echo 'COMPLETED'
echo '========='
