"""Website."""

from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from keys import APP_SECRET_KEY

# Enable debug and test environment
TEST_ENVIRONMENT_ENABLED = True
# Database location
DB_NAME = 'database_test.db'
# Premier League ID
LEAGUE_ID = 39
# The current active season
# Note: Only used as a fallback in case no active season is set in the database
ACTIVE_SEASON = '2025'
SEASON_DISPLAY_NAME = '2025-26'

db: SQLAlchemy = SQLAlchemy()

def create_app() -> Flask:
    """Create the app and initialize the database and login manager."""

    app = Flask(__name__)
    app.config['SECRET_KEY'] = APP_SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # pylint: disable=import-outside-toplevel
    # pylint: disable=cyclic-import
    from .views import views
    from .auth import auth
    from .admin import admin

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/admin')

    # pylint: disable=unused-import
    # Note: Import all defined models to allow create_all to function properly.
    from .models import User, Tip, Fixture, Team, TeamStanding, Result, General

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.endpoint_login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: int) -> User:
        # TODO: move to function in models.py
        return db.session.execute(db.select(User).filter_by(id=user_id)).scalar()

    @app.errorhandler(404)
    def not_found_error(_error) -> str:
        return render_template('404.html'), 404

    return app
