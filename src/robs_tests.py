#!/usr/bin/env python
"""
Run the tests from the collected by rob mayers xsl/csv

Only run's against typeahead.
"""

import time
import jwt

import authorization_levels

import logging
import argparse
import csv
import os
import random
import requests
import string

from authorization_django import jwks
from urllib.parse import urlparse, parse_qsl

parser = argparse.ArgumentParser(description='Test rob osv tests')
parser.add_argument('url', help='URL to test')
args = parser.parse_args()


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('searchtests')
log.setLevel(logging.DEBUG)
logging.getLogger('requests').setLevel(logging.ERROR)


CATEGORY_LABEL_MAP = {
    'vestiging': 'Vestigingen',
    'mac': 'Maatschappelijke activiteiten',
    'weg': 'Straatnamen',
    'vbo': 'Adres',
    'ligplaats': 'Adres',
    'standplaats': 'Adres',
    'meetbout': 'Meetbouten',
    'bouwblok': 'Bouwblok',
    'stadsdeel': 'Stadsdeel',
    'gebied': 'Gebieden',
    'buurt': 'Buurt',
    'buurtcombinatie': 'Buurtcombinatie',
    'grootstedelijk': 'Grootstedelijk',
    'kad. subject': 'Kadastrale subjecten',
    'kad. subject.persoon': 'Kadastrale subjecten',
    'kad. object': 'Kadastrale objecten'
}


def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))


def get_access_token(username, password, acceptance, scopes):
    state = randomword(10)
    acc_prefix = 'acc.' if acceptance else ''
    authz_url = f'https://{acc_prefix}api.data.amsterdam.nl/oauth2/authorize'
    params = {
        'idp_id': 'datapunt',
        'response_type': 'token',
        'client_id': 'citydata',
        'scope': ' '.join(scopes),
        'state': state,
        'redirect_uri': f'https://{acc_prefix}data.amsterdam.nl/'
    }

    response = requests.get(authz_url, params, allow_redirects=False)
    if response.status_code == 303:
        location = response.headers["Location"]
    else:
        return {}

    data = {
        'type': 'employee_plus',
        'email': username,
        'password': password,
    }

    response = requests.post(location, data=data, allow_redirects=False)
    if response.status_code == 303:
        location = response.headers["Location"]
    else:
        return {}

    response = requests.get(location, allow_redirects=False)
    if response.status_code == 303:
        returned_url = response.headers["Location"]
    else:
        return {}

    # Get grantToken from parameter aselect_credentials in session URL
    parsed = urlparse(returned_url)
    fragment = parse_qsl(parsed.fragment)
    access_token = fragment[0][1]
    return access_token


class AuthorizationSetup(object):
    """
    Helper methods to setup JWT tokens and authorization levels

    sets the following attributes:

    token_default
    token_employee
    token_employee_plus
    """
    def __init__(self):

        self.token_default = None
        self.token_employee = None
        self.token_employee_plus = None

        self.set_up_authorization()

    def set_up_authorization(self):
        """
        SET

        token_default
        token_employee
        token_employee_plus

        to use with:

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.token_employee_plus))

        """
        password = os.getenv('PASSWORD', 'unknown')
        username = os.getenv('USERNAME', 'searchtest')
        environment = os.getenv('ENVIRONMENT', 'acceptance')
        if password != 'unknown':
            self.token_default = get_access_token(username, password, environment == 'acceptance', [])
            self.token_employee = get_access_token(username, password, environment == 'acceptance',
                                                    [s for s in authorization_levels.SCOPES_EMPLOYEE])
            self.token_employee_plus = get_access_token(username, password, environment == 'acceptance',
                                                         [s for s in authorization_levels.SCOPES_EMPLOYEE_PLUS])
            print(f'token_employee: {self.token_employee}')
            print(f'token_employee: {self.token_employee_plus}')
            print(f'We can create authorized requests for user {username} in {environment}!')
        else:
            # NEW STYLE AUTH
            # The following JWKS data was obtained in the authz project :  jwkgen -create -alg ES256
            # This is a test public/private key def and added for testing .
            JWKS_TEST_KEY = """
                {
                    "keys": [
                        {
                            "kty": "EC",
                            "key_ops": [
                                "verify",
                                "sign"
                            ],
                            "kid": "2aedafba-8170-4064-b704-ce92b7c89cc6",
                            "crv": "P-256",
                            "x": "6r8PYwqfZbq_QzoMA4tzJJsYUIIXdeyPA27qTgEJCDw=",
                            "y": "Cf2clfAfFuuCB06NMfIat9ultkMyrMQO9Hd2H7O9ZVE=",
                            "d": "N1vu0UQUp0vLfaNeM0EDbl4quvvL6m_ltjoAXXzkI3U="
                        }
                    ]
                }
            """

            jwks_string = os.getenv('PUB_JWKS', JWKS_TEST_KEY)
            jwks_signers = jwks.load(jwks_string).signers

            assert len(jwks_signers) > 0
            if len(jwks_signers) == 0:
                print("""

                WARNING WARNING WARNING

                'JWT_SECRET_KEY' MISSING!!

                """)
                return False

            list_signers = [(k, v) for k, v in jwks_signers.items()]
            (kid, key) = list_signers[len(list_signers)-1]
            header = {"kid": kid}

            print('We can create authorized requests!')

            now = int(time.time())

            token_default = jwt.encode({
                'scopes': [],
                'iat': now, 'exp': now + 3600}, key.key, algorithm=key.alg, headers=header)
            token_employee = jwt.encode({
                'scopes': [s for s in authorization_levels.SCOPES_EMPLOYEE],
                'iat': now, 'exp': now + 3600}, key.key, algorithm=key.alg, headers=header)
            token_employee_plus = jwt.encode({
                'scopes': [s for s in authorization_levels.SCOPES_EMPLOYEE_PLUS],
                'iat': now, 'exp': now + 3600}, key.key, algorithm=key.alg, headers=header)

            self.token_default = str(token_default, 'utf-8')
            self.token_employee = str(token_employee, 'utf-8')
            self.token_employee_plus = str(token_employee_plus, 'utf-8')


