#!/usr/bin/env bash

set -x

cd /home/ubuntu/Starfish-master

set +x
# enter python venv
source venvdj3/bin/activate
set -x

python manage.py backup_database /home/ubuntu/Starfish-master/db.sqlite
