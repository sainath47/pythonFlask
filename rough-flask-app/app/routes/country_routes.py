# app/routes/country_routes.py

from flask import Blueprint
from app.controllers.country_controller import  get_all_countries

country_routes = Blueprint('country_routes', __name__)

country_routes.route('/', methods=['GET'])(get_all_countries)



