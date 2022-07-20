{ pkgs ? import <nixpkgs> {} }:

with pkgs;

let 
	my-python = pkgs.python3;
	python-with-my-packages = my-python.withPackages (p: with p; [
	requests
	ldap
	]);
in
mkShell {
  buildInputs = [
    python-with-my-packages
    memcached
    python39
    sqlite
	uwsgi
	pcre
	icu
	libxml2
	zlib
	lzma
	openldap
	python39Packages.ldap
	openssl
	cyrus_sasl
  ];

  shellHook = ''
    clear;

    if [ ! -d ./venv ]; then
      echo "Creating python virtual environment (venv)...";
      python3 -m venv venv;
      echo "Activating python venv...";
      source venv/bin/activate;
      pip install --upgrade pip;
      echo "Installing python packages in venv...";
      venv-upgrade
    fi

    . venv/bin/activate;

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


    serve () {
      if test -f /home/ubuntu/; then
        sh ./scripts/server/serve.sh;
      else
        pkill -9 memcached;
        memcached -l localhost -p 11211 &
        sf runserver;
      fi
    }

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
      echo "                                          ";
      if test -f /home/ubuntu/; then
        echo "  ---development--(you're-running-in-prod)";
      else
        echo "  ---development--------------------------";
      fi
      echo "  db-pull-from-prod  create a local backup of the database";
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
