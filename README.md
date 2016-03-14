# Atlas_search_tests
Search Tests op de HELE elastic dataset.

Nieuwe 'zoek features' gedragen zich vaak anders op de hele dataset.
Ook het toevoegen van nieuwe datasets kan bestaande zoek resultaten
vervuilen.


Intstall

- maak een virtualenv voor pyhton2.7 !
-   mkvirtualenv --python=python2.7 search_test27
- pip install -r requirements.txt

Runtests

 - resttest.py https://api-acc.datapunt.amsterdam.nl smoke_test.yml


Docker environment

 - docker-compose build
 - docker-compose run smoketest resttest.py https://api-acc.datapunt.amsterdam.nl smoke_test.yml || echo "Test Failure"

