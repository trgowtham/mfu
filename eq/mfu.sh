#!/bin/bash

if [ $# -lt 2 ]; then
	echo "Usage: mfu.sh <full path to PDF> password"
	exit 1
fi

if [ ! -f "$1" ]; then
	echo "$1 not found"
	exit 1
fi

if [ ! -d /Users/gowtham/Downloads/mfu/eq ]; then
	echo "/Users/gowtham/Downloads/mfu/eq not found!"
	exit 1
fi

if [ ! -d /Users/gowtham/Downloads/mfu/casparser ]; then
	echo "caspasrser not found!"
	exit 1
fi

OPT="$3 $4"

cd /Users/gowtham/Downloads/mfu/eq

rm -f CAMS.pdf CAMS.pdf.csv VR.csv

cp $1 CAMS.pdf

node ../casparser/casparser.js CAMS.pdf $2 -csv

if [ "$3" = '-m' ] || [ "$4" = '-m' ]; then
	ARG="FUND_FILE=MT.funds"
else
	ARG="FUND_FILE=GT.funds"
fi

./cams_convert_csv.py CAMS.pdf.csv VR.csv

env $ARG ./pd.py $OPT
