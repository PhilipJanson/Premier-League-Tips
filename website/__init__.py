"""Website."""

import os

from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

# Database location
DB_NAME = 'database_test.db'
# Premier League ID
LEAGUE_ID = 39
# The current active season
# Note: Only used as a fallback in case no active season is set in the database
ACTIVE_SEASON = '2025'

db: SQLAlchemy = SQLAlchemy()
csrf: CSRFProtect = CSRFProtect()
migrate: Migrate = Migrate()

app_secret_key = os.environ.get('APP_SECRET_KEY')
api_secret_key = os.environ.get('API_SECRET_KEY')

def create_app() -> Flask:
    """Create the app and initialize the database and login manager."""

    # pylint: disable=unused-import
    # Note: Import all defined models to allow create_all to function properly.
    from .models import User, Tip, Fixture, Team, TeamStanding, Result, General, Season

    if app_secret_key is None:
        raise RuntimeError("APP_SECRET_KEY is not set in environment")
    if api_secret_key is None:
        raise RuntimeError("API_SECRET_KEY is not set in environment")

    app = Flask(__name__)
    app.config['SECRET_KEY'] = app_secret_key
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DATABASE_TEST'] = False
    db.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    # pylint: disable=import-outside-toplevel
    # pylint: disable=cyclic-import
    from .views import views
    from .auth import auth
    from .admin import admin
    from .user import user

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(user, url_prefix='/user')

    with app.app_context():
        if app.config.get('DATABASE_TEST', False):
            db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.endpoint_login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        # TODO: move to function in models.py
        return db.session.execute(db.select(User).filter_by(id=user_id)).scalar()

    @app.errorhandler(404)
    def not_found_error(_error) -> str:
        return render_template('404.html'), 404

    return app
