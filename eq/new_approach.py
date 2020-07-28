#!/usr/bin/env python
import csv
import logging
import sys
import string
from copy import deepcopy
import difflib
import argparse
from itertools import groupby

SCHEME_CSV="schemes.csv"

def read_csv(csvfile):
    all_rows = []
    with open(csvfile, 'r') as f:
        csv_reader = csv.DictReader(f)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                all_rows.append(row)
    return all_rows

def group_mfapi_data(all_mfapi):
    '''
    Take a list of dictionaries where each dictionary represents a scheme.
    Convert it into a dictionary of dictionaries grouped by fund house.
    dict[fund_house] = [ list of schemes by fund house ]
    '''
    # First sort list by fund house name
    sorted_mfapi=sorted(all_mfapi, key=lambda x: x['fund_house'])

    # now groupthem into dictionary with key as fund house name and value as
    # list of schemes
    grouped_data = {k.lower() : list(v) for k,v in groupby(sorted_mfapi,
                                                   key=lambda x: x['fund_house'])}
    return grouped_data

def main(pdfcsv, all_match):
    my_tx = read_csv(pdfcsv)

    schmes = read_csv(SCHEME_CSV)

    # arrange data
    grouped_data = group_mfapi_data(schmes)


    '''
    # scheme name in mfuapi data is of this structure
    # DSP Tax Saver Fund - Regular Plan - Growth
    # SBI HEALTHCARE OPPORTUNITIES FUND - REGULAR PLAN -GROWTH
    # Canara Robeco Equity Taxsaver Fund - Regular Plan - Dividend
    # Canara Robeco Equity Taxsaver Fund - Regular Plan - Growth
    # Canara Robeco Equity Taxsaver Fund - Direct Plan - Growth Option
    # Canara Robeco Equity Taxsaver Fund - Direct Plan - Dividend Option
    UTI-Dividend Yield Fund.-Income
    UTI-Dividend Yield Fund.-Growth
    UTI-Dividend Yield Fund.-Growth-Direct
    UTI-Dividend Yield Fund.-Income-Direct
    Mirae Asset Emerging Bluechip Fund - Regular Plan - Dividend
Mirae Asset Emerging Bluechip Fund - Regular Plan - Growth Option
Mirae Asset Emerging Bluechip Fund - Direct Plan - Growth
Mirae Asset Emerging Bluechip Fund - Direct Plan - Dividend
    '''
    # { Namme of scheme } {Regular/Direct}  {Growth/Dividend/Bonus}

    # set of unique fund name from PDF which are slightly filtered as below
    unique_modified = set()

    for entry in my_tx:
        all_parts = entry['Fund'].split('-')
        # doing some processing to the fundname from PDF
        fund = ' '.join(all_parts[1:])
        name = fund.strip() # remove trailing spaces
        name = name.lstrip(string.digits).strip() # remove trailing spaces
        # remove anything after '(' Mostly contains old scheme name or advisor
        name = name.partition('(')[0].strip()
        # remove multiple spaces
        name = ' '.join(name.split())
        unique_modified.add(name)

    logging.debug(" USING modified fund names from PDF Against scheme.csv")
    for mf in unique_modified:
        print(f' {mf}')
        continue
        #print(f' #### Finding match for {mf} ####')
        # match fund house first
        search_list = []
        possible_fund_house = mf.split(' ')[0].lower()
        for house in grouped_data:
            if possible_fund_house in house:
                search_list = [ d['scheme_name'].lower().replace('.', '')
                               for d in grouped_data[house]]
                break
        diff_ret = difflib.get_close_matches(mf.lower(), search_list)
        if not len(diff_ret):
            print("NOT FOUND")
            continue
        if all_match:
            for ret in diff_ret:
                print(f'\t {ret}')
        else:
            print(f'\t {diff_ret[0]}')



if __name__ == '__main__':
    logging.basicConfig(filename='debug-match.log', filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--input-file",
                        help ="CSV file from PDF convertor",
                        action="store", required=True)

    parser.add_argument("-a", "--all_matches",
                        help ="show all possible match else give only 1 best",
                        action="store_true")
    args = parser.parse_args()
    all_match = args.all_matches
    pdfcsv = args.input_file
    main(pdfcsv, all_match)

