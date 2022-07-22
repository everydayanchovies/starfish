{ pkgs ? import <nixpkgs> {} }:

with pkgs;

let
  my-python = pkgs.python39;
  python-with-my-packages = my-python.withPackages (p: with p; [
    wheel
    virtualenv
  ]);
in
mkShell {
  buildInputs = [
    procps
    memcached
    sqlite
    pcre
    openjpeg
    libtiff
    libimagequant
    icu
    libxml2
    zlib
    lzma
    openldap
    openssl
    cyrus_sasl
    expat
    ncurses
    git
    cacert
    my-python
    python-with-my-packages
  ];

  shellHook = ''
    GIT_SSL_CAINFO=$HOME/.nix-profile/etc/ca-bundle.crt

    alias sf='python manage.py';
    alias venv-upgrade='pip install -r requirements.txt';
    alias db-pull-from-prod='sh ./scripts/local/pull-db-from-prod.sh';
    alias upgrade='sh ./scripts/server/upgrade.sh';
    alias db-backup='sh ./scripts/server/backup.sh';
    alias cache-warmup='sh ./scripts/server/cache_warmup.sh';
    alias kill-memcached='kill_memcached';
    alias h='display_help';

    kill-process() {
      ps ax | grep "$1" | grep -v grep | awk '{print $1}' | xargs kill
    }

    serve () {
      if test -f /home/ubuntu/; then
        sh ./scripts/server/serve.sh;
      else
        kill-process memcached;
        memcached -l localhost -p 11211 &
        sf runserver;
      fi
    }

    function cleanup {
      echo "Killing leftover processes...";
      kill-process memcached;
      kill-process "python manage.py";
      kill-process node;
    }
    trap cleanup EXIT;

    if [ ! -d ./.venv ]; then
      echo "Creating python virtual environment (venv)...";
      python3 -m venv .venv;
      echo "Activating python venv...";
      source .venv/bin/activate;
      pip install --upgrade pip;
      echo "Installing python packages in venv...";
      venv-upgrade;
    else
      source .venv/bin/activate;
    fi

    #clear;

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

    display_help () {
      echo "You can use the following assist commands:";
      echo "  sf                 short for python manage.py";
      echo "  sf check           check starfish configuration";
      echo "  sf makemigrations  create database migrations";
      echo "  sf migrate         run database migrations";
      echo "                                          ";
      echo "  ---administrative-----------------------";
      echo "  serve              serve the application (works on dev and prod)";
      echo "  venv-upgrade       install python requirements in venv";
      echo "  kill-process       kill a process by name";
      echo "                                          ";
      if test -f /home/ubuntu/; then
        echo "  ---development--(you're-running-in-prod)";
      else
        echo "  ---development--------------------------";
      fi
      echo "  db-pull-from-prod  overwrite local db with the one on prod";
      echo "                                          ";
      if test -f /home/ubuntu/; then
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

    display_help;
  '';
}