auth = AuthorizationSetup()


class TestCase(object):
    """
    Represents a single test case line in the google doc / csv
    """
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
        self.expected_type = CATEGORY_LABEL_MAP[row[5]]
        self.comparator_typeahead = row[6]
        self.comparator_search = row[7]
        self.known_failure = (row[8] == "1")
        self.auth_level = row[9]
        self.expected_position = row[10]
        self.documentation = row[12]
        self.category_data = []

        self._check_comparator(self.comparator_search)
        self._check_comparator(self.comparator_typeahead)

        self._check_query_is_valid()

    def _check_comparator(self, comparator):
        if comparator not in ['eq', 'not eq']:
            raise SyntaxError("Unknown comparator: <%s>" % (comparator,))

    def _check_query_is_valid(self):
        if not bool(self.query):
            raise ValueError("query is missing: <%s>" % (self.query,))

    def allows_empty_result_typeahead(self):
        return self.comparator_typeahead == 'not eq'

    def __str__(self):
        return "%10s %-5s" % (self.name, self.sub_name)

    def eq_or_noteq(self):
        if 'not eq' in self.comparator_typeahead:
            return '!='
        return "=="

    def do_search_request(self):

        payload = {'q': self.query}
        the_test_url = '{}/typeahead/'.format(args.url)
        headers = {}

        # set authorization if needed
        if self.auth_level == '1':
            headers = {'Authorization': f'Bearer {auth.token_employee}'}
        elif self.auth_level == '2':
            headers = {'Authorization': f'Bearer {auth.token_employee_plus}'}

        response = requests.get(the_test_url, params=payload, headers=headers)

        return response

    def is_valid(self, response):
        """
        Check if expected result value is found in search response
        """
        if response.status_code != 200:
            log.error(response.status_code)
            log.error(response.text)
            log.error(response)
            return False

        data = response.json()

        # if we do not want to match and we do not have
        # data the test was a success

        if not data:
            return self.allows_empty_result_typeahead()

        # find the result category we want to match
        search_result = None

        should_not_find = 'not eq' in self.comparator_typeahead

        for category in data:
            if category['label'] == self.expected_type:
                search_result = category['content']
                # we found our content
                break

        if not search_result:
            return should_not_find

        display_results = [r['_display'] for r in search_result]
        # check if expected result is in
        # any display field
        result_in_data = self.expected in "|".join(display_results)

        self.category_data = display_results

        if should_not_find:
            return not result_in_data
        else:
            return result_in_data


def load_tests():
    all_tests = []

    with open("robs_tests.csv", encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)

        for i, row in enumerate(reader):
            # skip first 6 lines
            if i < 7:
                continue

            # commented out
            if not row[0] or row[0].startswith('#'):
                continue

            test = TestCase(row)
            all_tests.append(test)

    return all_tests


def run_tests(all_tests):
    """

    :type all_tests: [TestCase]
    """
    failed = 0
    known_failures = 0

    for test in all_tests:

        response = test.do_search_request()

        is_ok = test.is_valid(response)

        if not is_ok and not test.known_failure:
            failed += 1
        elif test.known_failure:
            known_failures += 1

        status = "%s %-45s %-4s %-5s %-4s %-5s  %s" % (
            test,
            test.query,
            'OK' if is_ok else 'FAIL',
            'KNOWN' if test.known_failure else '',
            '' if is_ok else test.eq_or_noteq(),
            '' if is_ok else test.expected_type,
            '' if is_ok else test.expected
        )

        log.debug(status)
        if not is_ok and not test.known_failure:
            log.debug('We got: %s' % test.category_data)

    if failed:
        log.debug('Failed: %s of %s' % (failed, len(all_tests)))
        os.sys.exit(9)
    else:
        log.info('Known failures: %s of %s' % (known_failures, len(all_tests)))
        log.info('SUCCESS')
        os.sys.exit(0)


def main():
    all_tests = load_tests()
    run_tests(all_tests)


if __name__ == "__main__":
    main()
