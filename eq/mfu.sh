#!/bin/bash

DIR="$( cd "$(dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PDIR="$(dirname "$DIR")"

if [ ! -d "$DIR" ]; then
	echo "$DIR not found!"
	exit 1
fi

if [ ! -d "$PDIR/casparser" ]; then
	echo "casparser not found!"
	exit 1
fi

usage()
{
	echo "mfu.sh"
	echo "     -p <Full path to CAMS pdf>"
	echo "     -z <Password to the pdf file>"
	echo "     -f Load latest NAV"
	echo "     -m <Fund file>"
	echo "     -r <Report directory> Default ../report"
	#echo "     -g Report only capital gain"
}

while getopts "hp:m:fr:cz:" OPTION; do
    case $OPTION in
    m)
        ENVI="$ENVI FUND_FILE=$OPTARG"
        ;;
    f)
        ARG="-f"
        ;;
    r)
        ENVI="$ENVI REPORT_DIR=$OPTARG"
        ;;
    c)
        CGAINS="-c"
		usage
        exit 1
        ;;
    z)
        PASS=$OPTARG
        ;;
    p)
        PDFFILE=$OPTARG
        ;;
	h)
		usage
		exit 1
		;;
    *)
        echo "Incorrect options provided"
		usage
        exit 1
        ;;
    esac
done

if [ -z "$PDFFILE" ] || [ -z "$PASS" ]; then
	usage
	exit 1
fi

if [ ! -f "$PDFFILE" ]; then
	echo "$PDFFILE not found"
	exit 1
fi

cd $DIR

rm -f CAMS.pdf CAMS.pdf.csv VR.csv

cp $PDFFILE CAMS.pdf

node ../casparser/casparser.js CAMS.pdf $PASS -csv

./cams_convert_csv.py CAMS.pdf.csv VR.csv

env $ENVI ./pd.py $ARG $CGAINS
