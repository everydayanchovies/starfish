#!/usr/bin/env bash

PROJECT_ROOT=$PWD;

alias sf='python $PROJECT_ROOT/manage.py';
alias db-pull-from-prod='sh $PROJECT_ROOT/scripts/local/pull-db-from-prod.sh';
alias upgrade='sh $PROJECT_ROOT/scripts/server/upgrade.sh';
alias db-backup='sh $PROJECT_ROOT/scripts/server/backup.sh';
alias cache-warmup='sh $PROJECT_ROOT/scripts/server/cache_warmup.sh';
alias enter-db='litecli $PROJECT_ROOT/db.sqlite';
alias prod='ssh ubuntu@starfish-education.eu';
alias h='display_help';

venv-upgrade () {
  pip install -r "$PROJECT_ROOT/requirements.txt";
  pip install https://projects.unbit.it/downloads/uwsgi-lts.tar.gz;
}

serve () {
  if [ -d /home/ubuntu/ ]; then
    sh "$PROJECT_ROOT/scripts/server/serve.sh";
  else
    kill-process memcached;
    memcached -l localhost -p 11211 &
    sf runserver;
  fi
}

if [ ! -d "$PROJECT_ROOT/.venv" ]; then
  echo "Warning! Create a python virtual environment (see scripts/)."
else
  source "$PROJECT_ROOT/.venv/bin/activate";
fi

display_help () {
  echo "You can use the following assist commands:";
  echo "                                          ";
  echo "  ---django-------------------------------";
  echo "  sf                 short for python manage.py";
  echo "  sf check           check starfish configuration";
  echo "  sf makemigrations  create database migrations";
  echo "  sf migrate         run database migrations";
  echo "                                          ";
  echo "  ---administrative-----------------------";
  echo "  serve              serve the application (works on dev and prod)";
  echo "  enter-db           enter the database";
  echo "  venv-upgrade       install python requirements in venv";
  echo "  kill-process       kill a process by name";
  echo "                                          ";
  if [ -d /home/ubuntu/ ]; then
    echo "  ---development--(you're-running-in-prod)";
  else
    echo "  ---development--------------------------";
  fi
  echo "  prod               enter the production shell";
  echo "  db-pull-from-prod  overwrite local db with the one on prod";
  echo "                                          ";
  if [ -d /home/ubuntu/ ]; then
    echo "  ---production---------------------------";
  else
    echo "  ---production--(you're-running-in-dev)--";
  fi
  echo "  upgrade            fetches the latest source code and restarts";
  echo "  db-backup          create a local backup of the database";
  echo "  cache-warmup       warms up the cache";
  echo "                                          ";
  echo "  ---misc---------------------------------";
  echo "  h                  display this message again";
  echo "                                          ";
}

# clear screen
printf "\033c"

cat << EOF
 .d8888b. 888                   .d888d8b        888
d88P  Y88b888                  d88P" Y8P        888
Y88b.     888                  888              888
 "Y888b.  888888 8888b. 888d888888888888.d8888b 88888b.
    "Y88b.888       "88b888P"  888   88888K     888 "88b
      "888888   .d888888888    888   888"Y8888b.888  888
Y88b  d88PY88b. 888  888888    888   888     X88888  888
 "Y8888P"  "Y888"Y888888888    888   888 88888P'888  888


EOF

display_help;
