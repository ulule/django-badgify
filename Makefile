.venv:
	virtualenv -p python2.7 `pwd`/.venv
	. .venv/bin/activate && pip install -r requirements/development.txt

install: .venv

clean:
	@rm -rvf .env .venv .tox build django-badgify* *.egg-info

pep8:
	@flake8 badgify --ignore=E501,E127,E128,E124

test:
	@coverage run --branch --source=badgify manage.py test badgify
	@coverage report --omit=*migrations*,*tests*,*management*

create_fixtures:
	. .venv/bin/activate && ENV=example python manage.py create_fixtures

serve: .venv
	. .venv/bin/activate && ENV=example python manage.py migrate --run-syncdb
	. .venv/bin/activate && ENV=example python manage.py runserver

release:
	rm -rf dist/*
	python setup.py sdist
	twine upload dist/*

delpyc:
	find . -name '*.pyc' -delete
