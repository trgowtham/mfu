#!/usr/bin/env python
import requests
import urllib.request
import time
import csv
import sys
import logging
import os
import pandas
from bs4 import BeautifulSoup


URLBASE = "https://api.mfapi.in/mf/"
SCHEME_CSV = "schemes.csv"

def get_mf_details(scheme_number):
    url = URLBASE + str(scheme_number)

    response = requests.get(url)
    if response.status_code != requests.codes.ok:
        return None
    page_json = response.json()

    # check for meta dictionary having scheme
    if len(page_json['meta']):
        return page_json['meta']
    # Got empty json
    return None


def write_csv(schemes):

    empty = True
    # check for duplicates
    if os.path.exists(SCHEME_CSV) and os.stat(SCHEME_CSV).st_size != 0:
        empty = False
    # write unique values
    if empty:
        pd = pandas.DataFrame(schemes)
        pd.to_csv(SCHEME_CSV, index=False)
    else:
        pd = pandas.read_csv(SCHEME_CSV)
        old_len = len(pd)

        pd = pd.append(schemes)

        pd = pd.drop_duplicates()
        new_len = len(pd)

        print(f'Found {new_len - old_len} new schemes')
        # update file
        pd.to_csv(SCHEME_CSV, index=False)

def main(args):
    start = int(args[0])
    end   = int(args[1])

    print(f'Iterating from {start}->{end}')

    schemes = []
    for i in range(start,end):
        scheme_details = get_mf_details(i)
        logging.debug('Processing %d entry', i)
        if scheme_details is not None:
            logging.debug('Got details for %s', scheme_details['scheme_name'])
            schemes.append(scheme_details)

    print(f'Found {len(schemes)} schemes')
    write_csv(schemes)

if __name__ == '__main__':
    logging.basicConfig(filename='api_scrap.log', filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s')
    main(sys.argv[1:])
