#!/usr/bin/env python3.7

from datetime import date, datetime, timedelta
import sys
sys.path.append('/Users/gowtham/Downloads/mfu/common')
from mf_util import fund_latest_nav


#tas = [(datetime.strptime("01-Jan-2017", "%d-%b-%Y").date(), -1000), (date(2018, 1, 1), -1000), (date(2019, 1, 1), -1000), (date(2020, 1, 1), 3641)]
tas = [(date(2020, 3, 6), -2500.0), (date(2020, 3, 9), 2421.1357113)]

def load_tx_from_file(fname, fund, sdate, edate):
	units = 0.0
	amt = 0.0
	s = None
	e = None
	fdict = {}
	with open(fname) as f:
		for lines in f.readlines():
			l = lines.split(',')
			if l[0] == "Transaction Date":
				continue
			if fund.lower() not in l[1].lower() and fund.lower() not in l[1].lower().replace(' ','_'):
				continue
			tdate = datetime.strptime(l[0], "%d-%b-%Y").date()
			if tdate < sdate or tdate > edate:
				continue
			if s == None or s > tdate:
				s = tdate
			if e == None or e < tdate:
				e = tdate
			fdict[l[1]] = "t"
			#print(l[4], l[6].strip(), s, e)
			units += float(l[4])
			amt += float(l[6])
		return units, fdict, amt, s, e

if __name__ == '__main__':
	if len(sys.argv) < 3:
		print("Usage: duration_inv.py <gt/mt> <fund string> <start date 01-01-2017> <end date 01-01-2017>")
		sys.exit()

	if sys.argv[1] == "gt":
		fname = "/Users/gowtham/Downloads/mfu/eq/VR.csv"
	elif sys.argv[1] == "mt":
		fname = "/Users/gowtham/Downloads/mfu/eq/VR_M.csv"
	else:
		print("Invalid file")
		sys.exit()

	fund = sys.argv[2]
	if len(sys.argv) >= 4:
		for fmt in ('%d-%b-%Y', '%d-%m-%Y'):
			try:
				sdate = datetime.strptime(sys.argv[3], fmt).date()
				break
			except ValueError:
				pass
	else:
		sdate = datetime.strptime("01-01-2007", "%d-%m-%Y").date()

	if len(sys.argv) == 5:
		for fmt in ('%d-%b-%Y', '%d-%m-%Y'):
			try:
				edate = datetime.strptime(sys.argv[4], fmt).date()
				break
			except ValueError:
				pass
	else:
		edate = date.today() + timedelta(days=1)
	#print(fname, fund, sdate, edate)

	print("Loading from %s..." % fname)
	units, f, amt, s, e = load_tx_from_file(fname, fund, sdate, edate)
	if not f:
		print("No fund found with that string!")
		sys.exit()
	elif len(f.keys()) > 1:
		#map(lambda st: str.replace(st, " ", "_"), f.keys())
		print("Please select one fund among", list(map(lambda st: str.replace(st, " ", "_"), f.keys())))
		sys.exit()
	val = fund_latest_nav(str(list(f.keys())[0]), False)
	print("Fund Name: " + str(list(f.keys())[0]))
	print("Start date: " + s.strftime("%d-%b-%Y"))
	print("End date: " + e.strftime("%d-%b-%Y"))
	print("Units: " + str(units))
	print("Amt: " + str(amt))
	print("Cur Value: " + str(round(float(val['nav']) * units, 2)) + " (" + str(val['date']) +")")
