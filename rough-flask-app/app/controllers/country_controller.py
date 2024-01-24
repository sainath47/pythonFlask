# app/controllers/country_controller.py

from flask import request, jsonify
from app.models.country_model import Country



def get_all_countries():
    try:
        # Query all countries using the SQLAlchemy model
        countries = Country.query.all()

        # Convert the list of countries to a list of dictionaries
        country_list = [country.to_dict() for country in countries]

        return jsonify(country_list)


    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500