install:
	@test -d .venv || virtualenv .venv
	@test -d .venv-django16 || virtualenv .venv-django16
	@echo "source `pwd`/.venv/bin/activate" >> .env
	@. .venv-django16/bin/activate && pip install -r requirements/base-development.txt
	@. .venv-django16/bin/activate && pip install Django==1.6 South
	@. .venv/bin/activate && pip install -r requirements/development.txt

clean:
	@rm -rvf .env .venv .tox build django-badgify* *.egg-info

pep8:
	@flake8 badgify --ignore=E501,E127,E128,E124

test:
	@coverage run --branch --source=badgify manage.py test badgify
	@coverage report --omit=*migrations*,*tests*,*management*

release:
	python setup.py sdist register upload -s

example-install:
	@bower i
	@ENV=example python manage.py syncdb
	@ENV=example python manage.py migrate
	@ENV=example python manage.py create_fixtures

example-runserver:
	@ENV=example python manage.py runserver [::]:8000

example: example-install example-runserver
