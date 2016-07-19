#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

URL=https://api.datapunt.amsterdam.nl

resttest.py $URL smoke_test.yml
resttest.py $URL aanduidingen_test.yml
resttest.py $URL typeahead.yml
