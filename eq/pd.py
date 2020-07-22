#!/usr/bin/env python3.7

import os, time, sys, requests, urllib, json
from datetime import datetime,timedelta

#from capital_gain import capital_gain
from xirr import xirr

# Import pandas as pd
import pandas as pd

index = ["Fund Name", "Fund Type", "NAV date", "Total Units", "Total Inv", "Cur NAV", "Current Value", "P/L", "XIRR", "Day P/L", "Week P/L", "Month P/L", "Duration", "Frequency", "Category Wt", "Portfolio Wt"]


def fund_pd_init(fname, tx_pd):
	fund_pd = pd.DataFrame(index=index)
	if not os.path.isfile(fname):
		for line in tx_pd.AMC_Scheme_Name.tolist():
			fund_pd[line.strip()] = None
		return fund_pd

	with open(fname) as flist:
		for line in flist:
			if line.strip() in tx_pd.AMC_Scheme_Name.tolist():
				fund_pd[line.strip()] = None
	return fund_pd


def dump_json(fund, mf_data):
	if not os.path.exists("../json"):
		os.mkdir("../json")
	with open('../json/%s.json' % fund, 'w', encoding='utf-8') as f:
		json.dump(mf_data, f, ensure_ascii=False, indent=4)


def load_mf_api(fund, code):
	url = "https://api.mfapi.in/mf/" + code;
	r = requests.get(url)
	mf_data = r.json()
	dump_json(fund, mf_data)


def load_nav(fund_pd, load_from_file):
	mf_map = {}
	with open('MF-EQ.csv') as f:
		for line in f:
			x, y = line.strip().split(',')
			mf_map[x] = y
	for fund in fund_pd.columns:
		if load_from_file:
			load_mf_api(fund, mf_map[fund])
		nav = json.load(open('../json/%s.json' % fund))
		fmap = pd.DataFrame(nav['data'])
		x = fund_pd[fund]
		x['Fund Name'] = fund
		x['Fund Type'] = nav['meta']['scheme_category'].split(" Scheme - ")
		x['NAV date'] = fmap.loc[0]['date']
		x['NAV date'] = pd.to_datetime(x['NAV date'])
		x['Cur NAV'] = float(fmap.loc[0]['nav'])
		x['Day P/L'] = float(fmap.loc[1]['nav'])
		x['Week P/L'] = float(fmap.loc[5]['nav'])
		x['Month P/L'] = float(fmap.loc[20]['nav'])


def calculate_amt(fund_pd, tx_pd):
	for fund in fund_pd.columns:
		x = fund_pd[fund]
		x['Total Units'] = tx_pd.loc[tx_pd['AMC_Scheme_Name'] == fund, 'Units(Credits/Debits)'].sum()
		x['Total Inv'] = -tx_pd.loc[tx_pd['AMC_Scheme_Name'] == fund, 'Amount(Credits/Debits)'].sum()
		x['Current Value'] = float(x['Cur NAV']) * float(x['Total Units'])
		x['P/L'] = x['Current Value'] - float(x['Total Inv'])

		old_nav = x['Day P/L']
		old_val = round((x['Cur NAV'] - old_nav) * x['Total Units'], 2)
		x['Day P/L'] = "%s(%s)" % (old_val, round((old_val/x['Current Value'])*100, 2))

		old_nav = x['Week P/L']
		old_val = round((x['Cur NAV'] - old_nav) * x['Total Units'], 2)
		x['Week P/L'] = "%s(%s)" % (old_val, round((old_val/x['Current Value'])*100, 2))

		old_nav = x['Month P/L']
		old_val = round((x['Cur NAV'] - old_nav) * x['Total Units'], 2)
		x['Month P/L'] = "%s(%s)" % (old_val, round((old_val/x['Current Value'])*100, 2))


