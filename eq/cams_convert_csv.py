#!/usr/bin/env python

import os, time, sys, requests, urllib, json
from datetime import datetime,timedelta

#from capital_gain import capital_gain
from xirr import xirr

# Import pandas as pd
import pandas as pd

def is_float(str):
	try :
	    float(str)
	    res = True
	except :
	    res = False
	return(res)

def process_csv(cname):
	data = []
	with open(cname) as clist:
		for line in clist:
			line = line.replace('d,', 'd')
			line = line.strip().replace('"', '')
			lines = line.split(',')
			if not is_float(lines[5]):
				continue
			elif float(lines[5]) > 0.0:
				invtype = "Investment"
			else:
				invtype = "Redemption"

			data.append([lines[3], lines[2], invtype,
				lines[6], lines[4], lines[7], lines[5]])
	return(data)

def fix_fund_names(csv_pd):
	filter = csv_pd['AMC Scheme Name'].str.contains("(?i)Segre")
	csv_pd = csv_pd[~filter]
	with open('CSV.map') as cmap:
		for line in cmap:
			l = line.strip().split(',')
			csv_pd_update = csv_pd.replace(to_replace ="(?i).*"+l[0]+".*", value = l[1], regex = True)
			csv_pd = csv_pd_update
	return(csv_pd)

if __name__ == "__main__":

	if len(sys.argv) != 3:
		print("Usage: cams_convert_csv.py <CSV exported from CAMS> <CSV file name to export>")
		sys.exit()

	columns = [ "Transaction Date", "AMC Scheme Name", "Transaction Type", "Price", "Units(Credits/Debits)", "Balance Units", "Amount(Credits/Debits)" ]
	csv_pd = pd.DataFrame(process_csv(sys.argv[1]), columns=columns)
	csv_pd = fix_fund_names(csv_pd)
	csv_pd['Transaction Date'] = pd.to_datetime(csv_pd['Transaction Date'])
	csv_pd = csv_pd.sort_values(by = 'Transaction Date')
	csv_pd['Transaction Date'] = csv_pd['Transaction Date'].dt.strftime("%d-%b-%Y")
	csv_pd.to_csv(sys.argv[2], index=False)
	print("Converted to %s" % sys.argv[2])
