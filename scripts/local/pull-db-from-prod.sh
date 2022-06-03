#!/usr/bin/env bash

if ! test -f db.sqlite; then
    echo "Please run from project root."
    exit 1
fi

cp db.sqlite db.sqlite.pre-pull-from-prod-backup

scp ubuntu@starfish-education.eu:~/Starfish-master/db.sqlite .

echo "Done!"
