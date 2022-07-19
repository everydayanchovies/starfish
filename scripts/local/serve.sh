#!/usr/bin/env bash

if test -f /home/ubuntu/; then
    echo "This script is NOT meant to be run on the production server."
    exit 1
fi

. venv/bin/activate

python3 manage.py runserver
