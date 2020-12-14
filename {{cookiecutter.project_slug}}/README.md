# {{ cookiecutter.project_name }}

{{ cookiecutter.description }}

## Installation

Setup a virtualenv and install requirements:

```bash
mkvirtualenv --no-site-packages {{ cookiecutter.project_slug }} -p python3
pip install -r requirements.txt
```

## Running server

```bash
./manage.py runserver
```

## Building front-end

To build JavaScript and CSS files, first install npm packages:

```bash
npm install
```

Then to build (and watch for changes locally) just run:

```bash
npm run dev-watch
```

## Running Celery

Celery can be used to run background tasks. To run it you can use:

```bash
celery -A {{ cookiecutter.project_slug }} worker -l INFO
```
{% if cookiecutter.enable_google_login == 'y' %}
## Google Authentication Setup

To setup Google Authentication, follow the [instructions here](https://django-allauth.readthedocs.io/en/latest/providers.html#google).
{% endif %}

## Running Tests

To run tests simply run:

```bash
./manage.py test
```

Or to test a specific app/module:

```bash
./manage.py test apps.utils.tests.test_slugs
```


On Linux-based systems you can watch for changes using the following:

```bash
ack --python | entr python ./manage.py test
```
