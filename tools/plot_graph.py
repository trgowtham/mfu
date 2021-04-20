#!/usr/bin/env python3.7

from datetime import date, datetime
import sys, os, shutil, csv
import plotly
import plotly.express as px 
import pandas as pd 
import numpy as np 
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import plotly.io as pio
pio.orca.config.use_xvfb = True

def plot_fund_graph(fund_name):

	df_wide = pd.read_csv('%s/csv/%s.csv' % (sys.argv[1], fund_name))

	x_axis= list(df_wide['Date'])

	tot_inv = list(df_wide['Total Inv'])
	cur_val = list(df_wide['Current Value'])
	xirr = list(df_wide['XIRR'])

	fig = make_subplots(specs=[[{"secondary_y": True}]])

	fig.add_trace(
	    go.Scatter(x=x_axis, y=tot_inv, name="Total Inv"),
		    secondary_y=False,
	)

	fig.add_trace(
	    go.Scatter(x=x_axis, y=cur_val, name="Current Val"),
		    secondary_y=False,
	)

	fig.add_trace(
	    go.Scatter(x=x_axis, y=xirr, name="XIRR"),
		    secondary_y=True,
	)

	fig.update_layout(
	    title_text=fund_name.replace('_', ' ')
	)

	# Set y-axes titles
	fig.update_yaxes(title_text="<b>Amount</b>", secondary_y=False)
	fig.update_yaxes(title_text="<b>XIRR</b>", secondary_y=True)

	plotly.offline.plot(fig, filename='%s/html/%s.html' % (sys.argv[1], fund_name))
	if shutil.which("orca") is not None:
		fig.write_image('%s/jpeg/%s.jpeg' % (sys.argv[1], fund_name))
	else:
		print("Please install orca!")
	return

if len(sys.argv) < 2:
	print("Give directory name")
	sys.exit()

csv_dict = {}
for f in os.listdir('../report/'):
	if not f.endswith(".csv"):
		continue
	fname = f.replace('.csv','')
	with open('../report/%s' % f) as c:
		reader = csv.reader(c)
		data = list(reader)
		csv_dict[fname] = data

dates = list(csv_dict.keys())
dates.sort(key = lambda date: datetime.strptime(date, '%d-%m-%Y'))
#print(dates)
f_dict = {}
for d in dates:
	header = csv_dict[d][0]
	header.insert(2, 'Date')
	for i in csv_dict[d]:
		if i[0] == '':
			continue
		fname = i[1]
		test = i[2:]
		test.insert(0, d)
		fname = fname.replace('ABSL', 'Aditya_Birla_Sun_Life')
		fname = fname.replace('Franklin_Smaller_Companies', 'Franklin_Templeton_Franklin_India_Smaller_Companies')
		fname = fname.replace('Franklin_Liquid_Fund', 'Franklin_Templeton_India_Liquid_Fund')
		fname = fname.replace('Franklin_Focused_Equity_Fund', 'Franklin_Templeton_India_Focused_Equity_Fund')
		fname = fname.replace('Franklin_Ultra_Short_Bond', 'Franklin_Templeton_Franklin_India_Ultra_Short_Bond')
		fname = fname.replace('SBI_Healthcare_Opp_Fund', 'SBI_Healthcare_Opportunities_Fund')
		if fname not in f_dict.keys():
			f_dict[fname] = []
			f_dict[fname].append(header[2:])
		f_dict[fname].append(test)

#print(f_dict.keys())
for fund in f_dict.keys():
	with open("%s/csv/%s.csv" % (sys.argv[1], fund), "w") as f:
		writer = csv.writer(f)
		writer.writerows(f_dict[fund])
	print("Plotting graph for %s" % fund)
	plot_fund_graph(fund)
  
