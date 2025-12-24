from flask import (
    Blueprint,
    Response,
    abort,
    render_template,
    flash, redirect,
    url_for,
    jsonify,
    request
)
from flask_login import login_required, current_user
from .models import User, Season, Team
from . import db

user = Blueprint('user', __name__)
current_user: User

@user.route('/<user_id>')
@login_required
def endpoint_user(user_id: str) -> str:
    """User page."""

    if not current_user.id == user_id:
        flash("Du är ej behörig att visa denna sida.", category='error')
        return redirect(url_for('views.endpoint_home'))

    kwargs = {
        'season_data': Season.get_season_data(),
        'user': current_user,
        'teams': Team.all()
    }
    return render_template('user.html', **kwargs)

@user.route('/<user_id>/set-favorite-team', methods=['POST'])
@login_required
def endpoint_set_favorite_team(user_id: str) -> Response:
    """Set the favorite team for a user."""

    if not current_user.id == user_id:
        flash("Du är ej behörig att visa denna sida.", category='error')
        return redirect(url_for('views.endpoint_home'))

    if not request.is_json:
        abort(415)
    data = request.get_json()

    try:
        team_id = str(data.get('teamId')).strip()
    except (TypeError, ValueError):
        abort(400)

    team = Team.by_id(team_id)
    if team is None:
        flash(f"Could not find team with id {team_id} in database.", category='error')
        abort(404)

    current_user.favorite_team = team
    db.session.commit()
    flash(f"{team.name} är nu ditt favoritlag.", category='success')

    return jsonify({}), 200

@user.route('/user_id/set-email', methods=['POST'])
@login_required
def endpoint_set_email(user_id: str) -> Response:
    """Set the email for a user."""

    if not current_user.id == user_id:
        flash("Du är ej behörig att visa denna sida.", category='error')
        return redirect(url_for('views.endpoint_home'))

    return jsonify({}), 200

@user.route('/<user_id>/change-password')
@login_required
def endpoint_change_password(user_id: str) -> str:
    """Change the password for a user."""

    if not current_user.id == user_id:
        flash("Du är ej behörig att visa denna sida.", category='error')
        return redirect(url_for('views.endpoint_home'))

    kwargs = {
        'season_data': Season.get_season_data(),
        'user': current_user,
    }
    return render_template('change_password.html', **kwargs)
