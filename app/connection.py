import psycopg2 as dbapi2

from flask import g
from flask import current_app as app

def get_connection():
    if not hasattr(g, 'connection'):
        g.connection = dbapi2.connect(app.config['dsn'])
    return g.connection
