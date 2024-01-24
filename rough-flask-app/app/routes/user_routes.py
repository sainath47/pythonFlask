# app/routes/user_routes.py

from flask import Blueprint
from app.controllers.user_controller import create_user ,login 

user_routes = Blueprint('user_routes', __name__)

user_routes.route('/create_user', methods=['POST'])(create_user)
user_routes.route('/login', methods=['POST'])(login )