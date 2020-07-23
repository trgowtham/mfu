#!/usr/bin/env python

import os, time, sys, requests, urllib, json
from datetime import datetime,timedelta

#from capital_gain import capital_gain
from xirr import xirr

# Import pandas as pd
import pandas as pd
#pd.options.display.float_format = '{:20,.2f}'.format
#pd.set_option('display.float_format', lambda x: '%.3f' % x)

index = ["Fund Name", "Fund Type", "NAV date", "Total Units", "Total Inv", "Cur NAV", "Current Value", "P/L", "XIRR", "Day P/L", "Week P/L", "Month P/L", "Duration", "Frequency", "Category Wt", "Portfolio Wt"]


def fund_pd_init(fname, tx_pd):
	fund_pd = pd.DataFrame(index=index)
	if fname is None or not os.path.isfile(fname):
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
		try:
			if load_from_file:
					load_mf_api(fund, mf_map[fund])
			nav = json.load(open('../json/%s.json' % fund))
		except:
				print("%s: cannot load JSON" % fund)
				sys.exit()
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
	tot_amt = [ 0, 0, 0]
	for fund in fund_pd.columns:
		x = fund_pd[fund]
		x['Total Units'] = tx_pd.loc[tx_pd['AMC_Scheme_Name'] == fund, 'Units(Credits/Debits)'].sum()
		x['Total Inv'] = -tx_pd.loc[tx_pd['AMC_Scheme_Name'] == fund, 'Amount(Credits/Debits)'].sum()
		x['Current Value'] = float(x['Cur NAV']) * float(x['Total Units'])
		x['P/L'] = x['Current Value'] - float(x['Total Inv'])

		old_nav = x['Day P/L']
		old_val = round((x['Cur NAV'] - old_nav) * x['Total Units'], 2)
		tot_amt[0] += old_val
		x['Day P/L'] = "%s(%s)" % (old_val, round((old_val/x['Current Value'])*100, 2))

		old_nav = x['Week P/L']
		old_val = round((x['Cur NAV'] - old_nav) * x['Total Units'], 2)
		tot_amt[1] += old_val
		x['Week P/L'] = "%s(%s)" % (old_val, round((old_val/x['Current Value'])*100, 2))

		old_nav = x['Month P/L']
		old_val = round((x['Cur NAV'] - old_nav) * x['Total Units'], 2)
		tot_amt[2] += old_val
		x['Month P/L'] = "%s(%s)" % (old_val, round((old_val/x['Current Value'])*100, 2))
	return tot_amt


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
	xirr_total = []
	for fund in fund_pd.columns:
		x = fund_pd[fund]
		f_data = tx_pd[tx_pd['AMC_Scheme_Name'] == fund]
		xirr_data = f_data[['Transaction_Date','Amount(Credits/Debits)']].values.tolist()
		xirr_data.append([x['NAV date'], x['Current Value']])
		xirr_total.extend(xirr_data)
		x['XIRR'] = xirr(xirr_data)*100
	fund_pd['Total'] = None
	fund_pd['Total']['XIRR'] = xirr(xirr_total)*100


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

		last_month = (datetime.now() - timedelta(days=30)).strftime("%b%y")
		f_data = f_data[f_data['Transaction_Date'] == last_month]
		if f_data['Amount(Credits/Debits)'].sum() == 0:
			x['Frequency'] = 'Inactive'
		else:
			x['Frequency'] = "%s(%s)" % (-f_data['Amount(Credits/Debits)'].sum(), len(f_data.index))


def populate_txn(txn_fname):
	txn = pd.read_csv(txn_fname)
	txn.columns = txn.columns.str.replace(" ", "_")
	txn['Transaction_Type']= txn['Transaction_Type'].str.replace(" ", "_")
	txn['AMC_Scheme_Name']= txn['AMC_Scheme_Name'].str.replace(" ", "_")
	txn['Transaction_Date'] = txn['Transaction_Date'].apply(lambda x: 
	                                    datetime.strptime(x,'%d-%b-%Y'))
	txn['Amount(Credits/Debits)'] = -txn['Amount(Credits/Debits)']
	return txn


def pd_add_total(fund_pd, tot_amt):
	fund_tr = fund_pd.transpose()
	x = fund_pd['Total']
	x['Total Inv'] = fund_tr['Total Inv'].sum()
	x['Current Value'] = fund_tr['Current Value'].sum()
	x['Day P/L'] = "%s(%s)" % (round(tot_amt[0], 2), round(tot_amt[0]/x['Current Value']*100*100, 2))
	x['Week P/L'] = "%s(%s)" % (round(tot_amt[1], 2), round(tot_amt[1]/x['Current Value']*100*100, 2))
	x['Month P/L'] = "%s(%s)" % (round(tot_amt[2], 2), round(tot_amt[2]/x['Current Value']*100*100, 2))
	# Not working
	#x['NAV date'] = fund_tr['NAV date'].value_counts().keys().to_pydatetime()


def make_pd_printable(fund_pd):
	fund_pd.columns = fund_pd.columns.str.replace("_Direct_G", "")
	fund_pd.columns = fund_pd.columns.str.replace("Franklin_Templeton_India", "Franklin")
	fund_pd.columns = fund_pd.columns.str.replace("Franklin_Templeton_Franklin_India", "Franklin")
	fund_pd.columns = fund_pd.columns.str.replace("Opportunities", "Opp")
	fund_pd.columns = fund_pd.columns.str.replace("Aditya_Birla_Sun_Life", "ABSL")
	fund_pd = fund_pd.transpose()
	fund_pd.drop(['Fund Name'], axis = 1, inplace=True) 
	fund_pd.drop(['Fund Type'], axis = 1, inplace=True) 
	fund_pd.drop(['Category Wt'], axis = 1, inplace=True) 
	fund_pd['NAV date'] = fund_pd['NAV date'].dt.strftime("%d-%m-%Y")
	fund_pd['XIRR'] = pd.to_numeric(fund_pd['XIRR'])
	fund_pd['Current Value'] = pd.to_numeric(fund_pd['Current Value'])
	fund_pd['XIRR'] = fund_pd['XIRR'].apply(lambda x: '%.2f' % x).values.tolist()
	return fund_pd


if __name__ == "__main__":

	vr_file = os.environ.get('VR_FILE')
	if vr_file is None:
		vr_file = "VR.csv"

	fund_file = os.environ.get('FUND_FILE')
	report_dir = os.environ.get('REPORT_DIR')
	if report_dir is None:
		report_dir = "/report/"

	if not os.path.isfile(vr_file):
		print(vr_file + " doesn't exist")
		sys.exit()

	tx_pd = populate_txn(vr_file)
	fund_pd = fund_pd_init(fund_file, tx_pd)
	load_nav(fund_pd, '-f' in sys.argv)
	tot_amt = calculate_amt(fund_pd, tx_pd)
	calculate_weight(fund_pd)
	calculate_dur_freq(fund_pd, tx_pd)
	calculate_xirr(fund_pd, tx_pd)
	pd_add_total(fund_pd, tot_amt)
	fund_pd = make_pd_printable(fund_pd)


	print(fund_pd.to_markdown())