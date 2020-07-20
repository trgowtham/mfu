#!/usr/bin/env python3.7

import os,time
from datetime import datetime,timedelta
import requests
import urllib, json
from tabulate import tabulate
import sys
import pdb

from capital_gain import capital_gain
from xirr import xirr

txn_ignore = ['Transaction Date', 'Segregated Portfolio', '01-Jun-2018,HDFC Hybrid Equity Fund Direct G,Merger Investment,52.91400,5678.70200,5678.70200,300483.00000']

gt_funds = ['Aditya_Birla_Sun_Life_Equity_Advantage_Fund_Direct_G', 'Aditya_Birla_Sun_Life_Frontline_Equity_Direct_G',
'Axis_Long_Term_Equity_Direct_G', 'Franklin_Templeton_Franklin_India_Smaller_Companies_Direct_G',
'Franklin_Templeton_India_Focused_Equity_Fund_Direct_G', 'HDFC_Hybrid_Equity_Fund_Direct_G',
'Mirae_Asset_Emerging_Bluechip_Direct_G', 'Mirae_Asset_Hybrid_Equity_Fund_Direct_G',
'Mirae_Asset_Large_Cap_Fund_Direct_G', 'SBI_Bluechip_Direct_G',
'SBI_Healthcare_Opportunities_Fund_Direct_G', 'Indiabulls_Ultra_Short_Term_Direct_G',
'Aditya_Birla_Sun_Life_Corporate_Bond_Fund_Direct_G', 'HDFC_Short_Term_Debt_Fund_Direct_G',
'Franklin_Templeton_Franklin_India_Ultra_Short_Bond_Direct_G', 'Indiabulls_Liquid_Direct_G',
'Nippon_India_Low_Duration_Fund_Direct_G', 'Nippon_India_Gilt_Securities_Inst_Direct_G',
'Franklin_Templeton_India_Liquid_Fund_Direct_G', 'Mirae_Asset_Cash_Management_Direct_G',
'SBI_Magnum_Constant_Maturity_Fund_Direct_G', 'PPFAS_Long_Term_Equity_Fund_Direct_G',
'Axis_Banking_&_PSU_Debt_Fund_Direct_G', 'Axis_Liquid_Direct_G']

gt_file = "VR.csv"
mt_file = "VR_M.csv"

mt_funds = ['HDFC_Corporate_Bond_Fund_Direct_G', 'Nippon_India_Low_Duration_Fund_Direct_G', 'Franklin_Templeton_Franklin_India_Dynamic_Accrual_Fund_Direct_G', 'Franklin_Templeton_India_Liquid_Fund_Direct_G', 'Franklin_Templeton_Franklin_India_Low_Duration_Direct_G', 'ICICI_Prudential_All_Seasons_Bond_Fund_Direct_G', 'ICICI_Prudential_Equity_&_Debt_Fund_Direct_G', 'Indiabulls_Ultra_Short_Term_Direct_G', 'Invesco_India_Money_Market_Fund_Direct_G', 'L&T_Hybrid_Equity_Fund_Direct_G', 'L&T_India_Value_Direct_G', 'L&T_Money_Market_Fund_Direct_G']

fund_map = {}

with open("VR_map.csv") as v:
	for line in v.readlines():
		l = line.strip().split(',')
		fund_map[l[0]] = l[1]
#print(fund_map)

active_funds = []
report_dir = ""
txn = {}
txn_summary = {}
mf_api = {}
cur_data = {}
hist_data = {}
fund_cat = {}

def change_fund(l):
	s = l.split(',')
	#print(s[1])
	s[1] = fund_map[s[1].strip()]
	return ','.join(s)

