
"""
Run the tests from the rob xsl/csv
"""

import requests

import argparse
import csv
import os

parser = argparse.ArgumentParser(description='Test rob osv tests')

parser.add_argument('url', help='URL to test')

args = parser.parse_args()

print('Testing on: %s' % args.url)


def load_tests():

    all_tests = []

    with open('rob_tests.csv') as csvfile:

        testreader = csv.reader(csvfile)

        # 0.Name,
        # 1.Subname,
        # 2.q,
        # 3.(hulpkolom),
        # 4.Resultaat,
        # 5.Type (van resultaat),
        # 6.comparator,
        # 7.comparator,,,
        # 8.Argumentatie (uit de specificatie)

        for i, row in enumerate(testreader):
            if i < 6:
                continue

            test = dict(
                name=row[0],
                subname=row[1],
                query=row[2],
                result=row[4],
                type=row[5],
                comparator=row[6],
                doc=row[8],
            )
            all_tests.append(test)

    return all_tests


def do_request(url):
    print(url)


def is_valid(response, test):
    """
    """
    if response.status_code != 200:
        return False

    data = response.json()

    if not data:
        if 'not eq' in test['comparator']:
            return True
        return False

    wanted_data = test['result']

    in_data = wanted_data in str(data[0])

    if 'not eq' in test['comparator']:
        if in_data:
            return False
        else:
            return True

    if in_data:
        return True


def run_tests(_, all_tests):

    failed = 0

    for test in all_tests:

        if not test['query']:
            print
            continue

        payload = {
            'q': test['query'],
            'format': 'json'
        }
        the_test_url = '{}/atlas/typeahead/'.format(args.url)

        response = requests.get(the_test_url, params=payload)

        is_ok = is_valid(response, test)

        if not is_ok:
            failed += 1

        status = "%10s %-5s %-50s %-4s %-4s   %s" % (
            test['name'], test['subname'],
            test['query'],
            '' if is_ok else '!=' if 'not eq' in test['comparator'] else "==",
            'OK' if is_ok else 'FAIL',
            '' if is_ok else test['result']
        )
        print(status)

    if failed:
        print('Failed: %s' % failed)
        os.sys.exit(9)
    else:
        print('SUCCESS')


def main():
    all_tests = load_tests()

    test_urls = [
        'http://127.0.0.1:8000',
    ]

    for url in test_urls:
        run_tests(url, all_tests)


if __name__ == "__main__":
    main()
