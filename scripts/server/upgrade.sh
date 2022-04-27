#!/usr/bin/env bash

set -x

cd /home/ubuntu/Starfish-master

cp db.sqlite /home/ubuntu/db_backups/misc/db_$(date +%F-%T).sqlite

git pull --ff-only

set +x
# enter python venv
source venvdj3/bin/activate
set -x

python manage.py collectstatic --noinput

set +x
# exit python venv
deactivate
set -x

set +x

echo "To serve, run"
echo "/home/ubuntu/Starfish-master/scripts/server/serve.sh > /var/log/starfish/prod.log 2>&1"