def vr_txn_update(fname):

	if os.path.exists(fname):
		os.system("rm %s_bk" % fname)  
		os.system("cp %s tmp.csv" % fname)  
		os.system("cp %s %s_bk" % (fname, fname))  
	else:
		return

	t1 = open("tmp.csv", "a")
	v1 = open(fname)
	v1lines = v1.readlines()

	old_max_date = None

	for i in v1lines:
		ld = i.split(',')
		try:
			d = datetime.strptime(ld[0], "%d-%b-%Y").date()
		except:
			continue
		if old_max_date is None or d > old_max_date:
			old_max_date = d

	print(old_max_date)

	update_list = []

	with open("%s.2" % fname) as v2:
		for line in v2.readlines():
			if '\n' not in line:
				line = line + '\n'
			if 'Fund-Seg' in line:
				continue
			if True in [i in line for i in txn_ignore]:
				continue
			#if line not in v1lines:
			#	update_list.append(line)
			sl = line.split(',')
			try:
				d = datetime.strptime(sl[0], "%d-%b-%Y").date()
			except:
				continue
			if d > old_max_date:
				update_list.append(change_fund(line))
				t1.write(change_fund(line))
	print(''.join(update_list))

	v1.close()
	t1.close()

	#print('\n'.join(update_list))
	#print('\n'.join(sld.keys()))
	#print('\n'.join(old.keys()))
	#sys.exit()

	if os.path.exists("tmp.csv"):
		os.system("mv tmp.csv %s" % fname)

	if len(update_list) == 0:
		return

	report_name = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)) + report_dir + time.strftime("%d-%m-%Y", time.localtime()) + ".update"
	with open(report_name, "w") as r:
		r.write(''.join(update_list))
		print(''.join(update_list))
		r.write("\n")
		print("\n")

def vr_txn(fund_list, txn_file):
	os.system("rm -rf "+"data")
	os.mkdir("data")
	with open(txn_file) as pdf:
		for lines in pdf.readlines():
			fname = lines.strip().split(',')[1]
			fname = fname.strip().replace(' ', '_')
			if fund_list and fname not in fund_list:
				continue
			if fname not in txn.keys():
				txn[fname] = []
			txn[fname].append(lines)
			with open("data/%s" % fname, "a") as myfile:
			    myfile.write(lines)

def vr_summary():
	for fund in txn.keys():
		unit_bal = 0
		fund_bal = 0
		xirr = []
		freq = 0
		my_dates = []
		my_map = []

		if fund not in active_funds[0]:
			continue

		for ent in txn[fund]:
			line = ent.split(",")
			if line[0] == "Transaction Date":
				continue
			unit_bal += float(line[4])
			fund_bal += float(line[6])
			xirr.append([datetime.strptime(line[0], "%d-%b-%Y").date(), -float(line[6])])
			my_map.append((line[0], line[6]))

		my_map.sort(key=lambda date: datetime.strptime(date[0], "%d-%b-%Y"))
		my_map = [(datetime.strptime(x[0], "%d-%b-%Y").strftime("%b%y"), x[1]) for x in my_map]

		if fund not in txn_summary.keys():
			txn_summary[fund] = {}

		tot_val = float(cur_data[fund]["nav"]) * unit_bal
		xirr.append([datetime.strptime(cur_data[fund]["date"], "%d-%m-%Y").date(), tot_val])
		txn_summary[fund]["xirr"] = xirr
		txn_summary[fund]["tot_units"] = round(unit_bal, 4)
		txn_summary[fund]["tot_val"] = round(tot_val, 4)
		txn_summary[fund]["tot_inv"] = round(fund_bal, 4)
		txn_summary[fund]["duration"] = "%s-%s" % (my_map[0][0], my_map[-1][0])
		txn_summary[fund]["day_chg"] = (float(cur_data[fund]["nav"]) - float(hist_data[fund][0]["nav"])) * unit_bal
		txn_summary[fund]["week_chg"] = (float(cur_data[fund]["nav"]) - float(hist_data[fund][1]["nav"])) * unit_bal
		txn_summary[fund]["month_chg"] = (float(cur_data[fund]["nav"]) - float(hist_data[fund][2]["nav"])) * unit_bal
		if fund in get_funds("Equity") or fund in get_funds("Hybrid"):
			last_month = (datetime.strptime(my_map[-1][0], "%b%y") - timedelta(days=30)).strftime("%b%y")
			#print(fund, last_month)
			tmp = [item for item in my_map if item[0] == last_month ]
			txn_summary[fund]["frequency"] = "%s-%d" % (len(tmp), sum(float(j) for i, j in tmp))
		else:
			txn_summary[fund]["frequency"] = "NA"

