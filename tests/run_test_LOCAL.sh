#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

URL="http://127.0.0.1:8000"

resttest.py $URL typeahead.yml
#resttest.py $URL aanduidingen_test.yml
#resttest.py $URL aanduidingen_test.yml
