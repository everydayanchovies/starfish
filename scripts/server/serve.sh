#!/usr/bin/env bash

set -x

cd /home/ubuntu/Starfish-master

pkill uwsgi

uwsgi --ini uwsgi_prod.ini

