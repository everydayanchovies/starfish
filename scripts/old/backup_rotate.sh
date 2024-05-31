#!/bin/bash
# Backup rotation

# Storage folder where to move backup files
# Must contain backup.monthly backup.weekly backup.daily folders
BACKUP_DIR=/home/sander/starfish_backup

# to send mails to if backup failed TODO add email
ADMIN_MAIL=

# Source folder where files are backed
SOURCE_DIR=$BACKUP_DIR/incoming

# Destination file names
date_daily=`date +"%d-%m-%Y"`

date_weekly=`date +"%V sav. %m-%Y"`
date_monthly=`date +"%m-%Y"`

# Get current month and week day number
month_day=`date +"%d"`
week_day=`date +"%u"`

# Optional check if source files exist. Email if failed.
if [ ! -f $SOURCE_DIR/archive.tgz ]; then
ls -l $SOURCE_DIR/ | mail $ADMIN_MAIL \
	-s "[backup script] Daily backup failed! Please check for missing files."
fi

# This does not really do anything unless we uncomment the code for weekly and
# monthly updates below.
if [ "$month_day" -eq 1 ] ; then
  DESTINATION=backup.monthly/$date_daily
else
  if [ "$week_day" -eq 7 ] ; then
    DESTINATION=backup.weekly/$date_daily
  else
    DESTINATION=backup.daily/$date_daily
  fi
fi

# Move the files
mkdir $DESTINATION
mv -v $SOURCE_DIR/* $DESTINATION

# daily - keep for 7 days
mkdir -p $BACKUP_DIR/backup.daily/  # Make sure the directory exists
find $BACKUP_DIR/backup.daily/ -maxdepth 1 -mtime +7 -type d -exec rm -rv {} \;

# XXX Uncomment if using weekly and/or monthly backups
# weekly - keep for 60 days
#find $BACKUP_DIR/backup.weekly/ -maxdepth 1 -mtime +60 -type d -exec rm -rv {} \;

# monthly - keep for 300 days
#find $BACKUP_DIR/backup.monthly/ -maxdepth 1 -mtime +300 -type d -exec rm -rv {} \;
