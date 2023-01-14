#!/usr/bin/env bash

if test -f /home/ubuntu/; then
    echo "This script is NOT meant to be run on the production server."
    exit 1
fi

. .venv/bin/activate

pkill -9 memcached
memcached -l localhost -p 11211 &

pkill -9 caddy
caddy run --config "./caddy/caddy-dev.conf" --adapter caddyfile &

python manage.py runserver
