"""Auth."""

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login() -> str:
    """The log in page for the website. Check if the user is already logged in, otherwise check the
    user login credentials."""

    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.by_username(username)

        if not user:
            flash("Användarnamnet existerar inte", category='error')
        elif not check_password_hash(user.password, password):
            flash("Ogiltigt lösenord", category='error')
        elif not login_user(user, remember=True):
            flash("Något gick fel vid inloggning", category='error')
        else:
            flash("Inloggad!", category='success')
            return redirect(url_for('views.home'))

    return render_template('login.html', user=None)

@auth.route('/logout')
@login_required
def logout() -> str:
    """Log out the user and redirect to the log in page."""

    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/signup', methods=['GET', 'POST'])
def signup() -> str:
    """The sign up page for the website. Check if the user is already logged in, otherwise check the
    user login credentials."""

    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password_repeat = request.form.get('repeatPassword')
        user = User.by_username(username)

        if user:
            flash("Användarnamnet är taget", category='error')
        elif len(username) == 0:
            flash("Ogiltigt användarnamn", category='error')
        elif len(password) < 5:
            flash("Lösenordet måste vara minst 5 tecken", category='error')
        elif password != password_repeat:
            flash("Lösenorden stämmer inte överens", category='error')
        else:
            new_user = User.create(username, generate_password_hash(password, method='scrypt'))
            login_user(new_user, remember=True)
            flash("Konto skapat!", category='success')
            return redirect(url_for('views.home'))

    return render_template('signup.html', user=None)
