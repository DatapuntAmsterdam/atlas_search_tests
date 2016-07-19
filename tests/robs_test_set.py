
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

    with open("Zoekfunctionaliteiten_tests.csv") as csvfile:

        testreader = csv.reader(csvfile)

        # 0.Name,
        # 1.Subname,
        # 2.q,
        # 3.(hulpkolom),
        # 4.Resultaat,
        # 5.Type (van resultaat),
        # 6.comparator,
        # 7.comparator,,,
        # 8.KNOWN FAILURE
        # 9.Positie resultaat (niet gebruikt)
        # 11.Argumentatie (van de test)

        for i, row in enumerate(testreader):
            if i < 6:
                # skip first 6 lines
                continue

            if row[0].startswith('#'):
                continue

            test = dict(
                name=row[0],
                subname=row[1],
                query=row[2],
                result=row[4],
                type=row[5],
                comparator=row[6],
                known_failure=row[8],
                doc=row[9],
            )
            all_tests.append(test)

    return all_tests


def do_request(url):
    print(url)


CAT_LABEL_MAP = {
    'weg': 'Straatnamen',
    'vbo': 'Adres',
    'meetbout': 'Meetbouten',
    'bouwblok': 'Bouwblok',
    'stadsdeel': 'Stadsdeel',
    'gebied': 'Gebieden',
    'buurt': 'Buurt',
    'buurtcombinatie': 'Buurtcombinatie',
    'grootstedelijk': 'Grootstedelijk',
    'kad. subject': 'Kadastrale subjecten',
    'kad. object': 'Kadastrale objecten'

}


def is_valid(response, test):
    """
    """
    success = True
    fail = False

    if response.status_code != 200:
        return False

    data = response.json()

    # if we do not want to macht and we do not have
    # data the test was a success
    if not data:
        if 'not eq' in test['comparator']:
            return True
        return False

    # find the result category we want to match
    wanted_data = test['result']
    wanted_label = CAT_LABEL_MAP[test['type']]
    search_result = None
    should_not_find = 'not eq' in test['comparator']

    result_in_data = False

    for category in data:
        if category['label'] == wanted_label:
            search_result = category
            continue

    # print(category['label'], wanted_label)

    if search_result:
        result_in_data = wanted_data in str(search_result)

    if should_not_find:
        # we did not even find the category
        return success

    if should_not_find:
        if not result_in_data:
            return fail

    # did we find what we are looking for?
    if result_in_data:
        return True


def run_tests(_, all_tests):

    failed = 0
    known_failures = 0

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

        known_failure = test['known_failure']
        is_ok = is_valid(response, test)

        if not is_ok and not known_failure:
            failed += 1
        elif known_failure:
            known_failures += 1

        status = "%10s %-5s %-50s %-4s %-4s %-4s %-5s  %s" % (
            test['name'], test['subname'],
            test['query'],
            'OK' if is_ok else 'FAIL',
            'KNOWN' if known_failure else '',
            '' if is_ok else '!=' if 'not eq' in test['comparator'] else "==",
            '' if is_ok else test['type'],
            '' if is_ok else test['result']
        )
        print(status)

    if failed:
        print('Failed: %s of %s' % (failed, len(all_tests)))
        os.sys.exit(9)
    else:
        print('Known failures: %s of %s' % (known_failures, len(all_tests)))
        print('SUCCESS')
        os.sys.exit(0)


def main():
    all_tests = load_tests()

    test_urls = [
        'http://127.0.0.1:8000',
    ]

    for url in test_urls:
        run_tests(url, all_tests)


if __name__ == "__main__":
    main()
