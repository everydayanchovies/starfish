#!/usr/bin/env bash

set -x

cd /home/ubuntu/Starfish-master

sudo pkill -f uwsgi -9

uwsgi --ini uwsgi_prod.ini

