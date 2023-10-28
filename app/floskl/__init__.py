# __init__.py serves double duty:
# 1. it will contain the application factory,
# 2. it tells Python that the floskl directory should be treated as a package.

import os

from flask import Flask

# Application Factory function
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # defaults
        SECRET_KEY="dev", # <-- used for session cookies - replace with something truly secret in production
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
