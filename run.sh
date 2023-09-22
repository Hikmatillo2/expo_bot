#!/bin/bash

sleep 10
psql postgresql://postgres:d4a8f0435b2b866f855323d7d021a79164d2e13b@database -f psql.sql

service nginx start
# database postgresql start
python3 manage.py collectstatic --noinput
sleep 1
whoami
python3 test.py

#chmod -R u+w /srv/
python3 manage.py migrate
sleep 1
# chown www-data:www-data /srv/db.sqlite3
python3 manage.py makemigrations
sleep 1
python3 manage.py migrate
sleep 1
python3 manage.py initadmin
sleep 1
PYTHONUNBUFFERED=1 /bin/gunicorn3 wsgi:application -b 127.0.0.1:8000 --env DJANGO_SETTINGS_MODULE=settings --user www-data --group www-data --enable-stdio-inheritance --log-level debug
#python3 manage.py runserver
