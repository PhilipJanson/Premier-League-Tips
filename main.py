"""Main."""

from flask import Flask
from website import create_app, TEST_ENVIRONMENT_ENABLED

app: Flask = create_app()

if __name__ == "__main__":
    app.run(debug=TEST_ENVIRONMENT_ENABLED)
