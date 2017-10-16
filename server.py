import os

from app import app


VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
if VCAP_APP_PORT is not None:
    port, debug = int(VCAP_APP_PORT), False
else:
    port, debug = 5000, True

VCAP_SERVICES = os.getenv('VCAP_SERVICES')
if VCAP_SERVICES is not None:
    app.config['dsn'] = get_elephantsql_dsn(VCAP_SERVICES)
else:
    app.config['dsn'] = """user='vagrant' password='vagrant'
                           host='localhost' port=5432 dbname='itucsdb'"""

app.run(host='0.0.0.0', port=port, debug=debug)
