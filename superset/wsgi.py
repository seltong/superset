from werkzeug.middleware.dispatcher import DispatcherMiddleware
from superset.app import create_app

# Create the original Superset app
app = create_app()

# This is the production WSGI callable with the prefix.
application = DispatcherMiddleware(
    app,
    {'/cop-analytics': app.wsgi_app},
)
