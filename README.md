Starfish
=====
Starfish was originally written for Django 1.5 in Python 2, since this version is not secure anymore the project needed to be made compatible with a newer version of Django (Django 2.0). The readme file will be kept up to date as the project advances through the update. If for some reason the project needs to be compatible with django x.x.x one can find the dependancies/instructions etc for that version.

&copy; ICTO FNWI


## Dependencies
This system is written in Python 3.6.3 using Django 2.0.5 and requires PostgreSQL 10.3 or higher.
Python dependencies are listed in `requirements.txt`, which also will be updated if the project supports a new version of Django.

## Getting started

### Database
Make sure that PostgreSQL is installed and running and that a database with user is set up. A good guide how to do this can be found [here](https://djangogirls.gitbooks.io/django-girls-tutorial-extensions/content/optional_postgresql_installation/) (NOTE: stop before the 'Update settings' part).

### Python version
Make sure you're using Python 3.6.3 You are strongly encouraged to use a [virtual environment](https://virtualenv.pypa.io/en/stable/).


```shell
$ python3 -m venv myenviroment
$ source venv/bin/activate
```

Now install dependencies:

```shell
(venv) $ pip install -r requirements.txt
```

### Settings
add secrets.json file in root of project with following inside:

```json
{
    "SECRET_KEY" : "your_local_secretkey",
    "DB_NAME"    : "your_local_database_name",
    "DB_USER"    : "your_db_owner",
    "DB_PWD"     : "password_of_owner",
    "DB_PORT"    : "some_port" or "",
    "ADMIN_NOTIFICATION_EMAIL" : "",
    "SERVER_EMAIL": "",
    "ADMIN_EMAIL": "",
    "IVO_TOKEN": ""
}
```

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

``` shell
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

## Installing uWSGI fails on M1 machines

```shell
ln -s /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.8/lib/python3.8/config-3.8-darwin/libpython3.8.a ~/miniconda3/lib/python3.8/config-3.8-darwin/
pip install uWSGI==2.0.17
```
