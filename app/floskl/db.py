import psycopg2
import psycopg2.extras

import click
from flask import app, current_app, g
from psycopg2.errors import OperationalError


# Get access to the database via a request specific (reusable) cursor 
def get_req_cursor():
  # "current_app" is a special object that points to the Flask application
  # handling the request
  #
  # "g" is a special object that is unique for each request. 
  # It is used to store data that might be accessed by multiple functions 
  # during the request

  if 'db_cur' not in g:
    g.db_cur = get_fresh_cursor()

  # # Detect cold-start and auto-initialize DB schema
  # if not schema_exists(g.db_cur):
  #   print("No valid schema found. Initialize fresh database...")
  #   init_db(g.db_cur)
  #   print("Database initialized")

  return g.db_cur


# Clean-up request specific database connection (if there is one)
def close_req_db(e=None):
  db_cur = g.pop('db_cur', None)

  if db_cur is not None:
    close_cursor_connection(db_cur)


# Create a new connection and cursor for database access
def get_fresh_cursor():
  # https://www.psycopg.org/docs/usage.html#basic-module-usage
  connection = psycopg2.connect(
      dbname=current_app.config['POSTGRES_DB'],
      user=current_app.config['POSTGRES_USER'],
      password=current_app.config['POSTGRES_PASSWORD'],
      host=current_app.config['POSTGRES_HOST'],
      port=current_app.config['POSTGRES_PORT']
    )
  
  # https://varun-verma.medium.com/use-psycopg2-to-return-dictionary-like-values-key-value-pairs-4d3047d8de1b
  cursor = connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

  return cursor


# Close both cursor and its associated connection
def close_cursor_connection(cursor):
  connection = cursor.connection
  cursor.close()  
  connection.close()


def schema_exists(cursor):
  # https://stackoverflow.com/questions/1874113/checking-if-a-postgresql-table-exists-under-python-and-probably-psycopg2
  # (but here ".exists" is used as cursor initialized with real-dict factory)
  cursor.execute("""
    SELECT EXISTS(
      SELECT * FROM information_schema.tables
      WHERE table_name=%s
    )
  """, ('users',))
  result = cursor.fetchone() 
  return result['exists']


# Full init/reset of database
def init_db(cursor = None):
  if cursor is None:
    cursor = get_req_cursor()

  cursor.execute('DROP TABLE IF EXISTS users CASCADE')
  cursor.execute("DROP TABLE IF EXISTS post CASCADE")

  cursor.execute("""
    CREATE TABLE users (
      id SERIAL PRIMARY KEY,
      username TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL
    )
  """)

  cursor.execute("""
    CREATE TABLE post (
      id SERIAL PRIMARY KEY,
      author_id INTEGER NOT NULL,
      created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      title TEXT NOT NULL,
      body TEXT NOT NULL,
      FOREIGN KEY (author_id) REFERENCES users (id)
    )
  """)

  cursor.connection.commit()


@click.command('init-db')
@click.option('--reset', is_flag=True, show_default=True, default=False, help="Reset the database if it already exists")
def init_db_command(reset):
  """Check for valid database schema and create if necessary."""
  try:
    cursor = get_fresh_cursor()
    if not schema_exists(cursor) or reset:
      click.echo(f"Initialized a fresh database")
      init_db(cursor)
    else:
      click.echo(f"Existing database retained")
    close_cursor_connection(cursor)
  except OperationalError as error:
    click.echo("ERROR: Can't connect to PostgreSQL database! Invalid/missing configuration?", err=True)
    click.echo("---", err=True)
    click.echo(error, err=True)
    click.echo("---", err=True)
    raise SystemExit("Can't run without a database connection")  


def init_app(app):
  # Configure Flask hooks
  app.teardown_appcontext(close_req_db)
  app.cli.add_command(init_db_command)
