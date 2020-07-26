#!/usr/bin/env python

import datetime
import pandas as pd
from tabulate import tabulate

def leap_year(year):
	if (year % 4) == 0:
		if (year % 100) == 0:
			if (year % 400) == 0:
				return 91
			else:
				return 90
		else:
			return 91
	else:
		return 90


def gain_summary(gain_list):
	gain_sum = {}
	for i in gain_list:
		year =  (i[0] - datetime.timedelta(days = leap_year(i[0].year))).year
		if year not in gain_sum.keys():
			gain_sum[year] = 0
		gain_sum[year] = gain_sum[year] + float(i[1])

	return gain_sum


def capital_gain(t_list):
	gain_list = []
	try:
		sindex = next(t_list.index(x) for x in t_list if float(x[3]) < 0)
	except:
		sindex = 0
	while sindex > 0:
		redtxn = t_list.pop(sindex)
		gain = 0
		i = 0
		while i <= sindex:
			if len(t_list) == 0:
				break
			b_units = float(t_list[i][2])
			b_amt = float(t_list[i][3])
			b_price = float(t_list[i][1])
			s_units = abs(float(redtxn[2]))
			s_amt = abs(float(redtxn[3]))
			s_price = abs(float(redtxn[1]))
			if b_units >= s_units:
				gain =  gain + (s_price - b_price) * s_units
				t_list[i][2] = str(b_units - s_units)
				t_list[i][3] = str((b_units - s_units) * float(t_list[i][1]))
				i = i + 1
				break
			else:
				s_txn = t_list.pop(i)
				gain = gain + (s_price - b_price) * b_units
				redtxn[2] = str(b_units - s_units)
				redtxn[3] = str((b_units - s_units) * float(redtxn[1]))

		gain_list.append([redtxn[0], gain])
		try:
			sindex = next(t_list.index(x) for x in t_list if float(x[3]) < 0)
		except:
			sindex = -1

	return gain_summary(gain_list)


def capital_summary(tx_pd):

	# List of all funds that have a Redemption
	flist = list(set(tx_pd.loc[tx_pd['Amount(Credits/Debits)'] > 0, 'AMC_Scheme_Name'].values.tolist()))
	cap_dict = {}

	for f in flist:
		# Send filtered list of txns to capital_gain() for calculating gain
		c_txn = tx_pd.loc[tx_pd['AMC_Scheme_Name'] == f].values.tolist()
		for c in c_txn:
			c[0] = c[0].to_pydatetime().date()
			del(c[1])
			del(c[1])
			del(c[3])
			c[3] = -c[3]
		c_txn.sort(key=lambda date: date[0])
		cap_data = capital_gain(c_txn)
		cap_dict[f] = cap_data
	
	# Create DataFrame and sort the data
	cap_pd = pd.DataFrame.from_dict(cap_dict, orient='index')
	cap_pd.sort_index(inplace=True)
	years = cap_pd.columns.tolist()
	years.sort()
	cap_pd = cap_pd[years]
	# Add Total row
	cap_pd = cap_pd.append(cap_pd.sum().rename('Total'))

	print(tabulate(cap_pd, headers=cap_pd.columns, numalign="left", tablefmt="grid", floatfmt='.8g'))