def dump_json(fund, mf_data):
	if not os.path.exists("../json"):
		os.mkdir("../json")

	with open('../json/%s.json' % fund, 'w', encoding='utf-8') as f:
		json.dump(mf_data, f, ensure_ascii=False, indent=4)


def load_json(fname):
	with open(fname) as json_data:
		d = json.load(json_data)
		json_data.close()
	
	return d

def load_mf_api(fname, load_from_file):
	with open(fname) as mfeq:
		for lines in mfeq.readlines():
			fund = lines.split(',')[0]
			code = lines.split(',')[1]
			if fund not in active_funds[0]:
				continue
			if not load_from_file:
				mf_data = load_json("../json/%s.json" % fund)
			else:
				url = "https://api.mfapi.in/mf/" + code;
				r = requests.get(url)
				mf_data = r.json()
				dump_json(fund, mf_data)
			mf_api[fund] = mf_data
			cur_data[fund] = mf_data["data"][0]
			#print(mf_data["data"][0:10])
			hist_data[fund] = [mf_data["data"][1], mf_data["data"][5], mf_data["data"][20]]
			#print(hist_data[fund])
			scheme = mf_data["meta"]["scheme_category"]
			category = scheme.split(" Scheme - ")
			if category[0] not in fund_cat.keys():
				fund_cat[category[0]] = {}
			if category[1] not in fund_cat[category[0]].keys():
				fund_cat[category[0]][category[1]] = []
			fund_cat[category[0]][category[1]].append(fund)

def get_funds(ftype):
	flist = []
	for k in fund_cat[ftype].keys():
		flist.extend(fund_cat[ftype][k])
	return sorted(flist)


def shorten_fund(f):
	f = f.replace("Franklin_Templeton_Franklin", "Franklin_Templeton")
	f = f.replace("Aditya_Birla_Sun_Life", "ABSL")
	f = f.replace("Franklin_Templeton_India", "Franklin")
	f = f.replace("_Direct_G", "")
	return f

def fund_summary(i):
	tab = []
	head = ["Fund Name", "NAV date", "Total Units", "Total Inv", "Cur NAV", "Current Value", "P/L", "XIRR", "Duration", "Frequency"]
	f = i.replace("Franklin_Templeton_Franklin", "Franklin_Templeton")
	f = f.replace("Aditya_Birla_Sun_Life", "ABSL")
	f = f.replace("Franklin_Templeton_India", "Franklin")
	f = f.replace("_Direct_G", "")
	#print(i, txn_summary.keys())
	tab.append([f, cur_data[i]["date"], txn_summary[i]["tot_units"], txn_summary[i]["tot_inv"], cur_data[i]["nav"], txn_summary[i]["tot_val"], round(txn_summary[i]["tot_val"] - txn_summary[i]["tot_inv"], 4), round(100 * xirr(txn_summary[i]["xirr"]), 2), txn_summary[i]["duration"], txn_summary[i]["frequency"]])
	print(tabulate(tab, headers=head, numalign="left", tablefmt="grid", floatfmt='.8g'))

def pl_pct(x, y):
	return(str(round(x, 2)) + " (" + str(round(x*100/(y-x), 2)) +"%)")

def get_wt(fund, fund_val, e, h, d):
	pct = 0.0
	if fund in get_funds("Equity"):
		pct = round((fund_val/(e+h))*100, 1)
	elif fund in get_funds("Hybrid"):
		pct = round((fund_val/(e+h))*100, 1)
	elif fund in get_funds("Debt"):
		pct = round((fund_val/d)*100, 1)

	return str(round(fund_val, 2)) + " (" + str(pct) + "%)"

