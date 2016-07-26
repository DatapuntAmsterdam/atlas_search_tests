#!/usr/bin/env python
"""
Run the tests from the rob xsl/csv
"""

import argparse
import csv
import os

import requests

parser = argparse.ArgumentParser(description='Test rob osv tests')

parser.add_argument('url', help='URL to test')

args = parser.parse_args()

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


class TestCase(object):
    name = None
    sub_name = None
    query = None

    expected = None
    expected_type = None
    expected_position = None

    comparator_typeahead = None
    comparator_search = None
    is_known_failure = False

    documentation = None

    def __init__(self, row):
        """

        :type row: [str]
        """
        self.name = row[0]
        self.sub_name = row[1]
        self.query = row[2]
        self.expected = row[4]
        self.expected_type = CAT_LABEL_MAP[row[5]]
        self.comparator_typeahead = row[6]
        self.comparator_search = row[7]
        self.known_failure = (row[8] == "1")
        self.expected_position = row[9]
        self.documentation = row[11]

        self._check_comparator(self.comparator_search)
        self._check_comparator(self.comparator_typeahead)

    def _check_comparator(self, comparator):
        if comparator not in ['eq', 'not eq']:
            raise SyntaxError("Unknown comparator: <%s>" % (comparator,))

    def is_valid(self):
        return bool(self.query)

    def allows_empty_result_typeahead(self):
        return self.comparator_typeahead == 'not eq'

    def __str__(self):
        return "%10s %-5s" % (self.name, self.sub_name)


def load_tests():
    all_tests = []

    with open("robs_tests.csv") as csvfile:
        reader = csv.reader(csvfile)

        for i, row in enumerate(reader):
            if i < 6:
                # skip first 6 lines
                continue

            if not row[0] or row[0].startswith('#'):
                continue

            test = TestCase(row)
            all_tests.append(test)

    return all_tests


def is_valid(response, test):
    """
    """
    if response.status_code != 200:
        return False

    data = response.json()

    # if we do not want to match and we do not have
    # data the test was a success
    if not data:
        return test.allows_empty_result_typeahead()

    # find the result category we want to match
    search_result = None
    should_not_find = 'not eq' in test.comparator_typeahead

    for category in data:
        if category['label'] == test.expected_type:
            search_result = category['content']
            continue

    if not search_result:
        return should_not_find

    display_results = [r['_display'] for r in search_result]

    result_in_data = test.expected in "|".join(display_results)

    if should_not_find:
        return not result_in_data
    else:
        return result_in_data

def run_tests(all_tests):
    """

    :type all_tests: [TestCase]
    """
    failed = 0
    known_failures = 0

    for test in all_tests:

        if not test.is_valid():
            raise SyntaxError("Could not execute test %s" % (test,))

        payload = {
            'q': test.query,
            'format': 'json'
        }
        the_test_url = '{}/atlas/typeahead/'.format(args.url)

        response = requests.get(the_test_url, params=payload)

        is_ok = is_valid(response, test)

        if not is_ok and not test.known_failure:
            failed += 1
        elif test.known_failure:
            known_failures += 1

        status = "%s %-50s %-4s %-4s %-4s %-5s  %s" % (
            test,
            test.query,
            'OK' if is_ok else 'FAIL',
            'KNOWN' if test.known_failure else '',
            '' if is_ok else '!=' if 'not eq' in test.comparator_typeahead else "==",
            '' if is_ok else test.expected_type,
            '' if is_ok else test.expected
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
    run_tests(all_tests)


if __name__ == "__main__":
    main()
