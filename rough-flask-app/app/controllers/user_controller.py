# app/controllers/user_controller.py

from flask import request, jsonify
from app.models.user_model import User
from app import db
import bcrypt
import datetime
import jwt

def create_user ():
    try:
        data = request.get_json()
        name = data['fullname']
        email = data['email']
        mobile = data['mobile']
        password = data['password']
        organisation = data.get('organisation', None)  # Use data.get to handle cases where 'organisation' is not present

        # Check if the user already exists by email
        existing_user_email = User.query.filter_by(email=email).first()

        # Check if the user already exists by mobile
        existing_user_mobile = User.query.filter_by(mobile=mobile).first()

        if existing_user_email or existing_user_mobile:
            result = {
                'status': 400,
                'Message': 'User already exists'
            }
        else:
            # Create a hashed password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # Create a new user instance
            new_user = User(fullname=name, email=email, mobile=mobile, password=hashed_password, organisation=organisation)

            # Add the new user to the database
            db.session.add(new_user)
            db.session.commit()

            result = {
                'status': 200,
                'Message': 'User data inserted successfully'
            }

        return jsonify(result)

    except Exception as e:
        # Log the error
        print(f"An error occurred while creating a user: {str(e)}")

        # Return a more informative error response
        return jsonify({
            'status': 500,
            'message': 'An error occurred while processing the request. Please try again later.'
        })


def login ():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']

        # Check if the user exists by email
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            # Generate a JWT token upon successful user validation
            payload = {
                'user_id': user.user_id,
                'email': email,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)  # Token expiration time
            }
            token = jwt.encode(payload, "PortfolioOne", algorithm='HS256')  # [1]->secret key

            result = {
                'status': 200,
                'data': {
                    'email': user.email,
                    'fullname': user.fullname,
                    'mobile': user.mobile,
                    'organisation': user.organisation,
                    'user_id': user.user_id
                },
                'Message': 'User found',
                'token': token
            }
        else:
            result = {
                'status': 404,
                'data': [],
                'Message': 'User not found'
            }

        return jsonify(result)

    except Exception as e:
        print(f"An error occurred while validating a user: {str(e)}")
        return jsonify({'error': str(e)}), 500