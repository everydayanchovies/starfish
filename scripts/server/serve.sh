#!/usr/bin/env sh

if ! [ -d "/home/ubuntu/" ]; then
    echo "This script is meant to be run on the production server only."
    exit 1
fi

set -x

PROJECT_ROOT=/home/ubuntu/Starfish-master;

cd $PROJECT_ROOT || exit

. "$PROJECT_ROOT/.venv/bin/activate";

uwsgi --ini uwsgi_prod.ini 

