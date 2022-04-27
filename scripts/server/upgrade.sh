#!/usr/bin/env bash

set -x

cd /home/ubuntu/Starfish-master

cp db.sqlite /home/ubuntu/db_backups/misc/db_$(date +%F-%T).sqlite

git pull --ff-only

# enter python venv
source venvdj3/bin/activate

python manage.py collectstatic --noinput

# exit python venv
deactivate

echo "To serve, run"
echo "./scripts/server/serve.sh > /var/log/starfish/prod.log 2>&1"
