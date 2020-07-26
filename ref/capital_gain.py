#!/usr/bin/env python

import os,time,datetime
import requests
import urllib, json
from tabulate import tabulate
import sys
import pdb

tas = [[datetime.date(2020, 4, 1), '2185.21870', '-1.14400', '-2500.00000'], [datetime.date(2020, 3, 31), '2175.71700', '-1.14900', '-2500.00000'], [datetime.date(2019, 12, 10), '2166.03800', '-1.15400', '-2500.00000'], [datetime.date(2019, 11, 11), '2156.86570', '-1.15900', '-2500.00000'], [datetime.date(2019, 10, 10), '2146.71840', '-1.16500', '-2500.00000'], [datetime.date(2019, 9, 11), '2136.98070', '-1.17000', '-2500.00000'], [datetime.date(2019, 8, 13), '2127.26550', '-1.17500', '-2500.00000'], [datetime.date(2019, 7, 10), '2114.28860', '-1.18200', '-2500.00000'], [datetime.date(2019, 6, 10), '2102.60710', '-1.18900', '-2500.00000'], [datetime.date(2019, 5, 10), '2089.67550', '-1.19600', '-2500.00000'], [datetime.date(2019, 4, 10), '2077.67170', '-1.20300', '-2500.00000'], [datetime.date(2019, 3, 11), '2064.01740', '-1.21100', '-2500.00000'], [datetime.date(2019, 2, 11), '2053.03210', '-1.21800', '-2500.00000'], [datetime.date(2019, 1, 10), '2040.28450', '-1.22500', '-2500.00000'], [datetime.date(2018, 12, 10), '2027.56330', '-1.23300', '-2500.00000'], [datetime.date(2018, 11, 12), '2015.66200', '-1.24000', '-2500.00000'], [datetime.date(2018, 10, 10), '2002.08810', '-1.24900', '-2500.00000'], [datetime.date(2018, 9, 10), '1990.09000', '-1.25600', '-2500.00000'], [datetime.date(2018, 8, 10), '1978.18000', '-1.26400', '-2500.00000'], [datetime.date(2018, 7, 10), '1966.03310', '-1.27200', '-2500.00000'], [datetime.date(2018, 6, 11), '1954.10390', '-1.27900', '-2500.00000'], [datetime.date(2018, 5, 10), '1942.03360', '-1.28700', '-2500.00000'], [datetime.date(2018, 4, 10), '1931.35260', '-1.29400', '-2500.00000'], [datetime.date(2018, 3, 12), '1918.77390', '-1.30300', '-2500.00000'], [datetime.date(2018, 2, 12), '1908.63520', '-1.31000', '-2500.00000'], [datetime.date(2018, 1, 10), '1897.28740', '-1.31800', '-2500.00000'], [datetime.date(2017, 12, 11), '1887.09480', '-1.32500', '-2500.00000'], [datetime.date(2017, 11, 10), '1876.93540', '-1.33200', '-2500.00000'], [datetime.date(2017, 10, 10), '1866.74740', '-1.33900', '-2500.00000'], [datetime.date(2017, 9, 11), '1857.10730', '-1.34600', '-2500.00000'], [datetime.date(2017, 8, 10), '1846.75780', '-1.35400', '-2500.00000'], [datetime.date(2017, 7, 10), '1836.48370', '-1.36100', '-2500.00000'], [datetime.date(2017, 6, 12), '1827.06930', '-1.36800', '-2500.00000'], [datetime.date(2017, 5, 11), '1816.57000', '-1.37600', '-2500.00000'], [datetime.date(2017, 4, 10), '1806.57070', '-1.38400', '-2500.00000'], [datetime.date(2017, 3, 20), '1799.06020', '55.58500', '100000.00000']]


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
		#print(i[0], (i[0] - datetime.timedelta(days = leap_year(i[0].year))).year)
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
		#print("For txn -> ", redtxn)
		#for i in range(sindex):
		while i <= sindex:
			#print(t_list)
			b_units = float(t_list[i][2])
			b_amt = float(t_list[i][3])
			b_price = float(t_list[i][1])
			s_units = abs(float(redtxn[2]))
			s_amt = abs(float(redtxn[3]))
			s_price = abs(float(redtxn[1]))
			#print("GT1", redtxn, i, b_units, s_units)
			if b_units > s_units:
				#print("Gain: ", (s_price - b_price) * s_units, " Units: ", (-s_units), " Amt: ", (-s_price))
				gain =  gain + (s_price - b_price) * s_units
				t_list[i][2] = str(b_units - s_units)
				t_list[i][3] = str((b_units - s_units) * float(t_list[i][1]))
				#print("In if")
				i = i + 1
				break
			else:
				#print("In else")
				s_txn = t_list.pop(i)
				gain = gain + (s_price - b_price) * b_units
				redtxn[2] = str(b_units - s_units)
				redtxn[3] = str((b_units - s_units) * float(redtxn[1]))
				#print("GT", gain, s_price, b_price, s_units)
		#print("Gain: ", redtxn[0], gain)
		gain_list.append([redtxn[0], gain])
		try:
			sindex = next(t_list.index(x) for x in t_list if float(x[3]) < 0)
		except:
			sindex = -1
	#print(t_list)
	#print(gain_list)
	print(gain_summary(gain_list))
	#print(sindex)


if __name__ == "__main__":
	tas.reverse()
	capital_gain(tas)

