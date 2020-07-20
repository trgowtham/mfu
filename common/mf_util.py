#!/usr/bin/env python3.7

import os,time
from datetime import datetime,timedelta
import requests
import urllib, json
from tabulate import tabulate
import sys
import pdb


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

def fund_latest_nav(fname, load_from_file):
	fname = fname.strip().replace(' ', '_')

	if not load_from_file:
		mf_data = load_json("../json/%s.json" % fname)
	else:
		url = "https://api.mfapi.in/mf/" + code;
		r = requests.get(url)
		mf_data = r.json()
		dump_json(fname, mf_data)

	return(mf_data["data"][0])
