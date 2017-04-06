# Atlas_search_tests
Search Tests op de HELE elastic dataset. Search Regressie vangnet

Nieuwe 'zoek features' gedragen zich vaak anders op de hele dataset.
Ook het toevoegen van nieuwe datasets kan bestaande zoek resultaten
vervuilen.

Het project bevat twee soorten tests: 

1. Tests gebaseerd op [pyresttest](https://github.com/svanoort/pyresttest)
2. Tests gebaseerd op een [Google Sheet](https://docs.google.com/spreadsheets/d/15i_rXplhsZhQIXwPmxKX2O54s9InrUupFAuD-hU03g4), ook bekend als de "Rob tests". 


## Install

- mkvirtualenv search_test
- pip install -r requirements.txt

## Runtests

    resttest.py https://acc.api.data.amsterdam.nl smoke_test.yml
    
## Specific test for atlas client created by rob m and rob k.

    python robs_tests.py https://acc.api.data.amsterdam.nl


## Docker environment

Either run the test directly or use the run script. Directly run test using:

    docker-compose build
    docker-compose run smoketest resttest.py https://acc.api.data.amsterdam.nl smoke_test.yml 

Use the run script as follows:

	URL=https://acc.api.data.amsterdam.nl ./run_tests.sh
