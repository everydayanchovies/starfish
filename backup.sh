#!/bin/bash

BACKUP_DIR=/home/sander/steep_backup
FILES_DIR=/var/www/steep
DB_DUMP_LOG=$FILES_DIR/db_dump.log

# Dump Django database
date >> $DB_DUMP_LOG
./manage.py dumpdata --format=json-unicode 2>> $DB_DUMP_LOG > \
	$BACKUP_DIR/incoming/db_dump.json

# Compress database dump
tar -cvzf $BACKUP_DIR/incoming/archive.tgz $BACKUP_DIR/incoming/db_dump.json \
	$FILES_DIR

# Cleanup
rm $BACKUP_DIR/incoming/db_dump.json

# Run backup rotate
cd $BACKUP_DIR
bash backup_rotate.sh
