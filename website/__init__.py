"""Website."""

import os

from datetime import datetime, timedelta
from flask import Flask, Response, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from sqlalchemy.pool import QueuePool
from typing import Any

# Database location, only used in dev environment
DB_NAME = 'database.db'
# Premier League ID
LEAGUE_ID = 39
# The current active season
# Note: Only used as a fallback in case no active season is set in the database
ACTIVE_SEASON = '2025'

db: SQLAlchemy = SQLAlchemy()
csrf: CSRFProtect = CSRFProtect()
migrate: Migrate = Migrate()

app_secret_key = os.environ.get('APP_SECRET_KEY', None)
api_secret_key = os.environ.get('API_SECRET_KEY', None)

def create_app() -> Flask:
    """Create the app and initialize the database and login manager."""

    # pylint: disable=unused-import
    # Note: Import all defined models to allow create_all to function properly.
    from .models import User, Tip, Fixture, Team, TeamStanding, Result, General, Season

    if not app_secret_key:
        raise RuntimeError("APP_SECRET_KEY is not set in environment")
    if not api_secret_key:
        raise RuntimeError("API_SECRET_KEY is not set in environment")

    app = Flask(__name__)
    app.config['SECRET_KEY'] = app_secret_key
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Enforce secure cookies and sane remember duration
    app.config.update({
        'SESSION_COOKIE_SECURE': True,
        'SESSION_COOKIE_HTTPONLY': True,
        'SESSION_COOKIE_SAMESITE': 'Lax',
        'REMEMBER_COOKIE_SECURE': True,
        'REMEMBER_COOKIE_HTTPONLY': True,
        'REMEMBER_COOKIE_DURATION': timedelta(days=7),
        'PERMANENT_SESSION_LIFETIME': timedelta(days=7)
    })

    app_database_url = os.environ.get('APP_DATABASE_URL', None)
    if app_database_url is not None:
        app.logger.info("Using remote database.")
        app.config['SQLALCHEMY_DATABASE_URI'] = app_database_url
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': 5,
            'max_overflow': 10,
            'pool_timeout': 30,
            'pool_recycle': 1800,
            'poolclass': QueuePool,
        }
    else:
        app.logger.info("Using local development database.")
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"

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

    login_manager = LoginManager()
    login_manager.login_view = 'auth.endpoint_login'
    login_manager.init_app(app)

    @app.context_processor
    def inject_context_data() -> dict[str, Any]:
        now = datetime.now()
        context = {
            'general': None,
            'season_data': None,
            'now': now
        }

        try:
            context['general'] = General.get()
            context['season_data'] = Season.get_season_data()
        except Exception as err:
            app.logger.exception(err)

        return context

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        return User.by_id(user_id)

    @app.errorhandler(404)
    def not_found_error(_error) -> Response:
        return render_template('not_found.html'), 404

    @app.after_request
    def set_security_headers(response: Response) -> Response:
        # Clickjacking, MIME sniffing, referrer, and CSP
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Content-Security-Policy'] = (
            # Fallback source
            "default-src 'self'; "
            # Script source
            "script-src 'self' 'unsafe-inline' "
            "https://cdnjs.cloudflare.com "
            "https://code.jquery.com "
            "https://cdn.jsdelivr.net "
            "https://kit.fontawesome.com "
            "https://ka-f.fontawesome.com; "
            # Style source
            "style-src 'self' 'unsafe-inline' "
            "https://cdnjs.cloudflare.com "
            "https://cdn.jsdelivr.net; "
            # Image source
            "img-src 'self' data: "
            "https://crests.football-data.org; "
            # Font source
            "font-src 'self' "
            "https://cdnjs.cloudflare.com "
            "https://cdn.jsdelivr.net "
            "https://ka-f.fontawesome.com "
            "https://use.fontawesome.com; "
            # Connection source
            "connect-src 'self' "
            "https://api.football-data.org "
            "https://ka-f.fontawesome.com; "
            # Plugin source
            "object-src 'none'; "
            # Embedded sites
            "frame-ancestors 'none'; "
            # <base> tag
            "base-uri 'none'; "
        )
        return response

    return app
