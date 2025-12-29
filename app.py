"""Main."""

import os
import requests

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from waitress import serve
from website import create_app

APP_URL = os.environ.get('APP_URL', None)
IS_PRODUCTION = os.environ.get('FLASK_ENV', None) == 'production'
IS_CHILD_PROCESS = os.environ.get('WERKZEUG_RUN_MAIN', None) == 'true'

app: Flask = create_app()

def keep_alive() -> None:
    try:
        app.logger.info(f"Keep alive triggered on: {APP_URL}")
        requests.get(APP_URL)
    except Exception as err:
        app.logger.error(f"Keep alive failed on {APP_URL}:", err)

if APP_URL:
    if (IS_PRODUCTION or IS_CHILD_PROCESS):
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=keep_alive, trigger='interval', minutes=10)
        scheduler.start()
        app.logger.info("Keep alive enabled.")
    elif IS_PRODUCTION:
        app.logger.info("Keep alive not enabled.")
else:
    app.logger.info("No APP_URL environment variable provided, keep alive is not enabled.")

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)
