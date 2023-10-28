""" Configuration for Gunicorn
For details, see: https://docs.gunicorn.org/en/stable/configure.html#configuration-file
"""
# pylint: skip-file

workers = 2
wsgi_app = 'floskl:create_app()'
bind = '0.0.0.0:8080'
