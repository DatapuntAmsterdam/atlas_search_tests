#!/usr/bin/env bash

set -u
set -e
set -x

docker-compose rm -f

docker-compose build

docker-compose run tests ./robs_tests.py $URL

docker-compose run tests ./pyresttest.sh $URL
