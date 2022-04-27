#!/usr/bin/env bash

set -x

cd /home/ubuntu/Starfish-master

git pull --ff-only

pkill uwsgi

./scripts/server/serve.sh > /var/log/starfish/prod.log 2>&1
