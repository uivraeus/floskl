# floskl

A simple blog application implemented in [Flask](https://flask.palletsprojects.com/en/3.0.x/) (Python), very much inspired by [the Flask tutorial](https://flask.palletsprojects.com/en/3.0.x/tutorial/).
    
Data persistence is managed by [PostgreSQL](https://www.postgresql.org/).

## Pre-condition: A running PostgreSQL database

### Running locally

```shell
./start-dev-db.sh
```

This will start an instance of the database with settings matching the default values of the app.

It is OK to run this start script also when the database is already running (nothing will happen).

> The script expects [Docker](https://www.docker.com/) and [docker-compose](https://docs.docker.com/compose/) to be available on your machine. 

You can stop the database by running:

```
./stop-dev-db.sh
```

### External database

Obtain settings such as host/port and credentials needed when configuring the application via the following environment variables:

```shell
FLOSKL_POSTGRES_HOST
FLOSKL_POSTGRES_PORT
FLOSKL_POSTGRES_DB
FLOSKL_POSTGRES_USER 
FLOSKL_POSTGRES_PASSWORD
```

## Run locally (during development)

### Option 1: run via CLI

Setup Python environment (`venv`) and enter the `app` directory:

```shell
./prep-venv.sh && source .venv/bin/activate
cd app
```

Initialize database schemas:

```shell
flask --app floskl init-db
```

> You only need to run this once unless you want to reset the database by adding the `--reset` option.

Run the app in "dev mode", with Flask's dev-server etc.:

```shell
flask --app floskl run
```

Alternatively, if you want to run in production-mode with the [Gunicorn](https://gunicorn.org/) HTTP-server, i.e. without Flask's dev-server:

```shell
gunicorn --config gunicorn_config.py
```

### Option 2: run via [Visual Studio Code](https://code.visualstudio.com/)

There are tasks and launcher options prepared, both for initializing the database and for running the application in "development mode", with full support for breakpoints, variable inspections etc (incl. automatic restart when you save you update the code).

The list of launcher options are found in the drop-down select in the "Run and Debug" pane (Ctrl + Shift + D):

* Python: Init database 
* Python: Flask

The Python `venv` environment is automatically prepared and activated when using these options. 

> This repo also contains a [dev container](.devcontainer/devcontainer.json) definition, which is prepared for Python development (and more). By leveraging this feature you don't need a local install of Python and other applicable tools (or the "correct" versions of them).
>
> Read more about the "dev container" concept in the [docs](https://code.visualstudio.com/docs/devcontainers/containers) and make sure to have the [Dev Container extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) installed.
>
> Even if you don't use this feature, you can still use the launcher options described above as long as you open the repo root directory in Visual Studio Code.
