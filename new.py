from flask import request, json, jsonify, Flask, g
import mysql.connector
from flask_mail import Mail, Message
from twilio.rest import Client
import random
import datetime
import jwt
from functools import wraps
import bcrypt

app = Flask(__name__)

# Database configuration
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'sai123',
    'db': 'dfx'
}


# db_config = {
#     'host': 'api.portfolioone.io',
#     'port': 3306,
#     'user': 'portfolio',
#     'password': 'PortfolioOne!@#',
#     'db': 'dfx'
# }


# Create a connection to the database
connection = mysql.connector.connect(**db_config)

# Decorator for token authentication
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')  # Get the token from the request header

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            # Verify and decode the token
            data = jwt.decode(token.split(' ')[1], "PortfolioOne", algorithms=['HS256'])
            # Optionally, you can add user information from the token to the request context for later use
            g.user = data
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        return f(*args, **kwargs)

    return decorated

@app.route('/RegisterUser', methods=['POST'])
def RegisterUser():
    try:
        data = request.get_json()
        name = data['fullname']
        email = data['email']
        mobile = data['mobile']
        password = data['password']  # Plain text password
        organisation = data['organisation']

        # Create a salt and hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        if connection is None:
            result = {
                'status': 500,
                'Message': 'Failed to connect to the database'
            }
            return jsonify(result)

        query = "SELECT * FROM user_details WHERE email=%s OR mobile=%s"
        cursor = connection.cursor(dictionary=True)  # Create a new cursor
        cursor.execute(query, (email, mobile))
        existing_user = cursor.fetchone()

        if existing_user:
            result = {
                'status': 500,
                'Message': 'User already exists with the given email or phone no.'
            }
        else:
            insert_query = "INSERT INTO user_details (fullname, email, mobile, password, organisation) VALUES (%s, %s, %s, %s, %s)"
            insert_data = (name, email, mobile, hashed_password, organisation)  # Store the hashed password
            cursor.execute(insert_query, insert_data)
            connection.commit()

            result = {
                'status': 200,
                'Message': 'User data inserted successfully'
            }

    except Exception as e:
        result = {
            'status': 500,
            'Message': str(e)
        }
    finally:
        cursor.close()
        # Do not close the connection here

    return jsonify(result)

@app.route('/validateUser', methods=['POST'])
def validateUser():
    try:
        data = request.get_json()
        username = data['email']
        password = data['password']

        cursor = connection.cursor(dictionary=True)

        query = "SELECT user_id, fullname, mobile, organisation, password FROM user_details WHERE email = %s"
        cursor.execute(query, (username,))
        user_data = cursor.fetchone()

        if user_data:
            stored_password = user_data['password']

            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                payload = {
                    'user_id': user_data['user_id'],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
                }
                token = jwt.encode(payload, "YourSecretKey", algorithm='HS256')

                result = {
                    'status': 200,
                    'data': user_data,
                    'Message': 'User found',
                    'token': token
                }
            else:
                result = {
                    'status': 401,
                    'data': [],
                    'Message': 'Invalid password'
                }
        else:
            result = {
                'status': 404,
                'data': [],
                'Message': 'User not found'
            }

    except Exception as e:
        result = {
            'status': 500,
            'Message': str(e)
        } 
    finally:
            cursor.close()

    return jsonify(result)

#######################################################################################
# Basic route for testing
@app.route('/', methods=['GET'])
def getRough():
    try:
        # Return a response
        result = {
            'status': 200,  # Use 200 for a successful response
            'Message': 'Application at 5000 port'  # Update the message
        }
        return jsonify(result)

    except Exception as e:
        # If an exception occurs, return an error response
        result = {
            'status': 500,  # Use 500 for an internal server error
            'Message': str(e)  # Include the error message in the response
        }
        return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
