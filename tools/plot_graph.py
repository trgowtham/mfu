#!/usr/bin/env python3.7

from datetime import date, datetime
import sys, os
import matplotlib.pyplot as plt 
import matplotlib
import csv

def plot_fund_graph(csv_dict, fund_name):
	dates = list(csv_dict.keys())
	dates_iter = list(csv_dict.keys())
	dates.sort(key = lambda date: datetime.strptime(date, '%d-%m-%Y'))
	xirr = []
	inv = []
	cur = []
	nav = []
	for k in dates_iter:
		try:
			i = [item[0] for item in csv_dict[k]].index(fund_name)
		except:
			print("Skipping %s for %s" % (k, fund_name));
			dates.remove(k)
			continue
		inv.append(round(float(csv_dict[k][i][6]), 2))
		cur.append(round(float(csv_dict[k][i][8]), 2))
		xirr.append(round(float(csv_dict[k][i][10]), 2))
		try:
			nav.append(round(float(csv_dict[k][i][7]), 2))
		except:
			continue

	fig, ax1 = plt.subplots()

	ax1.set_xlabel('Date')
	ax1.plot(dates, inv, label = "Inv", color='tab:red') 
	ax1.plot(dates, cur, label = "Cur", color='tab:orange') 

	ax2 = ax1.twinx()  
	ax2.plot(dates, xirr, label = "XIRR", color='tab:green') 

#	if len(nav) > 0:
#		ax3 = ax1.twinx()  
#		ax3.plot(dates, nav, label = "NAV", color='tab:cyan') 
#		ax3.legend()

	ax1.legend()
	ax2.legend()

	fig.tight_layout(rect=(0,0,1,0.9))
	fig.autofmt_xdate()
	plt.title(fund_name) 
	plt.savefig('../jpeg/%s.jpeg' % fund_name, bbox_inches='tight')
	plt.cla()
	plt.close(fig)

csv_dict = {}
for f in os.listdir('../report/'):
	if not f.endswith(".csv"):
		continue
	fname = f.replace('.csv','')
	with open('../report/%s' % f) as c:
		reader = csv.reader(c)
		data = list(reader)
		csv_dict[fname] = data

#plot_fund_graph(csv_dict, "Mirae_Asset_Hybrid_Equity_Fund")
#sys.exit()

for f in [item[0] for item in csv_dict[fname]]:
	if f is not '':
		print("Plotting %s" % f)
		plot_fund_graph(csv_dict, f)
  
