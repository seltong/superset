from superset.app import create_app

# Create the Superset app with APPLICATION_ROOT configuration
application = create_app()

# The APPLICATION_ROOT configuration in superset_config.py handles the URL prefix