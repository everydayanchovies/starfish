#!/usr/bin/env bash

set -x

cd /home/ubuntu/Starfish-master

/usr/bin/python3 manage.py runserver starfish-education.eu:8000 &
