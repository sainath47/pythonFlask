# app/controllers/country_controller.py

from flask import request, jsonify
from app.models.otp_model import OTP
from app import db
from app.models.user_model import User
import random
# import bcrypt
# import datetime
# Import necessary modules and libraries



def forgotPasswordRequestOTP():
    try:
        # Extract data from the request
        data = request.get_json()
        email = data.get('email')

        # Check if email is provided
        if not email:
            response = {
                'status': 400,
                'message': 'Email is required.'
            }
            return jsonify(response), 400

        # Check if the user exists
        user = User.query.filter_by(email=email).first()
        if not user:
            response = {
                'status': 400,
                'message': 'User not registered, please sign up.'
            }
            return jsonify(response), 400

        # Generate a random 4-digit OTP
        otp = ''.join(random.choice('0123456789') for i in range(4))

        # TODO: Send the OTP to the user's email (implement this part based on your email setup)

        # Save the OTP and user ID in the OTP table
        otp_entry = OTP(user_id=user.id, otp=otp)
        db.session.add(otp_entry)
        db.session.commit()

        response = {
            'status': 200,
            'message': 'OTP sent successfully',
            'otp': otp
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def forgotPasswordVerifyOTP():
    try:
        # Extract data from the request
        data = request.get_json()
        email = data.get('email')
        otp = data.get('otp')

        # Check if email and OTP are provided
        if not email or not otp:
            response = {
                'status': 400,
                'message': 'Email and OTP are required.'
            }
            return jsonify(response), 400

        # Check if the OTP matches the stored OTP for the user
        user = User.query.filter_by(email=email).first()
        if not user:
            response = {
                'status': 400,
                'message': 'User not found.'
            }
            return jsonify(response), 400

        # Check if the OTP is valid
        otp_entry = OTP.query.filter_by(user_id=user.id, otp=otp).first()
        if not otp_entry:
            response = {
                'status': 400,
                'message': 'OTP verification failed.'
            }
            return jsonify(response), 400

        response = {
            'status': 200,
            'message': 'OTP verified successfully'
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500



# Import necessary modules and libraries


def forgotPasswordSetNewPassword():
    try:
        # Extract data from the request
        data = request.get_json()
        email = data.get('email')
        new_password = data.get('new_password')

        # Check if email and new password are provided
        if not email or not new_password:
            response = {
                'status': 400,
                'message': 'Email and new password are required.'
            }
            return jsonify(response), 400

        # Update the password in the user_details table
        user = User.query.filter_by(email=email).first()
        if not user:
            response = {
                'status': 400,
                'message': 'User not found.'
            }
            return jsonify(response), 400

        # Update the user's password
        user.password = new_password
        db.session.commit()

        response = {
            'status': 200,
            'message': 'Password reset successfully'
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500



