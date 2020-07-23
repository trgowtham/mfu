Steps to run this project for first time.
All command will be executed at the level of this file.

1. Install tox to manager virtualenv

	`pip3.6 install tox`
2. Create virtual env by running tox.This will use tox.ini.

   `python3.6 -m tox`
3. Activate virtual env

   `source .tox/py36/bin/activate`
   
4. Now run any command in this project.

To run the tool on sample data. Use '-f' for the first time. This will fetch the NAV data from mfapi.
Subsequent runs need not have '-f'

$ cd eq
$ ./pd.py -f

To run the tool using a PDF from CAMS, we need to make sure the fund mapping is proper. Make sure you follow the below steps

1. Update CSV.map to convert Fund name from CAMS format to a readable format. 

Eg:
HDFC Balanced Fund,HDFC Hybrid Equity Fund

<pattern>,<fund name>

.*HDFC Balanced Fund.* will be converted to 'HDFC Hybrid Equity Fund'

Run cams_conver_csv.py to make sure the resultant CSV is readable
$ ./cams_convert_csv.py
Usage: cams_convert_csv.py <CSV exported from CAMS> <CSV file name to export>

2. Update the MFAPI code. Visit https://www.mfapi.in and search for your fund

Eg: For 'Indiabulls Ultra Short Fund', the search result is https://api.mfapi.in/mf/119143. So add an entry to MF-EQ.csv as below

Indiabulls_Ultra_Short_Term,119143

Please note the '_' instead of spaces

3. Run mfu.sh with path to CAMS.pdf and password as arguments.

$ ./mfu.sh
Usage: mfu.sh <full path to PDF> password

If you want to skip few funds and interested only in few of them, create a file like GT.funds and add all valid funds to it.

Eg:

$ head GT.funds
Aditya_Birla_Sun_Life_Equity_Advantage_Fund
Aditya_Birla_Sun_Life_Frontline_Equity
Axis_Long_Term_Equity

Modify mfu.sh to send the file name to pd.py as FUND_FILE=GT.funds
