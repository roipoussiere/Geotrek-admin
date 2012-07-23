SHELL = /bin/bash

baseurl=http://localhost:8000

bin/ lib/:
	virtualenv .
	wget http://python-distribute.org/bootstrap.py
	bin/python bootstrap.py
	rm bootstrap.py

install: bin/

clean_harmless:
	find caminae/ -name "*.pyc" -exec rm {} \;

clean: clean_harmless
	rm -rf bin/ lib/ local/ include/ *.egg-info/ develop-eggs/ parts/
	rm -rf reports/ var/
	rm -f .installed.cfg

unit_tests: bin/ clean_harmless
	bin/buildout -Nvc buildout-tests.cfg
	bin/django jenkins --coverage-rcfile=.coveragerc authent core land maintenance

functional_tests: 
	casperjs --baseurl=$(baseurl) --save=reports/FUNC-auth.xml caminae/tests/auth.js

tests: unit_tests functional_tests

serve: bin/ clean_harmless
	bin/buildout -Nvc buildout-dev.cfg
	bin/django syncdb --noinput --migrate
	bin/django runserver

load_data:
	# /!\ will delete existing data
	bin/django loaddata development-pne

deploy: bin/ clean_harmless
	bin/buildout -Nvc buildout-prod.cfg
	bin/django syncdb --noinput --migrate
	bin/supervisorctl restart all


.PHONY: all_makemessages all_compilemessages

all_makemessages:
	for dir in `find caminae/ -type d -name locale`; do pushd `dirname $$dir` > /dev/null; django-admin makemessages -a; popd > /dev/null; done

all_compilemessages:
	for dir in `find caminae/ -type d -name locale`; do pushd `dirname $$dir` > /dev/null; django-admin compilemessages; popd > /dev/null; done

deploy_demo: deploy load_data