def print_summary(write_to_file):
	tab = []
	head = ["Fund Name", "NAV date", "Total Units", "Total Inv", "Cur NAV", "Current Value", "P/L", "XIRR", "Day P/L", "Duration", "Frequency"]
	tot_inv = 0
	tot_val = 0
	tot_xirr = []
	cat_xirr = []
	cat_inv = 0
	cat_tot = 0
	fund_hist = [0, 0, 0]
	cat_hist = [0, 0, 0]
	summary = {}
	nav_date = []

	eq_total = 0
	hy_total = 0
	db_total = 0
	inv_total = 0

	for f in get_funds("Equity"):
		if f in txn_summary.keys():
			eq_total += txn_summary[f]["tot_val"]

	for f in get_funds("Hybrid"):
		if f in txn_summary.keys():
			hy_total += txn_summary[f]["tot_val"]

	for f in get_funds("Debt"):
		if f in txn_summary.keys():
			db_total += txn_summary[f]["tot_val"]

	inv_total = eq_total + hy_total + db_total

	print("E", eq_total, "H", hy_total, "D", db_total, "T", inv_total);


	for i in txn_summary.keys():
		summary[i] = [shorten_fund(i), cur_data[i]["date"],
		txn_summary[i]["tot_units"], txn_summary[i]["tot_inv"],
		cur_data[i]["nav"], get_wt(i, txn_summary[i]["tot_val"], eq_total, hy_total, db_total), 
		round(txn_summary[i]["tot_val"] - txn_summary[i]["tot_inv"], 4),
		str(round(100 * xirr(txn_summary[i]["xirr"]), 2))+"%",
		pl_pct(txn_summary[i]["day_chg"], txn_summary[i]["tot_val"]),
		txn_summary[i]["duration"], txn_summary[i]["frequency"]]

		tot_xirr.extend(txn_summary[i]["xirr"])
	for t in "Equity", "Debt", "Hybrid":
		cat_inv = 0
		cat_val = 0
		cat_xirr = []
		cat_hist = [0, 0, 0]
		#tab.append([t])
		for i in get_funds(t):
			if i not in txn_summary.keys():
				continue
			if t == "Equity" or t == "Hybrid":
				nav_date.append(cur_data[i]["date"])
			tab.append(summary[i])
			tot_inv += txn_summary[i]["tot_inv"]
			tot_val += txn_summary[i]["tot_val"]
			cat_inv += txn_summary[i]["tot_inv"]
			cat_val += txn_summary[i]["tot_val"]
			cat_hist[0] += txn_summary[i]["day_chg"]
			cat_hist[1] += txn_summary[i]["week_chg"]
			cat_hist[2] += txn_summary[i]["month_chg"]
			cat_xirr.extend(txn_summary[i]["xirr"])
			#print(cat_xirr)

		tab.append([t + " ========>", "========", "========",
		round(cat_inv, 4), "========",
		str(round(cat_val, 2)) + " (" + str(round((cat_val/inv_total)*100, 1)) + "%)",
		round(cat_val - cat_inv, 4),
		str(round(100 * xirr(cat_xirr), 2)) + "%",
		"D: " + pl_pct(cat_hist[0], cat_val),
		"W: " + pl_pct(cat_hist[1], cat_val),
		"M: " + pl_pct(cat_hist[2], cat_val)])

		fund_hist[0] += cat_hist[0]
		fund_hist[1] += cat_hist[1]
		fund_hist[2] += cat_hist[2]
