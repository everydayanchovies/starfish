# Starfish

&copy; ICTO FNWI

## Dependencies

This system is written in Python 3.9 using Django (LTS) 3.2.
Python dependencies are listed in `requirements.txt`.
Other dependencies are embedded in `shell.nix`, namely `memcached` and `sqlite3`.
You will need `yarn` to work on the frontend.

## Getting started

### A true quick-start

Install [nix-shell](https://nixos.org/download.html) and execute `shell.sh` to enter the Starfish shell.
This pulls the necessary dependencies and provides an interface to the project:

```text
You can use the following assist commands:
  sf                 short for python manage.py
  sf check           check starfish configuration
  sf makemigrations  create database migrations
  sf migrate         run database migrations

  ---administrative-----------------------
  serve              serve the application (works on dev and prod)
  venv-upgrade       install python requirements in venv

  ---development--------------------------
  db-pull-from-prod  create a local backup of the database

  ---production--(you're-running-in-dev)--
  upgrade            fetches the latest source code and restarts
  db-backup          create a local backup of the database
  cache-warmup       warms up the cache

  ---misc---------------------------------
  h                  display this message again
```

If you would rather work without nix, read on.

### Database

The database is stored in `db.sqlite` on the project root.
This will need to be migrated to PostgreSQL once it starts to get slow.

### Python version

Make sure you're using Python 3.9.
You are strongly encouraged to use a [virtual environment](https://virtualenv.pypa.io/en/stable/).

```shell
$ python3 -m venv myenviroment
$ source venv/bin/activate
```

Now install dependencies:

```shell
(venv) $ pip install -r requirements.txt
```

### Cache

Install and setup a local instance of memcached before serving.

### Check, double check

To make sure everything is set up and configured well, run:

```shell
(venv) $ ./manage.py check
```

### Create and run migrations

Now that everything is setup, we can set up the datastructures.

```shell
(venv) $ python manage.py migrate
```

### Create a superuser

In order to use the admin site, you'll need a superuser account.

```shell
(venv) $ python manage.py createsuperuser
```

### Run development server

You are now ready to run the development server:

```shell
(venv) $ python manage.py runserver
```

### Run production server

```shell
./scripts/server/serve.sh > /var/log/starfish/prod.log 2>&1
```

### Using your user account...

To use your user account, first login to the admin page and create a person for
the user.

## Maintaining database migrations

Every time fields in any of the models change, a [database migration](https://docs.djangoproject.com/en/1.11/topics/migrations/)
needs to be created and applied. The first documents a database change and its
inverse, the second actually changes the database.

Make sure to commit the migration to GIT after applying it, so other developers
can use them.

```shell
(venv) $ python manage.py makemigration
(venv) $ python manage.py migrate
```

# Troubleshooting

## Installing uWSGI fails on M1 machines

```shell
ln -s /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.8/lib/python3.8/config-3.8-darwin/libpython3.8.a ~/miniconda3/lib/python3.8/config-3.8-darwin/

pip install uWSGI==2.0.17
```
