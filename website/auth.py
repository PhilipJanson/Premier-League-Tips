"""Auth."""

from flask import Blueprint, Response, render_template, flash, redirect, url_for, request
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from .utils import ValidationError, check_username_rules, check_password_rules
from . import db

auth = Blueprint('auth', __name__)
current_user: User

@auth.route('/login', methods=['GET', 'POST'])
def endpoint_login() -> Response:
    """The log in page for the website. Check if the user is already logged in, otherwise check the
    user login credentials."""

    if current_user.is_authenticated:
        return redirect(url_for('views.endpoint_home'))
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        remember_me = request.form.get('remember-me', False)
        user = User.by_username(username)

        if not user or not check_password_hash(user.password, password):
            # Display a generic message to not leak security information.
            flash("Fel användarnamn eller lösenord.", category='error')
        elif not login_user(user, remember=remember_me):
            flash("Något gick fel vid inloggning.", category='error')
        else:
            flash("Inloggad!", category='success')
            return redirect(url_for('views.endpoint_home'))

    return render_template('login.html', user=None)

@auth.route('/logout')
@login_required
def endpoint_logout() -> Response:
    """Log out the user and redirect to the log in page."""

    logout_user()
    return redirect(url_for('auth.endpoint_login'))

@auth.route('/signup', methods=['GET', 'POST'])
def endpoint_signup() -> Response:
    """The sign up page for the website. Check if the user is already logged in, otherwise check the
    user login credentials."""

    if current_user.is_authenticated:
        return redirect(url_for('views.endpoint_home'))
    if request.method == 'POST':
        try:
            username = request.form.get('username').strip()
            password = request.form.get('password').strip()
            password_repeat = request.form.get('password-repeat').strip()
            remember_me = request.form.get('remember-me', False)
            user = User.by_username(username)

            if user:
                raise ValidationError("Användarnamnet är redan taget.")

            # Raises ValidationError on failure
            check_username_rules(username)
            check_password_rules(password)

            if password != password_repeat:
                raise ValidationError("Lösenorden stämmer inte överens.")

            new_user = User.create(username, generate_password_hash(password))
            db.session.commit()
            login_user(new_user, remember=remember_me)
            flash("Konto skapat!", category='success')
            return redirect(url_for('views.endpoint_home'))
        except ValidationError as err:
            flash(err.message, category='error')

    return render_template('signup.html', user=None)
