#!/usr/bin/env python
import csv
import sys
import string
from copy import deepcopy
import difflib
import argparse

SCHEME_CSV="schemes.csv"

POSSIBLE_PLAN = ['growth', 'dividend']

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


def main(pdfcsv, all_match):
    my_tx = read_csv(pdfcsv)

    schmes = read_csv(SCHEME_CSV)

    POSSIBLE_VALES = [ d['scheme_name'].lower().replace('.', '')
                      for d in schmes ]

    # set of unique fund name from PDF which are slightly filtered as below
    unique_modified = set()
    # Set of unique fund names from PDF as it is
    unique_unmodified = set()

    for entry in my_tx:
        # Just to compare how we get results
        unique_unmodified.add(entry['Fund'])
        all_parts = entry['Fund'].split('-')
        #import pdb;pdb.set_trace()
        # doing some processing to the fundname from PDF
        fund = ' '.join(all_parts[1:])

        name = fund.strip() # remove trailing spaces
        name = name.lstrip(string.digits).strip() # remove trailing spaces
        # remove anything after '(' Mostly contains old scheme name or advisor
        name = name.partition('(')[0].strip()
        # remove multiple spaces
        name = ' '.join(name.split())
        unique_modified.add(name)

    print("$$ USING modified fund names from PDF Against scheme.csv")
    for mf in unique_modified:
        print(f' #### Finding match for {mf} ####')
        diff_ret = difflib.get_close_matches(mf.lower(), POSSIBLE_VALES)
        if not len(diff_ret):
            print('No match found')
            continue
        if all_match:
            print(f'\t {diff_ret}')
        else:
            print(f'\t {diff_ret[0]}')
    sys.exit()



if __name__ == '__main__':
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

