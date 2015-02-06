.venv:
	virtualenv -p python2.7 `pwd`/.venv
	. .venv/bin/activate && pip install -r requirements/development.txt

install: .venv
	bower i

clean:
	@rm -rvf .env .venv .tox build django-badgify* *.egg-info

pep8:
	@flake8 badgify --ignore=E501,E127,E128,E124

test:
	@coverage run --branch --source=badgify manage.py test badgify
	@coverage report --omit=*migrations*,*tests*,*management*

test: .venv
	. .venv/bin/activate && coverage run --branch --source=badgify manage.py test badgify
	. .venv/bin/activate && coverage report --omit=badgify/test*

serve: .venv
	. .venv/bin/activate && ENV=example python manage.py syncdb
	. .venv/bin/activate && ENV=example python manage.py migrate
	. .venv/bin/activate && ENV=example python manage.py create_fixtures
	. .venv/bin/activate && ENV=example python manage.py runserver

release:
	python setup.py sdist register upload -s

delpyc:
	find . -name '*.pyc' -delete
