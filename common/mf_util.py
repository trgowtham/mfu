#!/usr/bin/env python3.7

import os
import requests
import urllib, json

json_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)) + '/json'

def dump_json(fund, mf_data):
	if not os.path.exists(json_dir):
		os.mkdir(json_dir)

	with open('%s/%s.json' % (json_dir, fund), 'w', encoding='utf-8') as f:
		json.dump(mf_data, f, ensure_ascii=False, indent=4)


def load_json(fname):
	with open(fname) as json_data:
		d = json.load(json_data)
		json_data.close()
	
	return d

def fund_latest_nav(fname, load_from_file):
	fname = fname.strip().replace(' ', '_')

	if not load_from_file:
		mf_data = load_json("%s/%s.json" % (json_dir, fname))
	else:
		url = "https://api.mfapi.in/mf/" + code;
		r = requests.get(url)
		mf_data = r.json()
		dump_json(fname, mf_data)

	return(mf_data["data"][0])