#	pdb.set_trace()
	#tab.append(["Total", cur_data[i]["date"], "", tot_inv, "", tot_val, tot_val - tot_inv, round(100 * xirr(tot_xirr), 2), round(fund_hist[0], 2), round(fund_hist[1], 2)])
	tab.append(
	["Total" + " ========>",
	cur_data[i]["date"], "",
	round(tot_inv, 2), "",
	round(tot_val, 2),
	round(tot_val - tot_inv, 2),
	str(round(100 * xirr(tot_xirr), 2))+"%",
	"D: " + pl_pct(fund_hist[0], tot_val),
	"W: " + pl_pct(fund_hist[1], tot_val),
	"M: " + pl_pct(fund_hist[2], tot_val)])
	print(tabulate(tab, headers=head, numalign="left", tablefmt="grid", floatfmt='.8g'))
	file_name = max(set(nav_date), key = nav_date.count)
	#print(file_name, nav_date)

	if write_to_file:
		report_name = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)) + report_dir + time.strftime(file_name, time.localtime())
		with open(report_name, "w") as r:
			r.write(tabulate(tab, headers=head, numalign="left", tablefmt="grid", floatfmt='.8g'))
			r.write("\n")


def list_txn(tlist):
	return [ [datetime.strptime(y[0], "%d-%b-%Y").date(), y[3], y[4], y[6]] for y in [x.rstrip().split(',') for x in tlist]]


def print_cap_summary(cap_data):
	cap_years = {}
	tab = []
	for f in cap_data:
		for y in cap_data[f]:
			if y not in cap_years.keys():
				cap_years[y] = []
			cap_years[y].append(f)
	cap_years = sorted(cap_years.keys())
	head = [ "" ] +  cap_years 
	tot = []
	tot.append("Total")
	c_sum = {}
	for f in cap_data:
		tmp = []
		tmp.append(shorten_fund(f))
		for y in cap_years:
			if y not in c_sum.keys():
				c_sum[y] = 0
			if y in cap_data[f].keys():
				tmp.append(round(cap_data[f][y], 3))
				c_sum[y] = c_sum[y] + float(cap_data[f][y])
			else:
				tmp.append("")
		tab.append(tmp)
	for y in cap_years:
		tot.append(round(c_sum[y], 3))
	tab.append(tot)
	print(tabulate(tab, headers=head, numalign="left", tablefmt="grid", floatfmt='.8g'))


def capital_summary(year):
	txn.clear()
	vr_txn(None, active_funds[1])
	cap_flist = []
	cap_data = {}
	for i in txn.keys():
		try:
			if any(float(x.rstrip().split(',')[6]) < 0 for x in txn[i]):
				cap_flist.append(i)
		except ValueError:
			pass
	for i in cap_flist:
		c_txn = list_txn(txn[i])
		c_txn.sort(key=lambda date: date[0])
		cap_data[i] = capital_gain(c_txn)
	print_cap_summary(cap_data)

if __name__ == "__main__":

	if len(sys.argv) >= 2:
		opt = sys.argv
	else:
		opt = sys.argv[0]

	if '-m' in sys.argv:
		active_funds = [mt_funds, mt_file]
		report_dir = "/mreport/"
	else:
		active_funds = [gt_funds, gt_file]
		report_dir = "/report/"

	if '-l' in sys.argv:
		for i,j in enumerate(gt_funds):
			    print("%s. %s"%(i+1,j))
		print("------------------")
		for i,j in enumerate(mt_funds):
			    print("%s. %s"%(i+1,j))
		sys.exit()

	if '-u' in sys.argv:
		vr_txn_update(active_funds[1])
		sys.exit()

	load_mf_api("MF-EQ.csv", '-f' in sys.argv)
	#print(hist_data)

	if '-xxx' in sys.argv:
		import pprint
		pprint.pprint(fund_cat)
		sys.exit()

	vr_txn(active_funds[0], active_funds[1])
	vr_summary()

	if '-n' in sys.argv:
		fund_in = int(sys.argv[sys.argv.index('-n') + 1]) - 1
		print("Result for " + active_funds[0][fund_in])
		fund_summary(active_funds[0][fund_in])
		sys.exit()

	if '-c' in sys.argv:
		capital_summary(2019)
		sys.exit()

	print_summary('-f' in sys.argv)
