#!/usr/bin/env sh

if ! [ -d "/home/ubuntu/" ]; then
    echo "This script is meant to be run on the production server only."
    exit 1
fi

set -x

cd /home/ubuntu/Starfish-master || exit

cp db.sqlite "/home/ubuntu/db_backups/misc/db_$(date +%F-%T).sqlite"

git pull --ff-only

set +x
# enter python venv
. .venv/bin/activate
set -x

python manage.py collectstatic --noinput

set +x
# exit python venv
deactivate
set -x

systemctl restart caddy
systemctl restart memcached.service
systemctl restart sf_django
