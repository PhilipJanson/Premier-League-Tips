# Premier-League-Tips

Website written in Python powered by Flask and api-sports.io to display Premier League fixtures and
to place simple bets on them.

## Installation

Dependencies are specified in [`requirements.txt`](./requirements.txt).

Example setup (Windows PowerShell):

```ps
# Create and activate virtual environment
pip install virtualenv
virtualenv --python <PATH_TO_PYTHON_EXE> .venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Environment variables
Setup a `.env` file to provide the correct settings for the app.
```
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
APP_SECRET_KEY=<flask_secret_key>
API_SECRET_KEY=<api_secret_key>
APP_DATABASE_URL=<database_url> # Only needed if using remote db.
APP_URL=<url> # Onlt needed for keep alive functionality.
```

## Database
Setup and migrate database changes
```ps
# Initialize database
python -m flask db init
# Migrate new database model changes
python -m flask db migrate -m "<message>"
# Upgrade
python -m flask db upgrade
```

## Set user as admin
```ps
python -m scripts.set_user_admin <user-uuid>
# Add revoke flag to unset them as admin
python -m scripts.set_user_admin <user-uuid> --revoke
```

## Run app
```ps
python -m flask run
```

## Linting
Linting rules specified in [`.pylintrc`](./.pylintrc).
```ps
pylint ${PWD}
```

## Links
- [API Football](https://dashboard.api-football.com/)
