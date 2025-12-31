import argparse
import os

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from website import create_app
from website import db
from website.models import User

parser = argparse.ArgumentParser(description='Set or revoke admin status for a user by UUID')
parser.add_argument('user_id', help='UUID of the user')
parser.add_argument('--revoke',
					action='store_true',
					help='Revoke admin status instead of setting it')
args = parser.parse_args()

def set_user_admin() -> None:
	app = create_app()

	with app.app_context():
		user = User.by_id(args.user_id)
		if user is None:
			print(f"User not found: {args.user_id}")
			return

		user.is_admin = not args.revoke
		db.session.commit()
		status = 'admin' if user.is_admin else 'non-admin'
		print(f"Updated user {user.username} ({user.id}) -> {status}")

if __name__ == '__main__':
	set_user_admin()