def calculate_weight(fund_pd):

	fund_tr = fund_pd.transpose()
	fund_tr['Fund Type'] = [l[0] for l in fund_tr['Fund Type']]

	eq_total = fund_tr.loc[fund_tr['Fund Type'] == "Equity", 'Current Value'].sum()
	debt_total = fund_tr.loc[fund_tr['Fund Type'] == "Debt", 'Current Value'].sum()
	hybrid_total = fund_tr.loc[fund_tr['Fund Type'] == "Hybrid", 'Current Value'].sum()
	portfolio_total = eq_total + debt_total + hybrid_total

	for fund in fund_pd.columns:
		x = fund_pd[fund]
		x_type = x.loc[['Fund Type']][0][0]
		if x_type == 'Equity' or x_type == 'Hybrid':
			x['Category Wt'] = (x['Current Value']/(eq_total+hybrid_total))*100
		else:
			x['Category Wt'] = (x['Current Value']/debt_total)*100
		x['Portfolio Wt'] = (x['Current Value']/portfolio_total)*100


def calculate_xirr(fund_pd, tx_pd):
	for fund in fund_pd.columns:
		x = fund_pd[fund]
		xirr_data = []
		f_data = tx_pd[tx_pd['AMC_Scheme_Name'] == fund]
		xirr_data = f_data[['Transaction_Date','Amount(Credits/Debits)']].values.tolist()
		xirr_data.append([x['NAV date'], x['Current Value']])
		x['XIRR'] = xirr(xirr_data)*100


def calculate_dur_freq(fund_pd, tx_pd):
	for fund in fund_pd.columns:
		x = fund_pd[fund]
		f_data = tx_pd[tx_pd['AMC_Scheme_Name'] == fund]
		f_data = f_data.sort_values(by = 'Transaction_Date')
		f_data = f_data.reset_index(drop=True)
		f_data['Transaction_Date'] = f_data['Transaction_Date'].dt.strftime("%b%y")
		sdate = f_data.iloc[0]['Transaction_Date']
		edate = f_data.iloc[-1]['Transaction_Date']
		x['Duration'] = sdate + '-' + edate

		last_month = (datetime.strptime(edate, "%b%y") - timedelta(days=30)).strftime("%b%y")
		f_data = f_data[f_data['Transaction_Date'] == last_month]
		x['Frequency'] = "%s(%s)" % (-f_data['Amount(Credits/Debits)'].sum(), len(f_data.index))


def populate_txn(txn_fname):
	txn = pd.read_csv(txn_fname)
	txn.columns = txn.columns.str.replace(" ", "_")
	txn['Transaction_Type']= txn['Transaction_Type'].str.replace(" ", "_")
	txn['AMC_Scheme_Name']= txn['AMC_Scheme_Name'].str.replace(" ", "_")
	#txn['Transaction_Date'] = pd.to_datetime(txn['Transaction_Date'])
	txn['Transaction_Date'] = txn['Transaction_Date'].apply(lambda x: 
	                                    datetime.strptime(x,'%d-%b-%Y'))
	txn['Amount(Credits/Debits)'] = -txn['Amount(Credits/Debits)']
	return txn


if __name__ == "__main__":

	# Start cmdline options

	if '-m' in sys.argv:
		vr_file = "VR_M.csv"
		fund_file = "MT.funds"
		report_dir = "/mreport/"
	else:
		vr_file = "VR.csv"
		fund_file = "GT.funds"
		report_dir = "/report/"

	if '-u' in sys.argv:
		vr_txn_update(active_funds[1])
		sys.exit()
	# End cmdline options


	tx_pd = populate_txn(vr_file)
	fund_pd = fund_pd_init(fund_file, tx_pd)
	load_nav(fund_pd, '-f' in sys.argv)
	calculate_amt(fund_pd, tx_pd)
	calculate_weight(fund_pd)
	calculate_xirr(fund_pd, tx_pd)
	calculate_dur_freq(fund_pd, tx_pd)

	print(fund_pd)
	print(fund_pd.info())
