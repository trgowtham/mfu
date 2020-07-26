#!/usr/bin/env python
import csv
import sys
from copy import deepcopy

SCHEME_CSV="schemes.csv"
NEW_SCHEME_CSV="schemes-mod.csv"

POSSIBLE_PLAN = ['growth', 'dividend']

def read_csv():
    all_rows = []
    with open(SCHEME_CSV, 'r') as f:
        csv_reader = csv.DictReader(f)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                all_rows.append(row)
    return all_rows

def copy_and_update(row, name, plan):
    '''
    Argument: dictionary having scheme details
    Returns: Copy of dictionary with new key 'scheme_plan' and
    'scheme_name' provided as argument.
    Always save name and plan in lower case. Best so that we know when we
    are comparing.
    '''
    new_row = deepcopy(row)
    new_row['scheme_name'] = name.lower()
    new_row['scheme_plan'] = plan
    return new_row

def growth_or_dividend(plan):
    plan_list = plan.split()
    if len(plan_list) > 2:
        #import pdb;pdb.set_trace()
        print(plan_list)
    #if plan_list[0] not in POSSIBLE_PLAN:
        #import pdb;pdb.set_trace()

    return plan_list[0].lower()


def transform(all_rows):
    '''
    Idea is to break scheme name got from MFU api into
    scheme name and plan(Growth or Dividend)
    So in the end we will have a list of dicionary having 1 more column
    'scheme_plan'.
    Using this we can match scheme_name directly with the pdf scheme name

    Also updates name of schemes and plan in lower case
    '''

    updated_rows = [] # deepcopy(all_rows)
    count = 0
    for row in all_rows[:]:
        # Scheme name
        name = row['scheme_name']

        import pdb;pdb.set_trace()
        # Plan doesnt make sense in case of ETF
        if "ETF" in row['scheme_category']:
            new_row = copy_and_update(row, name, 'na')
            updated_rows.append(row)
            continue

        # try to split
        name_and_plan = name.rsplit('-', 1)

        if len(name_and_plan) >= 2:
            # we got 2 values in split values
            name = name_and_plan[0].strip()
            plan = name_and_plan[1].strip().lower()

            match = any(map(plan.__contains__, POSSIBLE_PLAN))
            if match:
                new_row = copy_and_update(row, name, growth_or_dividend(plan))
                updated_rows.append(new_row)
                continue
            else:
                print('Fallen in else')
            #    import pdb;pdb.set_trace()
        continue
        # we come here only when we were unable to split.
        # This is not perfect solution as we are not yet removing
        # "Growth" or "Dividend" from the scheme name.
        # TODO remove the Growth or Dividend from the scheme name
        if 'growth' in name.lower():
            new_row = deepcopy(row)
            new_row = copy_and_update(row, name, 'growth')

        if 'dividend' in name.lower():
            new_row = deepcopy(row)
            new_row = copy_and_update(row, name, 'growth')


            print("============ ")
            print(row['scheme_category'])
            print(f'{name} -> {name_and_plan}')
            print("============ ")
                # Dont count
            count += 1
        name_and_plan.append('Not Applicable')
        #print(f'\n {name} => \t\t{split_values[0].strip()} , {split_values[1].strip()}')

    print (f'Count = {count}')

def main():
    all_rows = read_csv()
    print(f'Fetched {len(all_rows)}')
    print(f'Fetched {all_rows[0]}')
    transform(all_rows)

if __name__ == '__main__':
    main()
