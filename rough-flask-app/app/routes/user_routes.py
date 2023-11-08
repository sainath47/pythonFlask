# app/routes/user_routes.py

from flask import Blueprint
from app.controllers.user_controller import create_user_route, list_users_route

user_routes = Blueprint('user_routes', __name__)

user_routes.route('/create_user', methods=['POST'])(create_user_route)
user_routes.route('/list_users', methods=['GET'])(list_users_route)
