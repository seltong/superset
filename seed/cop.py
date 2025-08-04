import os
import json
from urllib.parse import quote_plus
from superset import create_app, db

app = create_app()

with app.app_context():
    from flask_appbuilder.security.sqla.models import User
    from superset.models.core import Database
    from superset.models.dashboard import Dashboard
    from superset.models.embedded_dashboard import EmbeddedDashboard
    from sqlalchemy.orm.exc import NoResultFound

    admin = db.session.query(User).filter_by(username="admin").one()

    try:
        dashboard = db.session.query(Dashboard).filter_by(slug="finops").one()
        print("Dashboard 'FinOps' already exists, skipping creation.")
    except NoResultFound:
        print("Dashboard 'FinOps' does not exist. Starting creation...")
        dashboard = Dashboard(
            dashboard_title="FinOps",
            slug="finops",
            owners=[admin],
            published=True,
            json_metadata=json.dumps({"dashboard_embeddable": True}),
        )
        db.session.add(dashboard)
        db.session.commit()
        print("Dashboard 'FinOps' has been created.")

        existing_embed = (
            db.session.query(EmbeddedDashboard)
            .filter_by(dashboard_id=dashboard.id)
            .one_or_none()
        )

        if existing_embed:
            print(f"Embedded config already exists for dashboard {dashboard.id}.")
        else:
            print(f"Creating embedded config for dashboard {dashboard.id}...")
            embed = EmbeddedDashboard(
                dashboard_id=dashboard.id,
                uuid=None,
                allow_domain_list=None,
            )

            db.session.add(embed)
            db.session.commit()
            print("Embedded config has been created.")

    db_conn = db.session.query(Database).filter_by(database_name="cop_tables_connection").first()
    if db_conn:
        print("Database connection 'cop_tables_connection' already exists, skipping creation.")
    else:
        print("Creating database connection 'cop_tables_connection'...")

        user = quote_plus(os.environ.get('COP_TABLES_DATABASE_USER') or os.environ['DATABASE_USER'])
        password = quote_plus(os.environ.get('COP_TABLES_DATABASE_PASSWORD') or os.environ['DATABASE_PASSWORD'])
        host = os.environ.get('COP_TABLES_DATABASE_HOST') or os.environ['DATABASE_HOST']
        port = os.environ.get('COP_TABLES_DATABASE_PORT') or os.environ['DATABASE_PORT']
        dbname = os.environ.get('COP_TABLES_DATABASE_NAME') or 'tables'

        sqlalchemy_uri = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
        
        new_db = Database(
            database_name="cop_tables_connection",
             sqlalchemy_uri=sqlalchemy_uri,
            extra=json.dumps({
                "metadata_params": {},
                "engine_params": {},
                "schemas_allowed_for_csv_upload": [],
                "expose_in_sqllab": True,
                "allow_ctas": True,
                "allow_cvas": True,
                "allow_dml": True,
                "allow_run_async": True
            }),
        )
        db.session.add(new_db)
        db.session.commit()
        print("Database connection 'cop_tables_connection' has been created.")