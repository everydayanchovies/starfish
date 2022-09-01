#!/usr/bin/env sh

if ! [ -d "/home/ubuntu/" ]; then
    echo "This script is meant to be run on the production server only."
    exit 1
fi

set -x

cd /home/ubuntu/Starfish-master || exit

set +x
# enter python venv
. .venv/bin/activate
set -x

python manage.py backup_database /home/ubuntu/Starfish-master/db.sqlite

ls -1 . | grep ".*.sqlite" | grep -vw "db.sqlite" | xargs -I{} mv {} /home/ubuntu/backups/
