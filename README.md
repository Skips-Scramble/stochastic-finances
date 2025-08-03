# AppStack Django Starter

Thanks for downloading AppStack. This project features a batteries-included Django starter project for AppStack. It is based on [DjangoX](https://github.com/wsvincent/djangox).

## Features

- Django 3.1 & Python 3.8
- Install via [Pip](https://pypi.org/project/pip/), [Pipenv](https://pypi.org/project/pipenv/), or [Docker](https://www.docker.com/)
- User log in/out, sign up, password reset via [django-allauth](https://github.com/pennersr/django-allauth)
- Static files configured with [Whitenoise](http://whitenoise.evans.io/en/stable/index.html)
- Debugging with [django-debug-toolbar](https://github.com/jazzband/django-debug-toolbar)
- DRY forms with [django-crispy-forms](https://github.com/django-crispy-forms/django-crispy-forms)

## Table of Contents
* **[Installation](#installation)**
  * [Pip](#pip)
  * [Pipenv](#pipenv)
  * [Docker](#docker)
* [Setup](#setup)

## Installation
AppStack Django can be installed via Pip, Pipenv, or Docker depending upon your setup. To start, clone the repo to your local computer and change into the proper directory.

### Pip

```
$ pip install -r requirements.txt
$ python manage.py migrate
$ python manage.py createsuperuser
$ python manage.py runserver
# Load the site at http://127.0.0.1:8000
```

### Pipenv

```
$ pipenv install
$ pipenv shell
$ python manage.py migrate
$ python manage.py createsuperuser
$ python manage.py runserver
# Load the site at http://127.0.0.1:8000
```

### Docker

```
$ docker build .
$ docker-compose up -d
$ docker-compose exec web python manage.py migrate
$ docker-compose exec web python manage.py createsuperuser
# Load the site at http://127.0.0.1:8000
```

For Docker, the `INTERNAL_IPS` configuration in `config/settings.py` must be updated to the following:

```python
# config/settings.py
# django-debug-toolbar
import socket
hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = [ip[:-1] + "1" for ip in ips]
```

## Setup

```
# Run Migrations
$ python manage.py migrate

# Create a Superuser
$ python manage.py createsuperuser

# Confirm everything is working:
$ python manage.py runserver

# Load the site at http://127.0.0.1:8000
```

## General Information
To get the VS Code instance going using poetry:
- Open a command window
- Navigate to where the repo is
- Then execute `poetry run code .`

### Poetry
Opening up from command line: `poetry shell`
Add packages
  - `poetry add <package name>`
    - This will automatically choose the right version for you
  - This will rebuild for you as well

### Ruff
We are using ruff as our formatter and linter
- [Getting Started](https://docs.astral.sh/ruff/tutorial/#getting-started)
- `ruff check`
- `ruff check --fix`
- `ruff check <file location>`
- `ruff format`

### Djlint
I don't think ruff lints and formats django html files, so we use djlint
Make sure you are in a poetry shell, or prefix with `poetry run`
  - `djlint /path/to/file.html --check`
  - `djlint /path/to/file.html --reformat`
