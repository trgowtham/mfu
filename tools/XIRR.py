#!/usr/bin/env python

'''
A single function that calculates IRR using Newton's Method
'''
import sys
from datetime import date, datetime

date_field = 0
amt_field = 1

def xirr(transactions):

    '''
    Calculates the Internal Rate of Return (IRR) for an irregular series of cash flows (XIRR)
    Takes a list of tuples [(date,cash-flow),(date,cash-flow),...]
    Returns a rate of return as a percentage
    '''

    years = [(ta[0] - transactions[0][0]).days / 365. for ta in transactions]
    residual = 1.0
    step = 0.05
    guess = 0.05
    epsilon = 0.0001
    limit = 10000
    while abs(residual) > epsilon and limit > 0:
        limit -= 1
        residual = 0.0
        for i, trans in enumerate(transactions):
            if guess == 0:
                print(pow(guess, years[i]), guess, years[i])
                continue
            residual += trans[1] / pow(guess, years[i])
        if abs(residual) > epsilon:
            if residual > 0:
                guess += step
            else:
                guess -= step
                step /= 2.0
    return guess - 1

#tas = [(datetime.strptime("01-Jan-2017", "%d-%b-%Y").date(), -1000), (date(2018, 1, 1), -1000), (date(2019, 1, 1), -1000), (date(2020, 1, 1), 3641)]
tas = [(date(2020, 3, 6), -2500.0), (date(2020, 3, 9), 2421.1357113)]

def load_tas_from_file(fname):
	tas = []
	with open(fname) as f:
		for lines in f.readlines():
			l = lines.split(',')
			tas.append((datetime.strptime(l[date_field], "%d-%m-%Y").date(), -float(l[amt_field])))
		return tas

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("XIRR for test data = {:.2%}".format(xirr(tas)))
		sys.exit()

	fname = sys.argv[1]
	print("Loading from %s..." % fname)
	tas = load_tas_from_file(fname)
	print("XIRR for file data = {:.2%}".format(xirr(tas)))
