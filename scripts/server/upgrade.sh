#!/usr/bin/env bash

set -x

cd /home/ubuntu/Starfish-master

cp db.sqlite /home/ubuntu/db_backups/misc/db_$(date +%F-%T).sqlite

git pull --ff-only

pkill uwsgi

./scripts/server/serve.sh > /var/log/starfish/prod.log 2>&1
