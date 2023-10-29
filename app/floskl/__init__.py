""" Package configuration
__init__.py serves double duty:
1. it will contain the application factory,
2. it tells Python that the floskl directory should be treated as a package.
"""

# pylint: disable=import-outside-toplevel

import os

from flask import Flask

def create_app(test_config=None):
    """Application Factory function"""
    # create and configure the app
    # (instance path not really used but configure a well-known value just in case)
    app = Flask(__name__, instance_path='/tmp/floskl-instance')
    app.config.from_mapping(
        # defaults
        SECRET_KEY="dev",  # <-- used for session cookies - replace with actual secret in prod
        POSTGRES_HOST="localhost",
        POSTGRES_PORT="5432",
        POSTGRES_DB="floskl",
        POSTGRES_USER="postgres",
        POSTGRES_PASSWORD="password"
    )

    # overrides
    if test_config is None:
        # Load all applicable environment variables, e.g. FLOSKL_POSTGRES_PASSWORD="s3cr3t"
        app.config.from_prefixed_env(prefix="FLOSKL")
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists (if/when needed)
    os.makedirs(app.instance_path, exist_ok=True)

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app
