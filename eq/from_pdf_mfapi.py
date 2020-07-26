#!/usr/bin/env python
import csv
import sys
import string
from copy import deepcopy

SCHEME_CSV="schemes.csv"
PDF_CSV="nirmal.csv"
PDF_COLUMNS = []
SCHEME_COLUMNS = []

POSSIBLE_PLAN = ['growth', 'dividend']

def read_csv(csvfile):
    all_rows = []
    with open(csvfile, 'r') as f:
        csv_reader = csv.DictReader(f)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                all_rows.append(row)
    return all_rows

def clean_list(str_list):
    cleaned = [str.strip() for str in str_list]
    return cleaned


def main():
    my_tx = read_csv(PDF_CSV)
    PDF_COLUMNS = my_tx[0].keys()

    schmes = read_csv(SCHEME_CSV)
    SCHEME_COLUMNS = schmes[0].keys()

    # unique mf names in pdf
    # each key will have dict of different part of name
    # {
    #   ' FILL example
    # }
    #
    unique_mf = {}
    for entry in my_tx:

        long_scheme_name = entry['Fund']
        # remove all digits not required
        #remove_digits = str.maketrans('', '', string.digits)
        #long_scheme_name = long_scheme_name.translate(remove_digits).strip()
        #print(f' --- {long_scheme_name} ---- ')
        #print(clean_list(long_scheme_name.split('-')))
        #print('--------------')
        fund = entry['Fund'].split('-')[1]
        name = fund.strip() # remove trailing spaces
        name = fund.lstrip(string.digits).strip() # remove trailing spaces
        unique_mf[name] = clean_list(long_scheme_name.split('-'))

    print(unique_mf)

    # now search in mf file

    # first_filter => matching schemes names. we will get multiple entries
    # regular or Direct or growth or dividend
    first_filter= {mf: [] for mf in unique_mf}
    for mf in unique_mf:
        first_filter[mf] = [ d for d in schmes if mf in d['scheme_name'] ]

    for key in first_filter.keys():
        print(f'{key}')
        print(f'\t\t{first_filter[key]}')


    # Do a second pass to filter from selected mf schemes in first_filter
    # TODO
    # Idea is to search max matches (growth, regular  etc) from unique_mf
    # into matches found in first_filter


if __name__ == '__main__':
    main()

