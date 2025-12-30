import os

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from website import create_app
from website import db

def clear_database() -> None:
	if (os.environ.get('APP_DATABASE_URL', None)) or \
	   (os.environ.get('FLASK_ENV', None) != 'development'):
		print("Database could be set to production, terminating.")
		return

	confirm = input("Type confirm to continue: ")
	if confirm.strip() != 'confirm':
		return

	app = create_app()

	with app.app_context():
		db.drop_all()
		db.create_all()

if __name__ == '__main__':
	clear_database()
