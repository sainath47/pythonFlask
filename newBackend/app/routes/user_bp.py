# app/routes/user.py

from flask import Blueprint, render_template

user_bp = Blueprint('user', __name__)

@user_bp.route('/')
def list_users():

    # Retrieve user data from the database using your user model
    # Replace this with actual data retrieval code
    # users = User.query.all()

    return render_template('user/list.html')

@user_bp.route('/<int:user_id>')
def view_user(user_id):
    # Retrieve user data from the database using your user model
    # Replace this with actual data retrieval code
    # user = User.query.get(user_id)

    return render_template('user/detail.html')
