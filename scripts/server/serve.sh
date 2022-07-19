#!/usr/bin/env bash

if ! test -f /home/ubuntu/; then
    echo "This script is meant to be run on the production server only."
    exit 1
fi

set -x

cd /home/ubuntu/Starfish-master

sudo pkill -f uwsgi -9

uwsgi --ini uwsgi_prod.ini

