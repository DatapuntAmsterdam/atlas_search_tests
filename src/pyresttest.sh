#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

URL=$1

resttest.py ${URL} pyresttest/smoke_test.yml
resttest.py ${URL} pyresttest/aanduidingen_test.yml
resttest.py ${URL} pyresttest/hr_test.yml
resttest.py ${URL} pyresttest/typeahead.yml

