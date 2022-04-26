#!/usr/bin/env bash

set -x

cd /home/ubuntu/Starfish-master

source venvdj3/bin/activate

uwsgi --ini uwsgi_prod.ini

