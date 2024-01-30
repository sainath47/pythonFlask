# coding: cp1252
from flask import request, json, jsonify, Flask,g, send_file
# import pandas as pd
# from sqlalchemy import create_engine,text
# from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import mysql.connector
from flask_mail import Mail, Message
# from twilio.rest import Client
import random
import datetime
import jwt
from functools import wraps
import traceback 
import pandas as pd
import uuid
import os
from mysql.connector import Error







# from logger import logging

# logger = logging.getLogger()

app = Flask(__name__)
CORS(app)

db_config = {
    'host': 'api.portfolioone.io',
    'port': 3306,
    'user': 'portfolio',
    'password': 'PortfolioOne123',
    'db': 'dfx'
}

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587  # Use 587 for TLS or 465 for SSL
app.config['MAIL_USE_TLS'] = True  # Enable TLS
app.config['MAIL_USE_SSL'] = False  # Disable SSL
app.config['MAIL_USERNAME'] = 'no-reply@portfolioone.io'
app.config['MAIL_PASSWORD'] = 'Kox02665'
app.config['MAIL_DEFAULT_SENDER'] = 'no-reply@portfolioone.io'

mail = Mail(app)

# app.config['MAIL_DEBUG'] = True

# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 465  # Use the appropriate port (587 for TLS)
# app.config['MAIL_USE_TLS'] = False
# app.config['MAIL_USE_SSL'] = True   
# app.config['MAIL_USERNAME'] = 'reddysainath47@gmail.com'
# app.config['MAIL_PASSWORD'] = 'jxyhiqscawrnbntw'  # Replace with your email password
# app.config['MAIL_DEFAULT_SENDER'] = 'reddysainath47@gmail.com'





# Define a decorator for token authentication
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

@app.route('/api/lease_template')
def download_file():
    # Get the absolute path of the directory containing the Flask app
    app_root = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the Excel file in the same directory as the app
    file_path = os.path.join(app_root, 'lease_template.xlsx')

    # Provide a filename for the downloaded file
    filename = 'lease_template.xlsx'

    return send_file(file_path, as_attachment=True, download_name=filename)


@app.route('/api/countries', methods=['GET'])
def get_all_countries():
    try:
        # Establish a connection to the MySQL database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Execute a query to fetch all countries
        cursor.execute("SELECT * FROM countries")

        # Fetch all rows and convert to a list of dictionaries
        countries = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        return jsonify(countries)

    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500


@app.route('/api/getAllLeaseData', methods=['GET'])
@token_required
def getAllLeaseData():
    try:
        connection = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['db']
        )
        cursor = connection.cursor(dictionary=True)
        

        query = "SELECT * FROM lease_data ORDER BY updated_at DESC"
        cursor.execute(query)

        data_list = cursor.fetchall()


        if len(data_list) == 0:
            result = {
                'status': 200,
                'data': [],
                'Message': 'Request Submitted Successfully',
                'count': 0,
            }
        else:
            last_updated_date = data_list[0]['updated_at']  # Access the 'updated_at' key in the dictionary

            result = {
                'status': 200,
                'data': data_list,
                'Message': 'Request Submitted Successfully',
                'count': len(data_list),
                'last_updated_date': last_updated_date,
            }

        return jsonify(result)

    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/getAllLeaseDataByUser/<string:id>', methods=['GET'])
@token_required
def getAllLeaseData_by_id(id):
    connection = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['db']
        )
    try:
      
        auth_header = request.headers.get('Authorization')
      # Get the token by removing 'Bearer ' from the header
        token = auth_header.split(' ')[1]
        
        # Assuming `token` holds the JWT token you received or retrieved
        decoded_token = jwt.decode(token, "PortfolioOne", algorithms=['HS256'])

        # Access the 'user_id' from the decoded token
        user_id = decoded_token.get('user_id')
      
        cursor = connection.cursor(dictionary=True)
        # SQL query to fetch data based on the provided ID
        query = f"SELECT * FROM lease_data WHERE user_id = '{user_id}' ORDER BY updated_at DESC"
        # Use pandas to read data into a DataFrame
        cursor.execute(query)
        # Convert the DataFrame to a list of dictionaries
        data_list = cursor.fetchall()
        cursor.close()
        connection.close()
        if len(data_list) == 0:
            result = {
                'status': 200,
                'data': [],
                'Message': 'Request Submitted Successfully',
                'count': 0,
            }
        else:
            last_updated_date = data_list[0]['updated_at']  # Access the 'updated_at' key in the dictionary

            result = {
                'status': 200,
                'data': data_list,
                'Message': 'Request Submitted Successfully',
                'count': len(data_list),
                'last_updated_date': last_updated_date,
            }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500




@app.route('/api/validateUser', methods=['POST'])
def validateUser():
    connection = mysql.connector.connect(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['db']
    )
    try:
        cursor = connection.cursor(dictionary=True)
        data = request.get_json()
        username = data['email']
        password = data['password']

        # SQL query to fetch data based on the provided email
        query = f"SELECT email, fullname, mobile, organisation, user_id, is_email_verified FROM user_details WHERE email = '{username}' AND BINARY password = '{password}'"
        cursor.execute(query)
        user_data = cursor.fetchone()

        if user_data is None:
            result = {
                'status': 404,
                'data': {},
                'Message': 'User not found'
            }
            return jsonify(result)

        if not user_data['is_email_verified']:
            result = {
                'status': 403,
                'Message': 'Please verify your email before logging in'
            }
            return jsonify(result)

        # Check if the user is present in the subscriptions table
        subscription_query = f"SELECT * FROM subscriptions WHERE user_id = '{user_data['user_id']}'"
        cursor.execute(subscription_query)
        subscription_data = cursor.fetchone()

        if subscription_data:
            # Check if the subscription has expired
            end_date = subscription_data['end_date']
            current_date = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            
            if end_date and end_date < datetime.datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S'):
                result = {
                    'status': 200,
                    'data': {
                        'email': user_data['email'],
                        'fullname': user_data['fullname'],
                        'mobile': user_data['mobile'],
                        'organisation': user_data['organisation'],
                        'user_id': user_data['user_id'],
                        'is_email_verified': user_data['is_email_verified'],
                        'subscribed': False
                    },
                    # 'Message': 'User subscription has expired'
                    "Message": "User found",
                }
            elif not end_date:
                result = {
                    'status': 200,
                    'data': {
                        'email': user_data['email'],
                        'fullname': user_data['fullname'],
                        'mobile': user_data['mobile'],
                        'organisation': user_data['organisation'],
                        'user_id': user_data['user_id'],
                        'is_email_verified': user_data['is_email_verified'],
                        'subscribed': False
                    },
                    # 'Message': 'User just clicked on button of pypal subscription, never completed the payment'
                    "Message": "User found",
                }
              
            else:
                result = {
                    'status': 200,
                    'data': {
                        'email': user_data['email'],
                        'fullname': user_data['fullname'],
                        'mobile': user_data['mobile'],
                        'organisation': user_data['organisation'],
                        'user_id': user_data['user_id'],
                        'is_email_verified': user_data['is_email_verified'],
                        'subscribed': True
                    },
                    # 'Message': 'User is a subscriber'
                    "Message": "User found",
                }
        else:
            # User is not a subscriber, provide additional information
            # For example, no. of sq feet, count of docs, and no. of days since registration
            # Fetch the additional info from lease_data table
            lease_data_query = f"SELECT COUNT(*) as doc_count, SUM(rentable_sf) as sq_feet FROM lease_data WHERE user_id = '{user_data['user_id']}'"
            cursor.execute(lease_data_query)
            lease_data = cursor.fetchone()

            # Fetch registration date
            registration_date_query = f"SELECT created_at FROM user_details WHERE user_id = '{user_data['user_id']}'"
            cursor.execute(registration_date_query)
            registration_date = cursor.fetchone()['created_at']

            result = {
                'status': 200,
                'data': {
                    'email': user_data['email'],
                    'fullname': user_data['fullname'],
                    'mobile': user_data['mobile'],
                    'organisation': user_data['organisation'],
                    'user_id': user_data['user_id'],
                    'sq_feet': lease_data['sq_feet'],
                    'count_docs': lease_data['doc_count'],
                    'registration_date': registration_date,
                    'is_email_verified': user_data['is_email_verified'],
                    'subscribed': False
                },
                # 'Message': 'User is not a subscriber',
                "Message": "User found",
            }

        # Generate a JWT token upon successful user validation
        payload = {
            'username': username,  # username is the user's email
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30),  # Token expiration time
            'user_id': user_data['user_id']
        }
        token = jwt.encode(payload, "PortfolioOne", algorithm='HS256')

        result['token'] = token

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()





@app.route('/api/RegisterUser', methods=['POST'])
def RegisterUser():
    connection = None
    cursor = None  # Initialize cursor to None

    try:
        data = request.get_json()

        name = data['fullname']
        email = data['email']
        mobile = data['mobile']
        password = data['password']  # Plain text password
        organisation = data['organisation']

        # Create a database connection
        connection = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['db']
        )

        if connection is None:
            result = {
                'status': 500,
                'Message': 'Failed to connect to the database'
            }
            return jsonify(result)

        cursor = connection.cursor(dictionary=True)
        # Check if there's an unverified document for the email and delete it
        delete_query = "DELETE FROM user_details WHERE email = %s AND is_email_verified = FALSE"
        cursor.execute(delete_query, (email,))
        connection.commit()

        # Check if the user already exists by email
        query_email = "SELECT * FROM user_details WHERE email=%s"
        cursor.execute(query_email, (email,))
        existing_user_email = cursor.fetchone()

        # Check if the user already exists by mobile
        query_mobile = "SELECT * FROM user_details WHERE mobile=%s"
        cursor.execute(query_mobile, (mobile,))
        existing_user_mobile = cursor.fetchone()

        if existing_user_email or existing_user_mobile:
            result = {
                'status': 400,
                'Message': 'User already exists with the same email or mobile no.'
            }
        else:
            # Create a salt and hash the password
            # salt = bcrypt.gensalt()
            # hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

            insert_query = "INSERT INTO user_details (fullname, email, mobile, password, organisation) VALUES (%s, %s, %s, %s, %s)"
            insert_data = (name, email, mobile, password, organisation)  # Store the hashed password
            cursor.execute(insert_query, insert_data)
                    # Get the user_id of the newly inserted user
            user_id = cursor.lastrowid

            # Insert into user_headcount with default values
            insert_headcount_query = "INSERT INTO user_headcount (user_id) VALUES (%s)"
            cursor.execute(insert_headcount_query, (user_id,))


            connection.commit()
            
            # Generate token with no expiry containing the email for email verification
            payload = {
                'email': email
            }
            token = jwt.encode(payload, "EmailVerificationSecret", algorithm='HS256')

            # Construct the link with the token for email verification
            verification_link = f"https://portfolioone.io/verify_email?token={token}"
            
            # Send email with the verification link
            # Use your email sending functionality here (code to send an email)
            # Example using Flask-Mail:
            message = Message(subject='Email Verification Link', recipients=[email])
            # message.body = f"Click on the link to verify your email: {verification_link}"
            # return jsonify({'name':name})
            message.html = f'''
            <!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Document</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;700&display=swap"
      rel="stylesheet"
    />
    <style>
.logo {{
  max-width: 80%;
}}
.greet {{
  font-size: 52px;
  line-height: normal;
}}
.main-content {{
  font-size: 24px;
}}
h2 {{
  font-size: 42.21px;
}}

.app-advt > p {{
  font-size: 24px;
}}
.app-advt {{
  padding: 40px 0;
}}
/* Media query for mobile devices */
@media screen and (max-width: 480px) {{
  .logo {{
    max-width: 60%;
  }}
  .greet {{
    font-size: 24px;
    line-height: 24px;
  }}
  .main-content {{
    font-size: 18px;
    padding: 0 20px;
  }}
  h2 {{
    font-size: 29.21px;
  }}
  .app-advt > p {{
    font-size: 20px;
  }}
  .app-advt {{
    padding: 40px 20px;
  }}
}}
    </style>
  </head>

  <body
    style="
      text-align: center;

      background-color: #eaf0f3;
      font-family: 'Barlow', serif;
      margin: 100px 0;
    "
  >
    <div class="mail" style="text-align: center">
      <header>
        <div class="header" style="padding-bottom: 55px; margin: auto">
          <img
            class="logo"
            src="data:image/svg+xml;base64,%0APHN2ZwpjbGFzcz0ibG9nbyIKd2lkdGg9IjQ2NCIKaGVpZ2h0PSI2MCIKdmlld0JveD0iMCAwIDQ2NCA2MCIKZmlsbD0ibm9uZSIKeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgo+CjxwYXRoCiAgZD0iTTAgNTUuNjUxNlYzLjAwNzVIMjAuNzY5OUMyNC43NjI3IDMuMDA3NSAyOC4xNjQzIDMuNzcwMDkgMzAuOTc0OCA1LjI5NTI1QzMzLjc4NTEgNi44MDMyOSAzNS45MjcyIDguOTAyNTUgMzcuNDAxIDExLjU5MzFDMzguODkxOSAxNC4yNjYzIDM5LjYzNzUgMTcuMzUwOSAzOS42Mzc1IDIwLjg0NjlDMzkuNjM3NSAyNC4zNDI3IDM4Ljg4MzUgMjcuNDI3NSAzNy4zNzU0IDMwLjEwMDdDMzUuODY3NCAzMi43NzQxIDMzLjY4MjMgMzQuODU2MiAzMC44MjA0IDM2LjM0NzFDMjcuOTc1OSAzNy44MzggMjQuNTMxMyAzOC41ODMzIDIwLjQ4NzEgMzguNTgzM0g3LjI0ODg2VjI5LjY2MzdIMTguNjg3N0MyMC44Mjk3IDI5LjY2MzcgMjIuNTk1IDI5LjI5NTMgMjMuOTgyOCAyOC41NTg0QzI1LjM4ODEgMjcuODA0NCAyNi40MzM2IDI2Ljc2NzYgMjcuMTE5MSAyNS40NDhDMjcuODIxNSAyNC4xMTE1IDI4LjE3MjggMjIuNTc3NyAyOC4xNzI4IDIwLjg0NjlDMjguMTcyOCAxOS4wOTkgMjcuODIxNSAxNy41NzM2IDI3LjExOTEgMTYuMjcxNEMyNi40MzM2IDE0Ljk1MTggMjUuMzg4MSAxMy45MzIxIDIzLjk4MjggMTMuMjEyNEMyMi41Nzc4IDEyLjQ3NTUgMjAuNzk1NSAxMi4xMDcxIDE4LjYzNjMgMTIuMTA3MUgxMS4xMzAzVjU1LjY1MTZIMFpNNjMuODY0NSA1Ni40MjI4QzU5Ljg3MTcgNTYuNDIyOCA1Ni40MTg3IDU1LjU3NDQgNTMuNTA1NCA1My44Nzc5QzUwLjYwOTIgNTIuMTY0MyA0OC4zNzI4IDQ5Ljc4MjQgNDYuNzk2MiA0Ni43MzJDNDUuMjE5NiA0My42NjQ2IDQ0LjQzMTQgNDAuMTA4NSA0NC40MzE0IDM2LjA2NDNDNDQuNDMxNCAzMS45ODU5IDQ1LjIxOTYgMjguNDIxMyA0Ni43OTYyIDI1LjM3MUM0OC4zNzI4IDIyLjMwMzYgNTAuNjA5MiAxOS45MjE2IDUzLjUwNTQgMTguMjI0OUM1Ni40MTg3IDE2LjUxMTIgNTkuODcxNyAxNS42NTQ0IDYzLjg2NDUgMTUuNjU0NEM2Ny44NTczIDE1LjY1NDQgNzEuMzAxOSAxNi41MTEyIDc0LjE5ODEgMTguMjI0OUM3Ny4xMTE0IDE5LjkyMTYgNzkuMzU2MyAyMi4zMDM2IDgwLjkzMjkgMjUuMzcxQzgyLjUwOTQgMjguNDIxMyA4My4yOTc3IDMxLjk4NTkgODMuMjk3NyAzNi4wNjQzQzgzLjI5NzcgNDAuMTA4NSA4Mi41MDk0IDQzLjY2NDYgODAuOTMyOSA0Ni43MzJDNzkuMzU2MyA0OS43ODI0IDc3LjExMTQgNTIuMTY0MyA3NC4xOTgxIDUzLjg3NzlDNzEuMzAxOSA1NS41NzQ0IDY3Ljg1NzMgNTYuNDIyOCA2My44NjQ1IDU2LjQyMjhaTTYzLjkxNTkgNDcuOTQwMUM2NS43MzIzIDQ3Ljk0MDEgNjcuMjQ5MSA0Ny40MjYgNjguNDY1OSA0Ni4zOTc4QzY5LjY4MjQgNDUuMzUyNCA3MC41OTkzIDQzLjkzIDcxLjIxNjMgNDIuMTMwN0M3MS44NTA0IDQwLjMzMTQgNzIuMTY3NCAzOC4yODM0IDcyLjE2NzQgMzUuOTg3MUM3Mi4xNjc0IDMzLjY5MDggNzEuODUwNCAzMS42NDMgNzEuMjE2MyAyOS44NDM3QzcwLjU5OTMgMjguMDQ0MiA2OS42ODI0IDI2LjYyMTggNjguNDY1OSAyNS41NzY2QzY3LjI0OTEgMjQuNTMxMyA2NS43MzIzIDI0LjAwODcgNjMuOTE1OSAyNC4wMDg3QzYyLjA4MjQgMjQuMDA4NyA2MC41NDAxIDI0LjUzMTMgNTkuMjg5IDI1LjU3NjZDNTguMDU1MSAyNi42MjE4IDU3LjEyMTMgMjguMDQ0MiA1Ni40ODcyIDI5Ljg0MzdDNTUuODcwMiAzMS42NDMgNTUuNTYxOSAzMy42OTA4IDU1LjU2MTkgMzUuOTg3MUM1NS41NjE5IDM4LjI4MzQgNTUuODcwMiA0MC4zMzE0IDU2LjQ4NzIgNDIuMTMwN0M1Ny4xMjEzIDQzLjkzIDU4LjA1NTEgNDUuMzUyNCA1OS4yODkgNDYuMzk3OEM2MC41NDAxIDQ3LjQyNiA2Mi4wODI0IDQ3Ljk0MDEgNjMuOTE1OSA0Ny45NDAxWk05MC40MTgxIDU1LjY1MTZWMTYuMTY4NkgxMDEuMDM0VjIzLjA1NzZIMTAxLjQ0NkMxMDIuMTY1IDIwLjYwNzEgMTAzLjM3MyAxOC43NTYyIDEwNS4wNyAxNy41MDUxQzEwNi43NjYgMTYuMjM3MSAxMDguNzIgMTUuNjAzIDExMC45MzEgMTUuNjAzQzExMS40NzkgMTUuNjAzIDExMi4wNyAxNS42MzczIDExMi43MDQgMTUuNzA1OEMxMTMuMzM5IDE1Ljc3NDQgMTEzLjg5NSAxNS44Njg3IDExNC4zNzUgMTUuOTg4NlYyNS43MDUyQzExMy44NjEgMjUuNTUxIDExMy4xNSAyNS40MTM3IDExMi4yNDIgMjUuMjkzOEMxMTEuMzMzIDI1LjE3MzkgMTEwLjUwMiAyNS4xMTQgMTA5Ljc0OCAyNS4xMTRDMTA4LjEzNyAyNS4xMTQgMTA2LjY5OCAyNS40NjUxIDEwNS40MyAyNi4xNjc3QzEwNC4xNzkgMjYuODUzMiAxMDMuMTg1IDI3LjgxMzEgMTAyLjQ0OCAyOS4wNDY4QzEwMS43MjggMzAuMjgwNyAxMDEuMzY4IDMxLjcwMzEgMTAxLjM2OCAzMy4zMTM5VjU1LjY1MTZIOTAuNDE4MVpNMTQzLjAxNyAxNi4xNjg2VjI0LjM5NDNIMTE5LjI0VjE2LjE2ODZIMTQzLjAxN1pNMTI0LjYzOCA2LjcwOTA0SDEzNS41ODlWNDMuNTE4OEMxMzUuNTg5IDQ0LjUyOTggMTM1Ljc0MyA0NS4zMTgxIDEzNi4wNTEgNDUuODgzN0MxMzYuMzYgNDYuNDMyMSAxMzYuNzg4IDQ2LjgxNzcgMTM3LjMzNiA0Ny4wNDA0QzEzNy45MDIgNDcuMjYzMSAxMzguNTUzIDQ3LjM3NDYgMTM5LjI5IDQ3LjM3NDZDMTM5LjgwNCA0Ny4zNzQ2IDE0MC4zMTggNDcuMzMxNiAxNDAuODMyIDQ3LjI0NkMxNDEuMzQ2IDQ3LjE0MzIgMTQxLjc0MSA0Ny4wNjYyIDE0Mi4wMTUgNDcuMDE0OEwxNDMuNzM3IDU1LjE2MzNDMTQzLjE4OSA1NS4zMzQ2IDE0Mi40MTcgNTUuNTMxNyAxNDEuNDI0IDU1Ljc1NDRDMTQwLjQzIDU1Ljk5NDMgMTM5LjIyMiA1Ni4xNCAxMzcuNzk5IDU2LjE5MTRDMTM1LjE2IDU2LjI5NDIgMTMyLjg0NyA1NS45NDI5IDEzMC44NTkgNTUuMTM3NUMxMjguODg4IDU0LjMzMiAxMjcuMzU0IDUzLjA4MTIgMTI2LjI1NyA1MS4zODQ1QzEyNS4xNjEgNDkuNjg4IDEyNC42MjEgNDcuNTQ1OSAxMjQuNjM4IDQ0Ljk1ODNWNi43MDkwNFpNMTcxLjM4MyAxNi4xNjg2VjI0LjM5NDNIMTQ3LjAxNFYxNi4xNjg2SDE3MS4zODNaTTE1Mi41OTIgNTUuNjUxNlYxMy4zMTUyQzE1Mi41OTIgMTAuNDUzNSAxNTMuMTQ5IDguMDc5OTggMTU0LjI2MyA2LjE5NDkzQzE1NS4zOTQgNC4zMDk4OSAxNTYuOTM3IDIuODk2MSAxNTguODkgMS45NTM1OUMxNjAuODQ0IDEuMDExMDYgMTYzLjA2MyAwLjUzOTgwNSAxNjUuNTQ4IDAuNTM5ODA1QzE2Ny4yMjcgMC41Mzk4MDUgMTY4Ljc2MSAwLjY2ODMzOCAxNzAuMTQ5IDAuOTI1MzhDMTcxLjU1NCAxLjE4MjQ1IDE3Mi42IDEuNDEzNzkgMTczLjI4NSAxLjYxOTQxTDE3MS4zMzEgOS44NDUwMUMxNzAuOTAzIDkuNzA3OTYgMTcwLjM3MiA5LjU3OTM1IDE2OS43MzggOS40NTk0OEMxNjkuMTIxIDkuMzM5NTQgMTY4LjQ4NyA5LjI3OTU2IDE2Ny44MzYgOS4yNzk1NkMxNjYuMjI1IDkuMjc5NTYgMTY1LjEwMiA5LjY1NjU2IDE2NC40NjggMTAuNDEwNkMxNjMuODM0IDExLjE0NzUgMTYzLjUxNyAxMi4xODQzIDE2My41MTcgMTMuNTIxVjU1LjY1MTZIMTUyLjU5MlpNMTk0LjQ5OCA1Ni40MjI4QzE5MC41MDUgNTYuNDIyOCAxODcuMDUyIDU1LjU3NDQgMTg0LjEzOSA1My44Nzc5QzE4MS4yNDMgNTIuMTY0MyAxNzkuMDA3IDQ5Ljc4MjQgMTc3LjQzIDQ2LjczMkMxNzUuODU0IDQzLjY2NDYgMTc1LjA2NSA0MC4xMDg1IDE3NS4wNjUgMzYuMDY0M0MxNzUuMDY1IDMxLjk4NTkgMTc1Ljg1NCAyOC40MjEzIDE3Ny40MyAyNS4zNzFDMTc5LjAwNyAyMi4zMDM2IDE4MS4yNDMgMTkuOTIxNiAxODQuMTM5IDE4LjIyNDlDMTg3LjA1MiAxNi41MTEyIDE5MC41MDUgMTUuNjU0NCAxOTQuNDk4IDE1LjY1NDRDMTk4LjQ5MSAxNS42NTQ0IDIwMS45MzYgMTYuNTExMiAyMDQuODMyIDE4LjIyNDlDMjA3Ljc0NSAxOS45MjE2IDIwOS45OSAyMi4zMDM2IDIxMS41NjcgMjUuMzcxQzIxMy4xNDMgMjguNDIxMyAyMTMuOTMxIDMxLjk4NTkgMjEzLjkzMSAzNi4wNjQzQzIxMy45MzEgNDAuMTA4NSAyMTMuMTQzIDQzLjY2NDYgMjExLjU2NyA0Ni43MzJDMjA5Ljk5IDQ5Ljc4MjQgMjA3Ljc0NSA1Mi4xNjQzIDIwNC44MzIgNTMuODc3OUMyMDEuOTM2IDU1LjU3NDQgMTk4LjQ5MSA1Ni40MjI4IDE5NC40OTggNTYuNDIyOFpNMTk0LjU1IDQ3Ljk0MDFDMTk2LjM2NiA0Ny45NDAxIDE5Ny44ODMgNDcuNDI2IDE5OS4xIDQ2LjM5NzhDMjAwLjMxNiA0NS4zNTI0IDIwMS4yMzMgNDMuOTMgMjAxLjg1IDQyLjEzMDdDMjAyLjQ4NCA0MC4zMzE0IDIwMi44MDEgMzguMjgzNCAyMDIuODAxIDM1Ljk4NzFDMjAyLjgwMSAzMy42OTA4IDIwMi40ODQgMzEuNjQzIDIwMS44NSAyOS44NDM3QzIwMS4yMzMgMjguMDQ0MiAyMDAuMzE2IDI2LjYyMTggMTk5LjEgMjUuNTc2NkMxOTcuODgzIDI0LjUzMTMgMTk2LjM2NiAyNC4wMDg3IDE5NC41NSAyNC4wMDg3QzE5Mi43MTYgMjQuMDA4NyAxOTEuMTc0IDI0LjUzMTMgMTg5LjkyMyAyNS41NzY2QzE4OC42ODkgMjYuNjIxOCAxODcuNzU1IDI4LjA0NDIgMTg3LjEyMSAyOS44NDM3QzE4Ni41MDQgMzEuNjQzIDE4Ni4xOTYgMzMuNjkwOCAxODYuMTk2IDM1Ljk4NzFDMTg2LjE5NiAzOC4yODM0IDE4Ni41MDQgNDAuMzMxNCAxODcuMTIxIDQyLjEzMDdDMTg3Ljc1NSA0My45MyAxODguNjg5IDQ1LjM1MjQgMTg5LjkyMyA0Ni4zOTc4QzE5MS4xNzQgNDcuNDI2IDE5Mi43MTYgNDcuOTQwMSAxOTQuNTUgNDcuOTQwMVpNMjMyLjAwMiAzLjAwNzVWNTUuNjUxNkgyMjEuMDUyVjMuMDA3NUgyMzIuMDAyWk0yNDAuNzc0IDU1LjY1MTZWMTYuMTY4NkgyNTEuNzIzVjU1LjY1MTZIMjQwLjc3NFpNMjQ2LjI3NSAxMS4wNzg5QzI0NC42NDYgMTEuMDc4OSAyNDMuMjQ5IDEwLjUzOTIgMjQyLjA4NCA5LjQ1OTQ4QzI0MC45MzggOC4zNjI3NCAyNDAuMzY0IDcuMDUxNzYgMjQwLjM2NCA1LjUyNjZDMjQwLjM2NCA0LjAxODU2IDI0MC45MzggMi43MjQ3NCAyNDIuMDg0IDEuNjQ1MTNDMjQzLjI0OSAwLjU0ODM3IDI0NC42NDYgMCAyNDYuMjc1IDBDMjQ3LjkwNCAwIDI0OS4yOTEgMC41NDgzNyAyNTAuNDQgMS42NDUxM0MyNTEuNjA1IDIuNzI0NzQgMjUyLjE4NyA0LjAxODU2IDI1Mi4xODcgNS41MjY2QzI1Mi4xODcgNy4wNTE3NiAyNTEuNjA1IDguMzYyNzQgMjUwLjQ0IDkuNDU5NDhDMjQ5LjI5MSAxMC41MzkyIDI0Ny45MDQgMTEuMDc4OSAyNDYuMjc1IDExLjA3ODlaTTI3OC4zMzUgNTYuNDIyOEMyNzQuMzQ0IDU2LjQyMjggMjcwLjg4OSA1NS41NzQ0IDI2Ny45NzYgNTMuODc3OUMyNjUuMDgxIDUyLjE2NDMgMjYyLjg0NCA0OS43ODI0IDI2MS4yNjkgNDYuNzMyQzI1OS42OTEgNDMuNjY0NiAyNTguOTAyIDQwLjEwODUgMjU4LjkwMiAzNi4wNjQzQzI1OC45MDIgMzEuOTg1OSAyNTkuNjkxIDI4LjQyMTMgMjYxLjI2OSAyNS4zNzFDMjYyLjg0NCAyMi4zMDM2IDI2NS4wODEgMTkuOTIxNiAyNjcuOTc2IDE4LjIyNDlDMjcwLjg4OSAxNi41MTEyIDI3NC4zNDQgMTUuNjU0NCAyNzguMzM1IDE1LjY1NDRDMjgyLjMyOCAxNS42NTQ0IDI4NS43NzQgMTYuNTExMiAyODguNjY5IDE4LjIyNDlDMjkxLjU4MSAxOS45MjE2IDI5My44MjggMjIuMzAzNiAyOTUuNDAzIDI1LjM3MUMyOTYuOTgxIDI4LjQyMTMgMjk3Ljc2OCAzMS45ODU5IDI5Ny43NjggMzYuMDY0M0MyOTcuNzY4IDQwLjEwODUgMjk2Ljk4MSA0My42NjQ2IDI5NS40MDMgNDYuNzMyQzI5My44MjggNDkuNzgyNCAyOTEuNTgxIDUyLjE2NDMgMjg4LjY2OSA1My44Nzc5QzI4NS43NzQgNTUuNTc0NCAyODIuMzI4IDU2LjQyMjggMjc4LjMzNSA1Ni40MjI4Wk0yNzguMzg4IDQ3Ljk0MDFDMjgwLjIwNSA0Ny45NDAxIDI4MS43MiA0Ny40MjYgMjgyLjkzNiA0Ni4zOTc4QzI4NC4xNTUgNDUuMzUyNCAyODUuMDcxIDQzLjkzIDI4NS42ODcgNDIuMTMwN0MyODYuMzIxIDQwLjMzMTQgMjg2LjYzNyAzOC4yODM0IDI4Ni42MzcgMzUuOTg3MUMyODYuNjM3IDMzLjY5MDggMjg2LjMyMSAzMS42NDMgMjg1LjY4NyAyOS44NDM3QzI4NS4wNzEgMjguMDQ0MiAyODQuMTU1IDI2LjYyMTggMjgyLjkzNiAyNS41NzY2QzI4MS43MiAyNC41MzEzIDI4MC4yMDUgMjQuMDA4NyAyNzguMzg4IDI0LjAwODdDMjc2LjU1NCAyNC4wMDg3IDI3NS4wMTIgMjQuNTMxMyAyNzMuNzYgMjUuNTc2NkMyNzIuNTI3IDI2LjYyMTggMjcxLjU5MyAyOC4wNDQyIDI3MC45NTkgMjkuODQzN0MyNzAuMzQxIDMxLjY0MyAyNzAuMDMyIDMzLjY5MDggMjcwLjAzMiAzNS45ODcxQzI3MC4wMzIgMzguMjgzNCAyNzAuMzQxIDQwLjMzMTQgMjcwLjk1OSA0Mi4xMzA3QzI3MS41OTMgNDMuOTMgMjcyLjUyNyA0NS4zNTI0IDI3My43NiA0Ni4zOTc4QzI3NS4wMTIgNDcuNDI2IDI3Ni41NTQgNDcuOTQwMSAyNzguMzg4IDQ3Ljk0MDFaIgogIGZpbGw9IiMwMDcyQjIiCi8+CjxwYXRoCiAgZD0iTTM5My4zNTggMzIuODI4NFY1NS42NTQ1SDM4Mi40MDhWMTYuMTcxNUgzOTIuODQ0VjIzLjEzNzRIMzkzLjMwN0MzOTQuMTgxIDIwLjg0MTEgMzk1LjY0NSAxOS4wMjQ3IDM5Ny43MDEgMTcuNjg3OUMzOTkuNzU5IDE2LjMzNDEgNDAyLjI1MiAxNS42NTczIDQwNS4xODEgMTUuNjU3M0M0MDcuOTI0IDE1LjY1NzMgNDEwLjMxNSAxNi4yNTcxIDQxMi4zNTQgMTcuNDU2NkM0MTQuMzkzIDE4LjY1NjIgNDE1Ljk3OCAyMC4zNjk4IDQxNy4xMSAyMi41OTc2QzQxOC4yMzkgMjQuODA4MyA0MTguODA2IDI3LjQ0NzUgNDE4LjgwNiAzMC41MTQ5VjU1LjY1NDVINDA3Ljg1NFYzMi40Njg0QzQwNy44NzEgMzAuMDUyMSA0MDcuMjU2IDI4LjE2NzIgNDA2LjAwNCAyNi44MTM0QzQwNC43NTQgMjUuNDQyNCA0MDMuMDMxIDI0Ljc1NjkgNDAwLjgzOCAyNC43NTY5QzM5OS4zNjMgMjQuNzU2OSAzOTguMDYgMjUuMDczOSAzOTYuOTMxIDI1LjcwOEMzOTUuODE2IDI2LjM0MjEgMzk0Ljk0MyAyNy4yNjc1IDM5NC4zMDggMjguNDg0QzM5My42OTEgMjkuNjgzNyAzOTMuMzc1IDMxLjEzMTcgMzkzLjM1OCAzMi44Mjg0Wk00NDUuNDMgNTYuNDI1NkM0NDEuMzY5IDU2LjQyNTYgNDM3Ljg3MyA1NS42MDMxIDQzNC45NDEgNTMuOTU4QzQzMi4wMjkgNTIuMjk1OCA0MjkuNzg1IDQ5Ljk0NzggNDI4LjIwNyA0Ni45MTQ2QzQyNi42MzEgNDMuODY0MyA0MjUuODQyIDQwLjI1NzEgNDI1Ljg0MiAzNi4wOTNDNDI1Ljg0MiAzMi4wMzE0IDQyNi42MzEgMjguNDY2OSA0MjguMjA3IDI1LjM5OTRDNDI5Ljc4NSAyMi4zMzIgNDMyLjAwMiAxOS45NDE2IDQzNC44NjQgMTguMjI3N0M0MzcuNzQ1IDE2LjUxNDEgNDQxLjEyIDE1LjY1NzMgNDQ0Ljk5MyAxNS42NTczQzQ0Ny41OTYgMTUuNjU3MyA0NTAuMDIxIDE2LjA3NzEgNDUyLjI2OCAxNi45MTY4QzQ1NC41MjkgMTcuNzM5MyA0NTYuNSAxOC45ODE3IDQ1OC4xNzkgMjAuNjQ0MkM0NTkuODc1IDIyLjMwNjQgNDYxLjE5NSAyNC4zOTcxIDQ2Mi4xMzkgMjYuOTE2MkM0NjMuMDggMjkuNDE4IDQ2My41NTMgMzIuMzQ4NSA0NjMuNTUzIDM1LjcwNzRWMzguNzE0OEg0MzAuMjEyVjMxLjkyODZINDUzLjI0NUM0NTMuMjQ1IDMwLjM1MjEgNDUyLjkwMiAyOC45NTU1IDQ1Mi4yMTcgMjcuNzM4N0M0NTEuNTI5IDI2LjUyMTkgNDUwLjU3OSAyNS41NzEgNDQ5LjM2MyAyNC44ODU1QzQ0OC4xNjMgMjQuMTgyOSA0NDYuNzY2IDIzLjgzMTYgNDQ1LjE3MiAyMy44MzE2QzQ0My41MTEgMjMuODMxNiA0NDIuMDM3IDI0LjIxNzEgNDQwLjc1MSAyNC45ODgzQzQzOS40ODQgMjUuNzQyMyA0MzguNDkgMjYuNzYyIDQzNy43NjkgMjguMDQ3MUM0MzcuMDUgMjkuMzE1MyA0MzYuNjgxIDMwLjcyOSA0MzYuNjY0IDMyLjI4ODZWMzguNzQwNkM0MzYuNjY0IDQwLjY5NCA0MzcuMDIzIDQyLjM4MjEgNDM3Ljc0NSA0My44MDQ1QzQzOC40ODEgNDUuMjI2OCA0MzkuNTE4IDQ2LjMyMzUgNDQwLjg1NSA0Ny4wOTQ2QzQ0Mi4xOTIgNDcuODY1OCA0NDMuNzc3IDQ4LjI1MTQgNDQ1LjYxMSA0OC4yNTE0QzQ0Ni44MjcgNDguMjUxNCA0NDcuOTM5IDQ4LjA4IDQ0OC45NTIgNDcuNzM3NEM0NDkuOTYzIDQ3LjM5NDUgNDUwLjgyNyA0Ni44ODA0IDQ1MS41NDkgNDYuMTk0OUM0NTIuMjY4IDQ1LjUwOTYgNDUyLjgxNSA0NC42Njk3IDQ1My4xOTIgNDMuNjc1OUw0NjMuMzIxIDQ0LjM0NDJDNDYyLjgwNyA0Ni43Nzc2IDQ2MS43NTMgNDguOTAyNiA0NjAuMTU4IDUwLjcxOUM0NTguNTgyIDUyLjUxODUgNDU2LjU0MyA1My45MjM3IDQ1NC4wNDEgNTQuOTM0N0M0NTEuNTU2IDU1LjkyODYgNDQ4LjY4NSA1Ni40MjU2IDQ0NS40MyA1Ni40MjU2WiIKICBmaWxsPSIjMDA3MkIyIgovPgo8cGF0aAogIGQ9Ik0zMjkuMTI5IDMyLjUzNkMzMjkuMTI5IDMyLjM3MjYgMzI4Ljg1NCAzMi4yNDA2IDMyOC41MTcgMzIuMjQwNkMzMjguMTgxIDMyLjI0MDYgMzI3LjY2NyAzMi4wNDk1IDMyNy4zNzggMzEuODE3OUMzMjcuMDg4IDMxLjU4NiAzMjYuNjk3IDMxLjU4NiAzMjYuNTEyIDMxLjgxNzlDMzI2LjMyNiAzMi4wNDkgMzI2LjQwMyAzMi4yNDA2IDMyNi42OCAzMi4yNDA2QzMyNi45NTggMzIuMjQwNiAzMjcuMzQ5IDMyLjM3MjYgMzI3LjU0NyAzMi41MzZDMzI3Ljc0NSAzMi42OTc5IDMyOC4xODEgMzIuODMwOCAzMjguNTE3IDMyLjgzMDhDMzI4Ljg1NCAzMi44MzA2IDMyOS4xMjkgMzIuNjk2OSAzMjkuMTI5IDMyLjUzNloiCiAgZmlsbD0iIzE3NTQyRiIKLz4KPHBhdGgKICBkPSJNMzMxLjI4NCAzMy4xMjcxQzMzMS4wNzQgMzIuOTY1NCAzMzAuODY2IDMyLjcxODEgMzMwLjgyMSAzMi41Nzg5TDMzMC4zOTggMzIuODMxMkwzMjkuOTc2IDMzLjA4NDRDMzI5LjUxIDMzLjI4NjMgMzI4Ljc1IDMzLjc3ODggMzI4LjI4NyAzNC4xODE3SDMyOS4xMzJIMzI5LjYzOEgzMzEuMjg0QzMzMS40OTQgMzQuMTgxNyAzMzEuNjY1IDM0LjAxMTYgMzMxLjY2NSAzMy44MDMxQzMzMS42NjUgMzMuNTkzNyAzMzEuNDk0IDMzLjI4OTcgMzMxLjI4NCAzMy4xMjcxWiIKICBmaWxsPSIjMTc1NDJGIgovPgo8cGF0aAogIGQ9Ik0zNTAuMDcyIDE5LjQ3NDZWMTkuNDk0MUMzNDkuODA5IDE5Ljg4ODkgMzQ5LjU5MiAyMC40MDI2IDM0OS41OTIgMjAuNjM1MkMzNDkuNTkyIDIwLjg2NjUgMzQ5LjYzMyAyMS4xOCAzNDkuNjg2IDIxLjMzMkMzNDkuNzM3IDIxLjQ4MjggMzUwLjAxNyAyMS4zOTY5IDM1MC4zMDYgMjEuMTQwOUMzNTAuNTk2IDIwLjg4NTYgMzUwLjkyOSAyMC42MTk3IDM1MS4wNDQgMjAuNTQ5N0MzNTEuMTYgMjAuNDggMzUxLjI1NCAyMC4xOTM2IDM1MS4yNTQgMTkuOTE1NlYxOS43NDdDMzUxLjI1NCAxOS41NzgxIDM1MC45NiAxOS4xNTY4IDM1MC44NzYgMTguOTg3NEMzNTAuNzkxIDE4LjgxODggMzUwLjUzOCAxOC40ODE0IDM1MC41MTYgMTguMjI4MUwzNTAuNDk3IDE3Ljk3NUMzNTAuMzMzIDE3LjYyNjggMzUwLjAzMSAxNy4zNDA5IDM0OS44MjQgMTcuMzQwOUgzNDkuNzhDMzQ5LjczNCAxNy4zNDA5IDM0OS42OTMgMTcuODA2MyAzNDkuNjA5IDE3LjkzMjNMMzQ5LjUyNCAxOC4wNTk5QzM0OS42NjQgMTguNDc4MSAzNDkuOTEgMTkuMTA0NCAzNTAuMDcyIDE5LjQ1MzhWMTkuNDc0NloiCiAgZmlsbD0iIzE3NTQyRiIKLz4KPHBhdGgKICBkPSJNMzQ4LjM4MSAyMC40Njc2TDM0OC41OTQgMjAuNDI0OUMzNDguODA0IDIwLjMwODYgMzQ5LjA1IDE5LjkzODUgMzQ5LjE0NCAxOS42MDIxQzM0OS4yMzYgMTkuMjY0MyAzNDkuMjkzIDE4Ljc5ODkgMzQ5LjI2OSAxOC41NjdMMzQ4Ljk3MyAxOC43MzYyQzM0OC42NzggMTguOTA0OCAzNDguMzgxIDE4Ljk4ODUgMzQ4LjM4MSAxOS4yNDI0QzM0OC4zODEgMTkuNDk1NSAzNDguMTcxIDIwLjUwOTYgMzQ4LjM4MSAyMC40Njc2WiIKICBmaWxsPSIjMTc1NDJGIgovPgo8cGF0aAogIGQ9Ik0zNjUuNDM4IDQyLjgzNzVDMzY0LjgxMyA0My42NTYyIDM2NC4yMTIgNDQuNDA5NSAzNjQuMTA0IDQ0LjUxMTNDMzYzLjk5NyA0NC42MTI5IDM2My42NjcgNDUuMDkzNSAzNjMuMzcgNDUuNTgzM0wzNjMuMjg2IDQ1Ljc1MjVMMzYzLjIwMSA0NS45MjExQzM2My40MzMgNDYuMjQ0IDM2My42ODYgNDYuNTEyMyAzNjMuNzY2IDQ2LjUxMjNDMzYzLjg0NSA0Ni41MTIzIDM2NC4wMDkgNDYuNTMwMSAzNjQuMTMgNDYuNTUzOEwzNjQuMjE1IDQ2LjUxMjNDMzY0LjI5OSA0Ni40NjkzIDM2NC4zODMgNDYuNDI3NiAzNjQuNDY4IDQ2LjIxNTVDMzY0LjU1MiA0Ni4wMDUzIDM2NC42MzcgNDUuOTYyNCAzNjQuNjc4IDQ1LjYyNTNDMzY0LjcyMSA0NS4yODc1IDM2NS4zMTIgNDQuMzE2NiAzNjUuMzUzIDQ0LjE0ODFMMzY1LjM5NyA0My45NzhDMzY1LjYwNCA0My4yODI5IDM2NS45MyA0Mi4yNzUzIDM2Ni4xMTYgNDEuNzQwOEwzNjUuNzc4IDQyLjI4OTNMMzY1LjQzOCA0Mi44Mzc1WiIKICBmaWxsPSIjMTc1NDJGIgovPgo8cGF0aAogIGQ9Ik0zNDUuNTM3IDAuMTYxMTMzQzMyOS4wNCAwLjE2MTEzMyAzMTUuNjE3IDEzLjU4MzEgMzE1LjYxNyAzMC4wODA2QzMxNS42MTcgNDYuNTc4IDMyOS4wNCA2MCAzNDUuNTM3IDYwQzM2Mi4wMzMgNjAgMzc1LjQ1NiA0Ni41NzggMzc1LjQ1NiAzMC4wODA2QzM3NS40NTYgMTMuNTgzMSAzNjIuMDMzIDAuMTYxMTMzIDM0NS41MzcgMC4xNjExMzNaTTM2MS40MTEgNi4zNDA0OUMzNjIuMjk0IDYuOTMzMDEgMzYzLjE0MSA3LjU3MzIxIDM2My45NTIgOC4yNTc3MkMzNjMuODQxIDguNDU4MTggMzYzLjgwOSA4LjYxMzMyIDM2My45MTUgOC42ODk1QzM2NC4xNDcgOC44NTg2NiAzNjMuNjYyIDkuNzM5OTQgMzYzLjMxMiAxMC4zMDg2TDM2Mi40ODkgOS42MTgzM0MzNjIuNDg5IDkuNjE4MzMgMzYxLjcyOSA3LjU5MzE5IDM2MS40NzYgNy4zMzg1MUMzNjEuMzE3IDcuMTc5NjMgMzYxLjM1OCA2LjY4NDkgMzYxLjQxMSA2LjM0MDQ5Wk0zNTUuMTQ1IDI2LjMzN0wzNTUuNjYxIDI1LjYyNEgzNTYuMzI1TDM1Ny42NzYgMjYuMDgyN0wzNTcuNTkxIDI1LjA2OTNIMzU4LjE4MkwzNTkuMzY1IDI2LjExN0gzNjEuNDc2QzM2MS40NzYgMjYuMTE3IDM2MS4yMjMgMjYuOTI3MiAzNjEuMDU0IDI3LjIzODlDMzYwLjg4NSAyNy41NTI5IDM1OS43ODcgMjcuODU1NyAzNTkuNzg3IDI3Ljg1NTdIMzU4LjI2N0wzNTcuNTA3IDI3Ljc3MTJMMzU2LjU3OCAyOC4zNjE0TDM1NS42NjEgMjcuOTM5OUMzNTUuNjYxIDI3LjkzOTkgMzU0LjU1NCAyNy4wMTE0IDM1NC40NjcgMjYuNzU3MUMzNTQuMzgyIDI2LjUwNDcgMzUzLjExOCAyNi4zMzQ2IDM1Mi44NjUgMjYuMjUwMkMzNTIuNjExIDI2LjE2NTUgMzUyLjE4OSAyNS45OTY4IDM1MS4xNzMgMjYuMjUwMkMzNTEuMTczIDI2LjI1MDIgMzUwLjc1MyAyNi41ODggMzQ5Ljk5MyAyNi43NTcxQzM0OS4yMzMgMjYuOTI3MiAzNTAuNzUzIDI1Ljc0MyAzNTEuMTczIDI1LjYyMjZDMzUxLjU5OCAyNS41MDE5IDM1MS43NjcgMjQuNzMwNSAzNTIuMDIgMjQuMTM5NEMzNTIuMjcxIDIzLjU0ODIgMzUzLjM2OSAyNC4xMzk0IDM1My4zNjkgMjQuMTM5NEgzNTQuMDQ0QzM1NC4wNDQgMjQuMTM5NCAzNTQuODA0IDI0LjY0NTYgMzU1LjA2IDI1LjA2NzlDMzU1LjMxMSAyNS40OTAzIDM1NC44OTEgMjUuMzIxMiAzNTQuNzIgMjUuNjIxNkMzNTQuNTU0IDI1LjkyNTQgMzU1LjE0NSAyNi4zMzcgMzU1LjE0NSAyNi4zMzdaTTM1OC44NTggMjMuMjk2OEMzNTguODU4IDIzLjI5NjggMzU5LjQ0OSAyMy4wNDM3IDM1OS43MDMgMjIuNzQ1NUMzNTkuOTU2IDIyLjQ0NjMgMzYwLjQ2MyAyMi43NDU1IDM2MC40NjMgMjIuNzQ1NUwzNjAuOTI2IDIxLjYwODVDMzYwLjkyNiAyMS42MDg1IDM2MS4zOTIgMjIuNDUyNiAzNjEuNDc2IDIyLjcwNjZDMzYxLjU2IDIyLjk2IDM2Mi40ODkgMjMuMzgyNSAzNjIuNDg5IDIzLjM4MjVMMzYxLjk4MyAyMy44ODM5TDM2MC42MzIgMjMuODc4NkMzNjAuNjMyIDIzLjg3ODYgMzYwLjA0IDIzLjg4ODUgMzU5LjM2NSAyMy44Nzg2TDM1OC44NTggMjMuMjk2OFpNMzYxLjg5OCAyOS4yOTE2QzM2MS44OTggMjkuMjkxNiAzNjIuMzIxIDI5Ljg4MzIgMzYyLjQ4OSAzMC40MzQ1QzM2Mi42NTggMzAuOTg3MSAzNjMuNjcyIDMxLjkwOTggMzYzLjg0MSAzMi43MjU4QzM2NC4wMSAzMy41NDE2IDM2My44NDEgMzQuMTg4NSAzNjMuODQxIDM0LjE4ODVDMzYzLjg0MSAzNC4xODg1IDM2My4wODEgMzMuMjYwMiAzNjIuODI3IDMyLjgzOEMzNjIuNTc0IDMyLjQxNTUgMzYxLjgxNCAzMS42NTYyIDM2MS40NzYgMzEuNDAyOEMzNjEuMTM4IDMxLjE1MDQgMzYxLjA1NCAyOS4yOTE4IDM2MS4wNTQgMjkuMjkxOEwzNjEuODk4IDI5LjI5MTZaTTM0Mi4zNzYgMTMuNzcwNEwzNDIuMzkzIDEzLjc1NjRMMzQyLjUzMyAxMy42NTI2QzM0Mi40ODQgMTMuNjkgMzQyLjQ0MSAxMy43MjM2IDM0Mi40MDcgMTMuNzQ5NkMzNDIuNDY4IDEzLjcwNCAzNDIuNDk0IDEzLjY3OTkgMzQyLjM5MyAxMy43NTY0QzM0Mi4zNzYgMTMuNzcwNiAzNDIuMzU0IDEzLjc4OSAzNDIuMzM1IDEzLjgwNjNDMzQyLjM0NCAxMy43OTc5IDM0Mi4zNTcgMTMuNzg5NCAzNDIuMzY2IDEzLjc4QzM0Mi4zNDkgMTMuNzk1IDM0Mi4zMzUgMTMuODA2MyAzNDIuMzMyIDEzLjgwNzhDMzQyLjMzMiAxMy44MDc4IDM0Mi4zMzUgMTMuODA3OCAzNDIuMzM1IDEzLjgwNjNDMzQyLjMxNSAxMy44MjEzIDM0Mi4yOTkgMTMuODM1MyAzNDIuMjgyIDEzLjg0NzhDMzQyLjI5OSAxMy44MzMzIDM0Mi4zNTkgMTMuNzg0OSAzNDIuMzc2IDEzLjc3MDRaTTMxNi45NzMgMzAuNDgxOEMzMTcuMDI5IDMwLjUzMDYgMzE3LjA2MiAzMC41NTk1IDMxNy4wNjIgMzAuNTU5NUMzMTcuMDYyIDMwLjU1OTUgMzE3LjAyNCAzMC41ODcgMzE2Ljk3NiAzMC42MzI5QzMxNi45NzYgMzAuNTgyIDMxNi45NzYgMzAuNTMyIDMxNi45NzMgMzAuNDgxOFpNMzE2Ljk5NyAzMS4yNzU5QzMxNy4wMTcgMzEuMjkwOSAzMTcuMDM2IDMxLjMwNTMgMzE3LjA2MiAzMS4zMjAzQzMxNy42NTQgMzEuNjU4MSAzMTcuMDYyIDMxLjQwNDMgMzE3LjY1NCAzMS42NTgxQzMxOC4yNDUgMzEuOTExNyAzMTguMjQ1IDMxLjkxMTQgMzE4LjI0NSAzMS45MTE0QzMxOC4yNDUgMzEuOTExNCAzMTguMTYgMzEuNzQyNSAzMTguMjQ1IDMxLjQwNDNDMzE4LjMyOSAzMS4wNjY1IDMxOC42NjcgMzEuNjU3NiAzMTguMzI5IDMxLjA2NjVDMzE3Ljk5MSAzMC40NzQ4IDMxOC4xNiAzMS4xNTExIDMxNy45OTEgMzAuNDc0OEwzMTcuODIzIDI5Ljc5ODNDMzE3LjgyMyAyOS43OTgzIDMxNy42NTQgMjkuMzc1OCAzMTcuOTA3IDI5LjM3NThDMzE4LjE2IDI5LjM3NTggMzE4LjQ3NiAzMC4zMDUyIDMxOC40NzYgMzAuMzA1MkMzMTguNDc2IDMwLjMwNTIgMzE4LjkyIDMxLjMxOTMgMzE5LjE3NCAzMS40ODhMMzE5LjQyNyAzMS42NTY2QzMxOS40MjcgMzEuNjU2NiAzMTkuNzY1IDMxLjk5NDQgMzE5Ljg0OSAzMi4zMzI1QzMxOS45MzQgMzIuNjcwMyAzMTkuNDI3IDMyLjc1NDcgMzE5Ljg0OSAzMy4wMDgxQzMyMC4yNjkgMzMuMjYwNSAzMTkuNjggMzIuNzU0NyAzMjAuMjY5IDMzLjI2MDVDMzIwLjg2MyAzMy43Njc0IDMyMS4yMDEgMzMuNjgyIDMyMS40NTQgMzMuODUxNkMzMjEuNzA3IDM0LjAyMDggMzIxLjc5MiAzMy4zNDU0IDMyMi4wNDUgMzMuODUxNkMzMjIuMjk4IDM0LjM1NzYgMzIxLjUzOCAzMy44NTE2IDMyMi4yOTggMzQuMzU3NkMzMjMuMDU2IDM0Ljg2NiAzMjMuNDc4IDM1LjExOTMgMzIzLjQ3OCAzNS4xMTkzQzMyMy40NzggMzUuMTE5MyAzMjMuNTYzIDM0LjYxMjIgMzI0LjA3MiAzNS4xMTkzQzMyNC41NzkgMzUuNjI0OCAzMjUuMTcgMzUuNzA5NSAzMjUuMTcgMzUuNzA5NUMzMjUuMTcgMzUuNzA5NSAzMjUuMjU0IDM1Ljk2NDEgMzI1LjY3NiAzNi4zMDA5QzMyNi4wOTkgMzYuNjM5IDMyNS42NzYgMzYuMTMyMyAzMjYuMDk5IDM2LjYzOUwzMjYuNTIxIDM3LjE0NDRMMzI3LjI4MSAzNy42NTE0SDMyNy42MTlMMzI3Ljg3MiAzOC4wNzM5TDMyOC41NDggMzguOTE3NFYzOS41MDk4QzMyOC41NDggMzkuNTA5OCAzMjguMTI1IDM4LjkxNzQgMzI4LjEyNSAzOS41MDk4QzMyOC4xMjUgNDAuMTAwOSAzMjguMjEgMzkuNTk0IDMyOC4xMjUgNDAuMTAwOUwzMjguMDQxIDQwLjYwNzFMMzI4LjU0OCA0MS4yODQyVjQyLjQ2NkMzMjguNTQ4IDQyLjQ2NiAzMjkuMDU0IDQzLjA1NzIgMzI5LjMwOCA0My4yMjQ4QzMyOS41NTkgNDMuMzkzNSAzMjguODg2IDQyLjgwMzMgMzI5LjU1OSA0My4zOTM1TDMzMC4yMzQgNDMuOTg1MUwzMzEuMTYzIDQ0LjgyOTlWNDUuMTY3N0MzMzEuMTYzIDQ1LjE2NzcgMzMxLjc1NCA0NC43NDU0IDMzMi4wMDggNDUuMTY3N0MzMzIuMjYxIDQ1LjU5MDcgMzMyLjU5OSA0Ni4wMTI3IDMzMi41OTkgNDYuMDEyN1Y0Ni4zNTA1QzMzMi41OTkgNDYuMzUwNSAzMzIuOTM3IDQ1LjY3NDkgMzMzLjEwNiA0Ni4zNTA1QzMzMy4yNzUgNDcuMDI1MyAzMzMuMTA2IDQ3LjM2MzEgMzMzLjEwNiA0Ny4zNjMxQzMzMy4xMDYgNDcuMzYzMSAzMzMuNjE1IDQ3Ljc4NTQgMzMzLjY5NyA0OC4wMzg3QzMzMy43ODEgNDguMjkyMSAzMzMuNTI4IDQ4LjU0NSAzMzMuNjk3IDQ4Ljc5OUMzMzMuODY2IDQ5LjA1MjQgMzM0LjExOSA1MC4xNTEgMzM0LjExOSA1MC4xNTFMMzM0Ljc5NSA1MS41MDE0QzMzNC43OTUgNTEuNTAxNCAzMzQuNjI2IDUyLjAwNjkgMzM0Ljc5NSA1Mi4yNjAzQzMzNC45NjQgNTIuNTEzNiAzMzUuMjE3IDUzLjAyMDYgMzM1LjIxNyA1My4wMjA2QzMzNS4yMTcgNTMuMDIwNiAzMzQuNjI2IDUzLjUyNjUgMzM1LjIxNyA1NC4xMTg3QzMzNS44MDggNTQuNzEwMyAzMzUuNDcgNTQuMTE4NyAzMzUuODA4IDU0LjcxMDNDMzM2LjE0NiA1NS4zMDE5IDMzNi4zOTkgNTUuODkyOCAzMzYuMzk5IDU1Ljg5MjhMMzM3LjQ5OSA1Ny4xNTg5TDMzOC4yMTYgNTcuNjk4MUMzMjYuMzY5IDU0LjU1MjIgMzE3LjUyMSA0My45Njk5IDMxNi45OTUgMzEuMjc1MkwzMTYuOTk3IDMxLjI3NTlaTTM0NS41MzcgNTguNjQ4NkMzNDMuMzI0IDU4LjY0ODYgMzQxLjE2OSA1OC4zOTY3IDMzOS4wOTcgNTcuOTE3MkgzMzkuMjdMMzM4LjQyNiA1Ni4yMjg1QzMzOC40MjYgNTYuMjI4NSAzMzguNTk1IDU1LjcyMjIgMzM4LjM0MiA1NS40NjkxTDMzOC4wODggNTUuMjE1OEwzMzcuODM1IDU0Ljc5MjhWNTQuMjAyNkMzMzcuODM1IDU0LjIwMjYgMzM4LjE3MyA1My43Nzk5IDMzNy44MzUgNTMuNjExMkMzMzcuNDk3IDUzLjQ0MTkgMzM3LjQ5NyA1My45NDkgMzM3LjQ5NyA1My40NDE5VjUyLjkzNDlDMzM3LjQ5NyA1Mi45MzQ5IDMzNy45MTkgNTIuNTk4MSAzMzguMDg4IDUyLjM0NDdDMzM4LjI1NyA1Mi4wOTE2IDMzOC4wMDQgNTIuNjgxNiAzMzguMjU3IDUyLjA5MTZDMzM4LjUxIDUxLjUwMDUgMzM4LjY3OSA1MC43NDA3IDMzOC42NzkgNTAuNzQwN0wzMzkuMjcgNTAuMjM0NFY0OS4xMzY0QzMzOS4yNyA0OS4xMzY0IDMzOS4xODYgNDguODg0IDMzOS4yNyA0OC41NDM4QzMzOS4zNTUgNDguMjA2IDMzOS4yNyA0Ny43IDMzOS4yNyA0Ny43QzMzOS4yNyA0Ny43IDMzOS41MjQgNDcuNTMyMyAzMzkuNzc3IDQ3LjM2MjJDMzQwLjAzMSA0Ny4xOTM1IDM0MC43MDYgNDYuNjAyOCAzNDAuNzA2IDQ2LjYwMjhDMzQwLjcwNiA0Ni42MDI4IDM0MC4yODQgNDYuMzUwNSAzNDAuNzA2IDQ2LjA5NjZDMzQxLjEyOCA0NS44NDM1IDM0MS4zODIgNDUuNTg5NyAzNDEuMjk3IDQ1LjI1MTlDMzQxLjIxMyA0NC45MTQxIDM0MS4zODQgNDUuNzU5OCAzNDEuMjEzIDQ0LjkxNDFDMzQxLjA0NCA0NC4wNjkxIDM0MC45NTkgNDQuMTU0NSAzNDAuOTU5IDQzLjU2MzFDMzQwLjk1OSA0Mi45NzA1IDM0MC42MjIgNDMuNDc3NSAzNDAuOTU5IDQyLjk3MDVDMzQxLjI5NyA0Mi40NjUgMzQxLjgwNCA0MS40OTM0IDM0MS44MDQgNDEuNDkzNEMzNDEuODA0IDQxLjQ5MzQgMzQxLjIxMyA0MC44NjE3IDM0MC45NTkgNDAuNzc2QzM0MC43MDYgNDAuNjkyMSAzNDAuNDUzIDQwLjUyMjQgMzQwLjAzMSA0MC4zNTIzQzMzOS42MDggNDAuMTg0NyAzMzguNDI4IDM5Ljc2MjIgMzM4LjQyOCAzOS43NjIyQzMzOC40MjggMzkuNzYyMiAzMzcuODM3IDM5LjUwODggMzM3LjU4NCAzOS40MjQ0QzMzNy4zMzEgMzkuMzM5NyAzMzYuNDg2IDM4LjE1NjkgMzM2LjQ4NiAzOC4xNTY5QzMzNi40ODYgMzguMTU2OSAzMzYuNDAyIDM4LjE1NjkgMzM1LjY0MiAzNy45MDM4QzMzNC44ODEgMzcuNjUwNCAzMzQuNzEzIDM3LjU2NTcgMzM0LjQ1OSAzNy4zMTM2QzMzNC4yMDYgMzcuMDYwMiAzMzMuNTMgMzYuNDY4NiAzMzMuNTMgMzYuNDY4NkwzMzMuMzYxIDM2LjA0NzFDMzMzLjM2MSAzNi4wNDcxIDMzMy4xMDggMzYuMjk5NSAzMzIuMzQ4IDM2LjIxNTdDMzMxLjU4OCAzNi4xMzEzIDMzMC45MTIgMzUuNTM5NyAzMzAuOTEyIDM1LjUzOTdDMzMwLjkxMiAzNS41Mzk3IDMzMC40OSAzNS41Mzk3IDMzMC4xNTIgMzUuNzA4M0MzMjkuODE0IDM1Ljg3NyAzMjkuMjIzIDM2LjI5OTkgMzI5LjIyMyAzNi4yOTk5TDMyOC42MzIgMzYuNDY4NkwzMjcuNTM0IDM2LjM4NDZMMzI2Ljc3NCAzNS45NjMxTDMyNi4zNTIgMzUuMDMzMkMzMjYuMzUyIDM1LjAzMzIgMzI2LjI2OCAzNC42MTE3IDMyNi4wMTQgMzQuNDQxNkMzMjUuNzYzIDM0LjI3MzkgMzI1LjA4OCAzMy43NjY5IDMyNS4wODggMzMuNzY2OUwzMjUuNDI1IDMyLjc1MzNDMzI1LjQyNSAzMi43NTMzIDMyNS4wODggMzIuMzMwOCAzMjQuNzUgMzIuNTAwOUMzMjQuNDEyIDMyLjY2ODYgMzIzLjkwNSAzMy4yNTk3IDMyMy45MDUgMzMuMjU5N0MzMjMuOTA1IDMzLjI1OTcgMzIzLjY1MiAzMy40Mjg2IDMyMy4zOTkgMzMuMzQ0NEMzMjMuMTQ1IDMzLjI1OTcgMzIyLjcyMyAzMy4wOTExIDMyMi4zMDEgMzIuNjY4OEMzMjEuODc5IDMyLjI0NzMgMzIxLjc5NCAzMS44MjQ4IDMyMS43OTQgMzEuNTcxNUMzMjEuNzk0IDMxLjMxODQgMzIyLjMwMSAzMC4yMjA1IDMyMi4zMDEgMzAuMjIwNUwzMjMuNzM2IDI5LjIwNjZIMzI0LjU4MUwzMjUuNTEgMjguNzg0MUwzMjYuNDM2IDI5Ljk2NzRMMzI3LjE5NyAzMC44OTU0QzMyNy4xOTcgMzAuODk1NCAzMjguMTI1IDMwLjMwNDIgMzI3LjkxNiAzMC4wNTE5QzMyNy43MDMgMjkuNzk3MyAzMjcuMzY1IDI5LjI5MTEgMzI3LjM2NSAyOS4yOTExQzMyNy4zNjUgMjkuMjkxMSAzMjcuNzg4IDI4LjYxNTUgMzI3LjkxNiAyOC4zNjI2QzMyOC4wNDMgMjguMTA5NSAzMjguMjEgMjguMDI1OCAzMjguNTQ4IDI3LjUxOTNDMzI4Ljg4NiAyNy4wMTIxIDMyOS4wNTQgMjYuNzU5IDMyOS4yMjMgMjYuNTA1N0MzMjkuMzkyIDI2LjI1MTggMzMwLjA2OCAyNS4wNzAzIDMzMC4wNjggMjUuMDcwM0wzMzAuNzQzIDI0LjU2MjFMMzMxLjMzNSAyMy44MDI4TDMzMS43NTcgMjMuMzgxNUgzMzIuNDMyTDMzMy42MTUgMjIuNzg5OUgzMzQuMzc1TDMzMy42OTkgMjEuOTQ2M0wzMzMuMjc3IDIxLjQzODRDMzMzLjY5OSAyMS4wMTU1IDMzNC44NzkgMjAuNzYzNiAzMzQuODc5IDIwLjc2MzZDMzM0Ljg3OSAyMC43NjM2IDMzNi4wNjEgMjAuMDg3NSAzMzUuOTc5IDIwLjM0MDhDMzM1Ljg5NSAyMC41OTM5IDMzNC45NjQgMjEuNzc3MiAzMzQuOTY0IDIxLjc3NzJMMzM1LjYzOSAyMi4yODM0QzMzNS42MzkgMjIuMjgzNCAzMzYuMzk5IDIyLjQ1MjEgMzM2LjU2OCAyMi4xOTkyQzMzNi43MzcgMjEuOTQ1OSAzMzYuODIxIDIxLjM1NDIgMzM2LjgyMSAyMS4zNTQyTDMzNi41NjggMjAuMjg0NlYxOS4wNzMxQzMzNi41NjggMTguNjUxNiAzMzYuMzk5IDE3LjU1NDUgMzM2LjE0NiAxNy43MjI2QzMzNS44OTUgMTcuODkxOCAzMzUuNjM5IDE2Ljk2MzggMzM1LjYzOSAxNi45NjM4VjE1Ljc4MDVMMzM0LjcxIDE2LjYyNDVDMzM0LjcxIDE2LjYyNDUgMzM0LjAzNSAxNi41Mzk5IDMzNC4xMTkgMTYuMjg2NUMzMzQuMjAzIDE2LjAzMzQgMzM0LjYyNiAxNS43Nzk2IDMzNC42MjYgMTUuNzc5NkwzMzMuNjk3IDE1LjAxODhDMzMzLjY5NyAxNS4wMTg4IDMzMi42ODMgMTQuMzQ0MiAzMzIuNTE0IDE0LjU5NjVDMzMyLjM0NiAxNC44NDk2IDMzMi4wOTIgMTUuNTI1IDMzMi4wOTIgMTUuNTI1TDMzMS42NyAxNi40NTQ0VjE3LjA0NjFMMzMxLjMzMiAxNy44ODk4TDMzMC4zMTkgMTguOTAzNUwzMjkuODEyIDE5LjkxNTlDMzI5LjgxMiAxOS45MTU5IDMyOS42NDMgMTguNjUwMSAzMjkuNjQzIDE4LjM5NzNDMzI5LjY0MyAxOC4xNDQyIDMyOC41NDUgMTcuMTMxNSAzMjguNTQ1IDE3LjEzMTVMMzI4LjI5MiAxNi4xMTc2QzMyOC4yOTIgMTYuMTE3NiAzMjguNjMgMTUuNDQxOCAzMjguNjMgMTUuMTg4OUMzMjguNjMgMTQuOTM2NyAzMjkuMDUyIDE0LjQyOTYgMzI5LjM5IDE0LjA5MThDMzI5LjcyOCAxMy43NTQgMzMwLjU3MiAxMy4wNzc5IDMzMC44MjUgMTIuOTA5OUMzMzEuMDc5IDEyLjc0MTMgMzMxLjY3IDEyLjQwMyAzMzEuNjcgMTIuNDAzTDMzMS41MDEgMTMuODM4MkwzMzIuNTk5IDEzLjY2OTNMMzMyLjQzIDEyLjkwOTlMMzMzLjM1OSAxMi40MDNMMzMzLjg2NiAxMS4wNTExQzMzMy44NjYgMTEuMDUxMSAzMzQuMzcyIDkuODY5MjcgMzM0LjYyNiAxMC4wMzcyQzMzNC44NzcgMTAuMjA2MyAzMzUuNDY4IDEwLjk2NzEgMzM1LjQ2OCAxMC45NjcxTDMzNC41MzkgMTIuODIzNkgzMzMuNzgxTDMzMy41MjggMTMuNTgzOUMzMzMuNTI4IDEzLjU4MzkgMzMzLjk1IDEzLjY2ODUgMzM0LjI4OCAxMy45MjE3QzMzNC42MjYgMTQuMTc1IDMzNS4yMTcgMTQuODQ5NiAzMzUuMjE3IDE0Ljg0OTZMMzM2LjIzIDE0LjA5MDhWMTMuNDE1MkgzMzYuOTg4TDMzNy40OTcgMTIuMzE3MUwzMzcuMzI2IDExLjU1NjhDMzM3LjMyNiAxMS41NTY4IDMzNy4zMjYgMTEuMzAzNSAzMzcuNDEzIDEwLjk2NjZMMzM3LjQ5NyAxMC42MjgzTDMzNy4xNTkgMTAuMDIxOFY4LjUxNzU4TDMzNi42NSA3LjU5MDQ5SDMzNS4wNDhMMzMyLjQzIDYuMzIyN0gzMzEuNzU0TDMzMC41OTEgNS43NDA5MUMzMzIuNTk5IDQuNTA0OTUgMzM0Ljc3IDMuNTExOTQgMzM3LjA2NSAyLjc5NzU0QzMzNi44IDIuOTg0OTIgMzM2LjY1MyAzLjE1MzYzIDMzNi42NTMgMy4yOTQ3M0MzMzYuNjUzIDMuODkxOTIgMzM2LjgzMyA0LjY4NTM5IDMzNy4wNTMgNS4wNTU0OUMzMzcuMjczIDUuNDI3IDMzNy42NjQgNS43Njk5OSAzMzcuOTE5IDUuODE1NzhMMzM4LjI1NyA1LjczMDI1QzMzOC41OTUgNS42NDcwOCAzMzkuMjcgNC44MDIyNCAzMzkuNDM3IDQuNTQ5OUMzMzkuNjA4IDQuMjk2NjMgMzQwLjc5MSAzLjYyMTQxIDM0MS4xMjggMy40NTE3NkwzNDEuMjggMy4zNzUxM0MzNDEuNDkzIDMuMzc1MTMgMzQxLjcwNSAzLjM2NTM0IDM0MS43NTEgMy4zNTQ1N0wzNDEuODA0IDMuMzY4MTNMMzQxLjk5IDMuNDEyNTNDMzQxLjgxMSAzLjM5MzM3IDM0MS41MjkgMy42MzQ0OSAzNDEuMzYgMy45NTI3TDM0MC43OTEgNC4zNzk4TDM0MC4xMTUgNC44ODY4MUMzMzkuOTI3IDUuMzcxODQgMzM5LjkyNyA2LjA1NTQ4IDM0MC4xMTUgNi40MDY0TDM0MC42MTkgNy4yNTEyN0MzNDAuNjY1IDcuNDgzOTYgMzQwLjcwNCA3Ljc0OTg2IDM0MC43MDQgNy44NDM3N1Y4LjA5NzA0QzM0MC43MDQgOC4zNTAzIDM0MC42MTkgOS4xMDk2NSAzNDAuNjE5IDkuMzYyOUMzNDAuNjE5IDkuNjE2MTYgMzQwLjExMyAxMC45NjgxIDM0MC4xMTMgMTEuMjIwN0MzNDAuMTEzIDExLjQ3NDEgMzM5Ljk2NSAxMi4xNTcxIDMzOS43ODIgMTIuOTkzN0wzMzkuMjczIDEzLjMzMTVDMzM4Ljc2MSAxMy42NjkzIDMzOS4xOTEgMTMuOTIyNiAzMzkuMjczIDE0LjM0NTFDMzM5LjM1MyAxNC43NjY2IDMzOC42ODQgMTQuNjgyOSAzMzkuMjczIDE1LjE4ODlDMzM5Ljg1OSAxNS42OTYxIDMzOS42MDYgMTUuMTg4OSAzMzkuODU5IDE1LjY5NjFDMzQwLjExMyAxNi4yMDMgMzM5Ljk0NCAxNS44NjUyIDM0MC40NSAxNS42OTYxTDM0MC45MjYgMTUuNTM4QzM0MS42OTEgMTQuNTkzNiAzNDIuMjk5IDEzLjgzNzkgMzQyLjI4MiAxMy44NDc4QzM0Mi4yOTQgMTMuODM5NCAzNDIuMzAzIDEzLjgyOTUgMzQyLjMyIDEzLjgxNkMzNDIuMzI1IDEzLjgxMTkgMzQyLjMzIDEzLjgwOSAzNDIuMzMyIDEzLjgwNTRDMzQyLjMzNSAxMy44MDI5IDM0Mi40MTcgMTMuNzQxNyAzNDIuNTI1IDEzLjY1ODdMMzQyLjczMSAxMy40OTk3QzM0My44MjggMTIuNjU2MSAzNDMuMTUzIDEzLjA3NzIgMzQzLjgyOCAxMi42NTYxQzM0NC41MDQgMTIuMjMzOSAzNDMuNjU5IDEyLjQ4NzUgMzQ0LjUwNCAxMi4yMzM5TDM0NS4zNDggMTEuOThDMzQ1LjkwNiAxMS43MDA2IDM0Ni42NjYgMTEuMDE3NSAzNDcuMDM3IDEwLjQ1OTRMMzQ3LjEyMiAxMC4yMDcxQzM0Ny4yMDYgOS45NTM5NiAzNDcuMzczIDkuOTUzOTYgMzQ3LjEyMiA5LjYxNjE2QzM0Ni44NjkgOS4yNzgyNCAzNDYuNTMxIDEwLjEyMzEgMzQ2Ljg2OSA5LjI3ODI0QzM0Ny4yMDYgOC40MzQ3NyAzNDcuMDUyIDguNDM0NzcgMzQ3LjI1NSA4LjA5NjkzQzM0Ny40NiA3Ljc1OTA4IDM0Ni44ODMgOC4yNjQ2NyAzNDcuMjU1IDcuMzM2MThDMzQ3LjYyOSA2LjQwNzY4IDM0Ny42MjkgNi40MDc2OCAzNDcuNjI5IDYuNDA3NjhDMzQ3Ljc2OSA2LjE3NjM5IDM0Ny42NTMgNS44MzQzMiAzNDcuMzc1IDUuNjQ4MzNMMzQ3Ljg4MiA1LjMxMDUxQzM0OC4zODkgNC45NzI2NiAzNDguNTIxIDQuNzgyNDUgMzQ4LjY4NSA0LjU1MTYyQzM0OC44NDcgNC4zMTg5MiAzNDguNzg5IDMuOTM5MDIgMzQ4LjU1OCAzLjcwNzdMMzQ4Ljk4IDMuNDU0NDRDMzQ5LjQwMiAzLjIwMTE2IDM0OS4zMTggMy42MzQ4IDM0OS41NzEgMi45NTM5N0MzNDkuODIyIDIuMjcxMjcgMzQ5LjU3MSAyLjg2Mzc3IDM0OS44MjIgMi4yNzEyN0MzNDkuOTA2IDIuMDc4NzUgMzQ5Ljk2MiAxLjk0ODM4IDM0OS45OTggMS44NjA5OUMzNTQuMTI2IDIuNTEyMzkgMzU3Ljk2MyA0LjA0OTc3IDM2MS4zMDcgNi4yNzEyMUMzNjEuMjAzIDYuNDE0MiAzNjEuMDQ3IDYuNTg4NDggMzYwLjgxNyA2Ljc0NzM3QzM2MC4zMjcgNy4wODUyMSAzNjAuOTY5IDcuNzYxMzkgMzYwLjgxNyA4LjA5OTI3QzM2MC42NjUgOC40MzcxMSAzNjAuODE3IDguOTQyNyAzNjAuODE3IDguOTQyN0MzNjAuODE3IDguOTQyNyAzNjEuOTgzIDkuODcxMiAzNjIuMzY2IDEwLjAzOTlDMzYyLjU0NSAxMC4xMTg1IDM2Mi43ODYgMTAuNDAxMSAzNjMuMDQ0IDEwLjczMDJDMzYzLjAxMyAxMC43NzQxIDM2Mi45OTYgMTAuNzk5NyAzNjIuOTk2IDEwLjc5OTdDMzYyLjk5NiAxMC43OTk3IDM2Mi45MTkgMTAuODg0NCAzNjIuMzY2IDExLjEzNzVDMzYxLjgxMSAxMS4zOTA4IDM2MC44MTcgMTEuODk2OCAzNjAuODE3IDExLjg5NjhDMzYwLjgxNyAxMS44OTY4IDM1OS43ODcgMTIuMjM1MyAzNTkuNzAzIDExLjg5NjhDMzU5LjYxOCAxMS41NTkgMzU4Ljg1OCAxMS4zOTA4IDM1OC44NTggMTEuMzkwOEMzNTguODU4IDExLjM5MDggMzU4LjUyIDExLjA1MyAzNTguMSAxMC44ODM5QzM1Ny42NzYgMTAuNzE0NyAzNTcuMTY5IDEwLjI5MjIgMzU3LjE2OSAxMC4yOTIyQzM1Ny4xNjkgMTAuMjkyMiAzNTYuNDExIDEwLjAzODkgMzU2LjA3MSAxMC4zNzY3QzM1NS43MzMgMTAuNzE0NyAzNTQuNzIyIDEwLjk2OTMgMzU0LjU1NCAxMS41NTk1QzM1NC4zODUgMTIuMTUwNiAzNTQuMTMxIDEyLjc0MjcgMzU0LjA0NyAxMy4wNzkxQzM1My45NiAxMy40MTY5IDM1Mi45NDkgMTQuNjgzMiAzNTIuNjExIDE1LjAyMDJDMzUyLjI3MyAxNS4zNTggMzUxLjg1MSAxNi4wMzQ0IDM1Mi4xMDQgMTYuMzcyMkMzNTIuMzU4IDE2LjcxIDM1My4wMzMgMTcuNTU0OSAzNTMuMjg3IDE3LjM4NkwzNTMuNTQgMTcuMjE2OUwzNTQuNzIyIDE4LjA2MDlDMzU0LjcyMiAxOC4wNjA5IDM1NS42OTUgMTUuOTc4NiAzNTUuNjMyIDE1Ljk2NDZDMzU1LjU2NyAxNS45NDk3IDM1NS4yNTEgMTQuNzY2NiAzNTUuNjYxIDE0LjUxNDNDMzU2LjA3NCAxNC4yNjA5IDM1Ni4zMjcgMTIuOTkzNyAzNTYuNTggMTMuMjQ3QzM1Ni44MzQgMTMuNTAwMSAzNTYuMjQzIDE1LjM1NzggMzU2LjI0MyAxNS4zNTc4TDM1Ny42NzggMTUuOTY0NEMzNTcuNjc4IDE1Ljk2NDQgMzU4LjY4OSAxNS40NzEyIDM1OC4yNjkgMTUuOTY0NEMzNTcuODQ3IDE2LjQ1NTkgMzU3LjA4NyAxNi45NjMzIDM1Ny4wMDMgMTcuMjE2MkMzNTYuOTE4IDE3LjQ2OTUgMzU1LjYzMiAxOC45MDQ5IDM1NS42MzIgMTguOTA0OUgzNTQuNTU2QzM1NC41NTYgMTguOTA0OSAzNTMuNjI1IDE4LjU2NzEgMzUzLjAzMyAxOC45MDQ5QzM1Mi40NDIgMTkuMjQyNyAzNTEuMjYgMjAuNDI0NiAzNTEuMjYgMjAuNDI0NlYyMS42MDcxQzM1MS4yNiAyMS42MDcxIDM1MC40MTUgMjEuMTAwMiAzNTAuMjQ3IDIxLjYwNzFDMzUwLjA3OCAyMi4xMTQzIDM1MC4yNDcgMjIuNzQ0IDM1MC4yNDcgMjIuNzQ0TDM1MC41ODQgMjMuNDY0M0MzNTAuNTg0IDIzLjQ2NDMgMzUwLjQyIDIzLjc4MjggMzQ5Ljc4NiAyMy44NzY5QzM0OS4xNTEgMjMuOTcxMiAzNDguOTggMjMuMzY5IDM0OC44MTMgMjMuODgxOUMzNDguNjQyIDI0LjM5NDIgMzQ4LjgxMyAyNS4xNTQgMzQ4LjgxMyAyNS4xNTRMMzQ4LjczNiAyNi4xMTk5QzM0OC43MzYgMjYuMTE5OSAzNDkuMTUxIDI0LjgwNjggMzQ5LjA2NyAyNi4xMTk5QzM0OC45OCAyNy40MzI5IDM0OS42NTggMjYuMzM1NiAzNDguOTggMjcuNDMyOUMzNDguMzA3IDI4LjUzMDEgMzQ4Ljk4IDI3LjY4NjMgMzQ4LjMwNyAyOC41MzAxQzM0Ny42MzEgMjkuMzc0MSAzNDcuNjMxIDI5LjcxOTggMzQ3LjEyNCAzMC40MzMzQzM0Ni42MTUgMzEuMTQ5MiAzNDYuNDU4IDMxLjkwODUgMzQ2LjE1OSAzMi4xMTg5QzM0NS44NTggMzIuMzMxIDM0Ni4yMDUgMzIuNTAwMiAzNDYuMTU5IDMyLjgzNzVDMzQ2LjExMSAzMy4xNzUzIDM0Ni4xNTkgMzQuMTg4IDM0Ni4xNTkgMzQuMTg4QzM0Ni4xNTkgMzQuMTg4IDM0Ni43ODcgMzUuNDU1MiAzNDYuOTU1IDM1LjcwODZDMzQ3LjEyNCAzNS45NjMxIDM0Ny4yMDkgMzYuMjE2NSAzNDcuNTQ3IDM2LjYzOEMzNDcuODg0IDM3LjA2MDUgMzQ3Ljg4NCAzNy4wNjA1IDM0Ny44ODQgMzcuMDYwNUMzNDcuODg0IDM3LjA2MDUgMzQ4LjY0NCAzNi44MDcxIDM0OC44OTggMzcuMDYwNUMzNDkuMTUxIDM3LjMxMzYgMzQ5LjE1MSAzNy4zMTM2IDM0OS4xNTEgMzcuMzEzNkgzNTAuMzMzQzM1MC41ODcgMzcuMzEzNiAzNTAuNzU2IDM3LjQ4MjMgMzUxLjAwOSAzNy4zMTM2QzM1MS4yNiAzNy4xNDM1IDM1MS45MzYgMzYuODkxMyAzNTEuOTM2IDM2Ljg5MTNMMzUyLjk1MSAzNy4zODY5TDM1My43OTMgMzcuNzM1MUMzNTQuMDQ3IDM4LjQwOTUgMzUzLjYyNSAzOS4yNTM4IDM1My44NzggMzkuNTkxOEMzNTQuMTMxIDM5LjkyOTYgMzU0LjcyMiA0MC43NzQ4IDM1NC45NzggNDAuNzc0OEMzNTUuMjI5IDQwLjc3NDggMzU1LjYzMiA0MS4xMTI5IDM1NS42MzIgNDEuMTEyOVY0Mi43MTUzTDM1NS4yMzIgNDMuNjQzN0wzNTUuMTQ3IDQ0LjE1MjFDMzU1LjE0NyA0NC4xNTIxIDM1NC45NzggNDQuOTk1NCAzNTUuMTQ3IDQ1LjUwMzFDMzU1LjMxNCA0Ni4wMDkgMzU1LjQwOCA0Ny4xOTEzIDM1NS43IDQ3LjQ0MzdDMzU1Ljk4OSA0Ny42OTY4IDM1Ni4xNTggNDguNTQxOCAzNTYuMTU4IDQ4LjU0MThMMzU2LjgzNCA0OS45NzgyQzM1Ni44MzQgNDkuOTc4MiAzNTguMzU0IDQ5LjQ3MTMgMzU4Ljg2IDQ5LjMwMjZDMzU5LjM2NyA0OS4xMzM5IDM1OS43ODkgNDguNzEgMzYwLjEyNyA0Ny44NjZDMzYwLjQ2NSA0Ny4wMjI3IDM2MC40OTkgNDYuMDk0MiAzNjAuODIgNDUuODQwOUMzNjEuMTQxIDQ1LjU4NzUgMzYxLjU2MyA0NS4xNjQ1IDM2MS45MDEgNDQuNzQyM0MzNjIuMjM4IDQ0LjMxOTggMzYyLjk5NiA0My4zMDcxIDM2My4wODEgNDIuOTY3OUMzNjMuMTY3IDQyLjYzMSAzNjIuOTE0IDQwLjUxOTggMzYyLjkxNCA0MC41MTk4QzM2Mi45MTQgNDAuNTE5OCAzNjIuNzQ1IDM5LjkyODYgMzYzLjA4MSAzOS41OTEzQzM2My40MjEgMzkuMjUzNSAzNjQuNTE2IDM4LjA3MTcgMzY0LjY4NSAzNy43MzQ2QzM2NC44NTQgMzcuMzk2NCAzNjUuOTU0IDM2LjA0NjEgMzY2LjAzNiAzNS43OTIzQzM2Ni4xMjEgMzUuNTM4OSAzNjYuMjkgMzQuMzU1OSAzNjYuMDM2IDM0LjUyNDZDMzY1Ljc4MyAzNC42OTUyIDM2NC43NyAzNS4yMDA2IDM2NC43NyAzNS4yMDA2QzM2NC43NyAzNS4yMDA2IDM2NC4wMSAzNC4xMDIxIDM2NC4zNDcgMzQuMTg2NUMzNjQuNjg1IDM0LjI3MjIgMzY2LjAzNiAzMy45OTEzIDM2Ni43OTYgMzMuNDU2MkMzNjcuNTU2IDMyLjkyMTIgMzY4LjU3IDMxLjczODkgMzY4LjU3IDMxLjczODlWMzAuNDMyNkMzNjguNTcgMzAuNDMyNiAzNjguMTQ4IDMwLjEzNDQgMzY3Ljg5NCAzMC4wNTAyQzM2Ny42NDEgMjkuOTY1NyAzNjYuODgxIDI5Ljg4MSAzNjYuODgxIDI5Ljg4MUwzNjYuMjA1IDI5LjI4OTZDMzY2LjIwNSAyOS4yODk2IDM2NC41MTYgMjguMTkyMyAzNjUuMTA3IDI4LjI3NkMzNjUuNjk5IDI4LjM2IDM2Ny45NzkgMjkuMjg5NiAzNjcuOTc5IDI5LjI4OTZDMzY3Ljk3OSAyOS4yODk2IDM2OS40MTQgMjkuMzczNiAzNjkuNjY4IDI5LjI4OTZDMzY5LjkyMSAyOS4yMDQ5IDM3MS4zNTcgMzAuMjI1NiAzNzEuNjEgMzAuNDMyNkMzNzEuODYzIDMwLjY0MTMgMzcyLjUzNyAzMS42NTQgMzcyLjg3NCAzMi4xMThDMzczLjIxMiAzMi41ODM0IDM3My44OSAzMy40NTU5IDM3My44OSAzMy40NTU5QzM3My44OSAzMy40NTU5IDM3My44OTMgMzMuNDczOCAzNzMuOSAzMy41MDQ0QzM3Mi4yMDEgNDcuNjUxNSAzNjAuMTMgNTguNjQ4NiAzNDUuNTM3IDU4LjY0ODZaIgogIGZpbGw9IiMwMDNENzEiCi8+Cjwvc3ZnPg==%0A"
            alt="Portfolioone"
            style="box-sizing: border-box; margin-bottom: 20px"
          />

          <div
            class="greet"
            style="
              box-sizing: border-box;
              letter-spacing: 0;

              text-align: center;
              width: 60%;
              margin: auto;
            "
            width="60%"
          >
            <p style="margin: 0; padding: 0">
              Hi <span style="font-weight: bold">{ name }</span>,
            </p>
            <p style="margin: 0; padding: 0">
              You're almost ready to get started. Please click on the button below to verify your email address and enjoy our services.
            </p>
          </div>
        </div>
      </header>

      <section
        class="main-content"
        style="
          background-color: white;
          border-radius: 6px;
          padding: 63px, 267px, 146px, 266px;
          text-align: center;
          max-width: 80%;
          min-height: 350px;
          margin: auto;
        "
      >
        <div style="display: inline-block; margin: auto">
          <div
            class="content"
            style="
              margin: 20px;
              padding: 10px;
              border-bottom: 1px solid #e5e5e5;
              max-width: 579px;
            "
          >

          <a
            class="button"
            href="https://portfolioone.io/verify_email?token={token}"
            style="
              background-color: #3490ec;
              border-radius: 60px;
              color: white;
              margin: auto;
              padding: 20px 100px;
              display: block;
              width: 30%;
              margin-top: 40px;
              margin-bottom: 40px;
              text-decoration: none;
              text-transform: uppercase;
            "
            >Verify your email</a
          >


          </div>
          <p style="margin: 0; padding: 0; max-width: 579px">
            You can now access PortfolioOne online or on any device by going to
            <a href="https://portfolioone.io">https://portfolioone.io</a>
          </p>
 
        </div>
      </section>

      <!-- <section
        class="app-advt"
        style="
          background-color: white;
          border-radius: 6px;
          margin: auto;
          margin-top: 40px;
          text-align: center;
          max-width: 80%;
        "
      >
        <h2>Get the PortfolioOne app!</h2>
        <p
          style="
            margin: 0;
            padding: 0;
            max-width: 669px;
            margin: auto;
          "
        >
          Get the most out of PortfolioOne by installing our mobile app. You can
          log in using your existing email address and password.
        </p>
        <img
          style="margin-top: 40px"
          src="data:image/svg+xml;base64,ICAgICAgICA8c3ZnCndpZHRoPSIyNzkiCmhlaWdodD0iMTAwIgp2aWV3Qm94PSIwIDAgMjc5IDEwMCIKZmlsbD0ibm9uZSIKeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgp4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayIKPgo8cmVjdAogIHg9IjAuODE5NjcyIgogIHk9IjAuODE5NjcyIgogIHdpZHRoPSIyNzcuMzYxIgogIGhlaWdodD0iOTguMzYwNyIKICByeD0iNDkuMTgwMyIKICBmaWxsPSJibGFjayIKLz4KPHJlY3QKICB4PSIwLjgxOTY3MiIKICB5PSIwLjgxOTY3MiIKICB3aWR0aD0iMjc3LjM2MSIKICBoZWlnaHQ9Ijk4LjM2MDciCiAgcng9IjQ5LjE4MDMiCiAgc3Ryb2tlPSIjMDAwMDFFIgogIHN0cm9rZS13aWR0aD0iMS42MzkzNCIKLz4KPHJlY3QgeD0iMjIuNSIgeT0iMTMiIHdpZHRoPSIyMzQiIGhlaWdodD0iNzQiIGZpbGw9InVybCgjcGF0dGVybjApIiAvPgo8ZGVmcz4KICA8cGF0dGVybgogICAgaWQ9InBhdHRlcm4wIgogICAgcGF0dGVybkNvbnRlbnRVbml0cz0ib2JqZWN0Qm91bmRpbmdCb3giCiAgICB3aWR0aD0iMSIKICAgIGhlaWdodD0iMSIKICA+CiAgICA8dXNlCiAgICAgIHhsaW5rOmhyZWY9IiNpbWFnZTBfMTcxN180MCIKICAgICAgdHJhbnNmb3JtPSJtYXRyaXgoMC4wMDIxMjI0MSAwIDAgMC4wMDY3MTE0MSAtMC4wMDUxMzM5NCAwKSIKICAgIC8+CiAgPC9wYXR0ZXJuPgogIDxpbWFnZQogICAgaWQ9ImltYWdlMF8xNzE3XzQwIgogICAgd2lkdGg9IjQ3NiIKICAgIGhlaWdodD0iMTQ5IgogICAgeGxpbms6aHJlZj0iZGF0YTppbWFnZS9wbmc7YmFzZTY0LGlWQk9SdzBLR2dvQUFBQU5TVWhFVWdBQUFkd0FBQUNWQ0FZQUFBRHlnMHZsQUFBTVBXbERRMUJKUTBNZ1VISnZabWxzWlFBQVNJbVZWd2RZVThrV25sdVNrSkNFRWdoRlN1aE5FSkdPbEJCYXBFb1ZiSVFrUUNnaEJvS0t2U3dxdUhZUkFVWFJWUkVGMXdMSVdoRzdpMkR2Q3lvcXlycFlzSmMzS2FEcnZ2SzkrYjY1ODk5L3p2em56TGx6NzUwQlFPTVlUeUxKUVRVQnlCVVhTR05EQTFuamtsTllwRWVBREppd0dnTTlIajlmd282SmlRQ3dETFovTDIrdUFVVGVYbmFVYS8yei83OFdMWUV3bnc4QUVnTnhtaUNmbnd2eGZnRHdLcjVFV2dBQVVjNWJUQzJReURHc1FFY0tBNFI0c1J4bktIR1ZIS2NwOFI2RlRYd3NCK0kyQU5Tb1BKNDBBd0I2QitSWmhmd01xRUh2aDloWkxCQ0pBZEJnUWV5WG01c25nRGdWWWx0b0k0RllydStaOXAxT3h0ODAwNFkwZWJ5TUlheWNpNktvQllueUpUbTg2ZjluT3Y1M3ljMlJEZnF3aHBXYUtRMkxsYzhaNXUxR2RsNjRIRk1oN2hPblJVVkRyQTN4TzVGQVlROHhTc21VaFNVbzdWRWpmajRINWd3K2FZQTZDM2hCNFJBYlFSd2l6b21LVVBGcDZhSVFMc1J3aGFEVFJBWGNlSWoxSVY0c3pBK09VOWxza3ViRnFueWhqZWxTRGx2Rm4rRkpGWDdsdnU3SnNoUFlLdjJYbVVLdVNoK2pGMlhHSjBGTWdkaXlVSlFZQlRFZFlxZjg3TGh3bGMzb29reE8xS0NOVkJZcmo5OFM0bGloT0RSUXFZOFZwa3REWWxYMkpibjVnL1BGTm1XS3VGRXF2TGNnTXo1TW1SK3NqYzlUeEEvbmduVUl4ZXlFUVIxaC9yaUl3YmtJaEVIQnlybGpUNFRpaERpVnpqdEpRV0NzY2l4T2tlVEVxT3h4YzJGT3FKdzNoOWcxdnpCT05SWlBMSUFMVXFtUHAwc0tZdUtWY2VKRldid3hNY3A0OEJVZ0FuQkFFR0FCR2F4cElBOWtBVkY3WDFNZnZGUDJoQUFla0lJTUlBU09LbVp3UkpLaVJ3eXZjYUFJL0FtUkVPUVBqUXRVOUFwQkllUS9EN0hLcXlOSVYvUVdLa1prZzBjUTU0SndrQVB2WllwUjRpRnZpZUFoWkVULzhNNkRsUS9qellGVjN2L3YrVUgyRzhPR1RJU0trUTE2WkdrTVdoS0RpVUhFTUdJSTBRNDN4UDF3SHp3Q1hnTmdkY0U5Y2EvQmVYeXpKendpZEJMdUU2NFN1Z2czSjR2bVMzK0lNaEowUWYwUVZTN1N2czhGYmcwMTNmQkEzQmVxUTJXY2lSc0NSOXdWK21Iai90Q3pHMlE1cXJqbFdXSDlvUDIzR1h6M05GUjJaR2N5U3RZakI1QnRmeHhKdDZlN0RhbkljLzE5ZnBTeHBnM2xtelBVODZOL3puZlpGOEEyL0VkTGJERzJEenVOSGNmT1lvZXdKc0RDam1MTjJBWHNzQndQcmE2SGl0VTE2QzFXRVU4MjFCSDl3OS9nazVWbk10KzV6cm5YK1pPeXIwQTRUZjZOQnB3OHlYU3BLQ096Z01XR2Z3UWhpeXZtT3cxbnVUaTd1QUFnLzc4b1AxK3ZtSXIvQnNJODk0MmJjZ3dBcnhKSVpuemplQllBSEh3RUFPUE5OODdpSlh4dFZnQnd1SU12a3hZcU9WeCtJY0N2aEFaODB3eUFDYkFBdG5BK0xzQWQrSUFBRUF6R2dHZ1FENUxCSkJoOUpsem5VakFWekFUelFERW9CU3ZBV2xBQnFzRVdzQVBzQm50QkV6Z0Vqb05UNER6b0FGZkJiYmg2ZXNBejBBL2VnSThJZ3BBUUdzSkFEQkJUeEFweFFGd1FUOFFQQ1VZaWtGZ2tHVWxGTWhBeElrTm1JZ3VRVW1RVlVvRnNSbXFSWDVHRHlISGtMTktKM0VTNmtWN2tKZklCeFZBcXFvTWFvOWJvQ05RVFphUGhhRHc2RWMxQXA2QkY2RUowR1ZxTzFxQzcwRWIwT0hvZXZZcDJvYy9RQVF4ZzZoZ1RNOE1jTVUrTWcwVmpLVmc2SnNWbVl5VllHVmFEMVdNdDhEbGZ4cnF3UHV3OVRzUVpPQXQzaENzNERFL0ErZmdVZkRhK0ZLL0FkK0NOZUJ0K0dlL0crL0V2QkJyQmlPQkE4Q1p3Q2VNSUdZU3BoR0pDR1dFYjRRRGhKSHlYZWdodmlFUWlrMmhEOUlEdllqSXhpemlEdUpTNGdkaEFQRWJzSkQ0Z0RwQklKQU9TQThtWEZFM2lrUXBJeGFUMXBGMmtvNlJMcEI3U096VjFOVk0xRjdVUXRSUTFzZHA4dFRLMW5XcEgxQzZwUFZiN1NOWWtXNUc5eWRGa0FYazZlVGw1SzdtRmZKSGNRLzVJMGFMWVVId3A4WlFzeWp4S09hV2VjcEp5aC9KS1hWM2RYTjFMZmF5NlNIMnVlcm42SHZVejZ0M3E3Nm5hVkhzcWh6cUJLcU11bzI2bkhxUGVwTDZpMFdqV3RBQmFDcTJBdG94V1N6dEJ1MGQ3UjJmUW5laGN1b0EraDE1SmI2UmZvai9YSUd0WWFiQTFKbWtVYVpScDdOTzRxTkduU2RhMDF1Um84alJuYTFacUh0Uzhyam1neGRBYXFSV3RsYXUxVkd1bjFsbXRKOW9rYld2dFlHMkI5a0x0TGRvbnRCOHdNSVlGZzhQZ014WXd0akpPTW5wMGlEbzJPbHlkTEoxU25kMDY3VHI5dXRxNnJycUp1dE4wSzNVUDYzWXhNYVkxazh2TVlTNW43bVZlWTM3UU05Wmo2d24xbHVqVjYxM1NlNnMvVEQ5QVg2aGZvdCtnZjFYL2d3SExJTmdnMjJDbFFaUEJYVVBjME41d3JPRlV3NDJHSnczN2h1a004eG5HSDFZeWJPK3dXMGFva2IxUnJORU1veTFHRjR3R2pFMk1RNDBseHV1TlR4ajNtVEJOQWt5eVROYVlIREhwTldXWStwbUtUTmVZSGpWOXl0SmxzVms1ckhKV0c2dmZ6TWdzekV4bXR0bXMzZXlqdVkxNWd2bDg4d2J6dXhZVUMwK0xkSXMxRnEwVy9aYW1scEdXTXkzckxHOVprYTA4clRLdDFsbWR0bnByYldPZFpMM0l1c242aVkyK0RkZW15S2JPNW80dHpkYmZkb3B0amUwVk82S2RwMTIyM1FhN0RudlUzczArMDc3Uy9xSUQ2dUR1SUhMWTROQTVuRERjYTdoNGVNM3c2NDVVUjdaam9XT2RZN2NUMHluQ2FiNVRrOVB6RVpZalVrYXNISEY2eEJkbk4rY2M1NjNPdDBkcWp4d3pjdjdJbHBFdlhleGQrQzZWTGxkRzBVYUZqSm96cW5uVUMxY0hWNkhyUnRjYmJneTNTTGRGYnExdW45MDkzS1h1OWU2OUhwWWVxUjVWSHRjOWRUeGpQSmQ2bnZFaWVBVjZ6ZkU2NVBYZTI5Mjd3SHV2OTE4K2pqN1pQanQ5bm95MkdTMGN2WFgwQTE5elg1N3ZadDh1UDVaZnF0OG12eTUvTTMrZWY0My8vUUNMQUVIQXRvREhiRHQyRm5zWCszbWdjNkEwOEVEZ1c0NDNaeGJuV0JBV0ZCcFVFdFFlckIyY0VGd1JmQy9FUENRanBDNmtQOVF0ZEVib3NUQkNXSGpZeXJEclhHTXVuMXZMN1Ivak1XYldtTFp3YW5oY2VFWDQvUWo3Q0dsRVN5UWFPU1p5ZGVTZEtLc29jVlJUTklqbVJxK092aHRqRXpNbDVyZXh4TEV4WXl2SFBvb2RHVHN6OW5RY0kyNXkzTTY0Ti9HQjhjdmpieWZZSnNnU1doTTFFaWNrMWlhK1RRcEtXcFhVTlc3RXVGbmp6aWNiSm91U20xTklLWWtwMjFJR3hnZVBYenUrWjRMYmhPSUoxeWJhVEp3Mjhld2t3MGs1a3c1UDFwak1tN3d2bFpDYWxMb3o5Uk12bWxmREcwampwbFdsOWZNNS9IWDhaNElBd1JwQnI5Qlh1RXI0T04wM2ZWWDZrd3pmak5VWnZabittV1daZlNLT3FFTDBJaXNzcXpycmJYWjA5dmJzcnpsSk9RMjVhcm1wdVFmRjJ1SnNjVnVlU2Q2MHZFNkpnNlJZMGpYRmU4cmFLZjNTY09tMmZDUi9ZbjV6Z1E3Y3lGK1EyY3Ara25VWCtoVldGcjZibWpoMTN6U3RhZUpwRjZiYlQxOHkvWEZSU05Fdk0vQVovQm10TTgxbXpwdlpQWXM5YS9Oc1pIYmE3Tlk1Rm5NV3p1bVpHenAzeHp6S3ZPeDV2ODkzbnI5cS91c0ZTUXRhRmhvdm5Mdnd3VStoUDlVVjA0dWx4ZGNYK1N5cVhvd3ZGaTF1WHpKcXlmb2xYMG9FSmVkS25VdkxTajh0NVM4OTkvUEluOHQvL3Jvc2ZWbjdjdmZsRzFjUVY0aFhYRnZwdjNMSEtxMVZSYXNlckk1YzNiaUd0YVpremV1MWs5ZWVMWE10cTE1SFdTZGIxMVVlVWQ2ODNuTDlpdldmS2pJcnJsWUdWalpVR1ZVdHFYcTdRYkRoMHNhQWpmWFZ4dFdsMVI4MmlUYmQyQnk2dWJIR3VxWnNDM0ZMNFpaSFd4TzNudjdGODVmYWJZYmJTcmQ5M2k3ZTNyVWpka2RiclVkdDdVNmpuY3ZyMERwWlhlK3VDYnM2ZGdmdGJxNTNyTi9jd0d3bzNRUDJ5UFk4L1RYMTEydDd3L2UyN3ZQY1Y3L2Zhbi9WQWNhQmtrYWtjWHBqZjFObVUxZHpjblBud1RFSFcxdDhXZzc4NXZUYjlrTm1oeW9QNng1ZWZvUnlaT0dScjBlTGpnNGNreHpyTzU1eC9FSHI1TmJiSjhhZHVOSTJ0cTM5WlBqSk02ZENUcDA0elQ1OTlJenZtVU5udmM4ZVBPZDVydW04Ky9uR0MyNFhEdnp1OXZ1QmR2ZjJ4b3NlRjVzN3ZEcGFPa2QzSHJua2YrbjQ1YURMcDY1d3I1eS9HblcxODFyQ3RSdlhKMXp2dWlHNDhlUm16czBYdHdwdmZidzk5dzdoVHNsZHpidGw5NHp1MWZ4aDkwZERsM3ZYNGU2ZzdndjM0KzdmZnNCLzhPeGgvc05QUFFzZjBSNlZQVFo5WFB2RTVjbWgzcERlanFmam4vWThreno3MkZmOHA5YWZWYzl0bisvL0srQ3ZDLzNqK250ZVNGOThmYm4wbGNHcjdhOWRYN2NPeEF6Y2U1UDc1dVBia25jRzczYTg5M3gvK2tQU2g4Y2ZwMzRpZlNyL2JQZTU1VXY0bHp0ZmM3OStsZkNrUE1WV0FJTVZUVThINE9WMkFHakpjTzhBejJlVThjcnpuNklneWpPckFvSC9oSlZuUkVWeEIyQjdBQUFKY3dHSWdIdVVqYkJhUVV5RnJYd0xIeDhBMEZHamh1cmdXVTF4cnBRWElqd0hiTEtYbzR1ajZkWGdoNkk4YzM0WDk0OHRrS3U2Z2gvYmZ3RU5BM20zNWFRdk9RQUFBRGhsV0VsbVRVMEFLZ0FBQUFnQUFZZHBBQVFBQUFBQkFBQUFHZ0FBQUFBQUFxQUNBQVFBQUFBQkFBQUIzS0FEQUFRQUFBQUJBQUFBbFFBQUFBRHpHeHlHQUFCQUFFbEVRVlI0QWUyZENkeDFVNzNIZDZPbTJ5Qmw1blZMaHRRdE1vZlhsRWdoU2Nyd2txRkNwaWhEcGlRaGlreHg2OVdBVW5FUkVyMjRobXVzWk00VWlnWXFwY2l0ZFgvZnBYWHVQdnVzdGM4Kys1enpQT2ZzOC85L1B1czV6OWxuNzdYWCt1MjExMzljLzVWbFJvYUFJV0FJR0FLR2dDRmdDQmdDaG9BaFlBZ1lBb2FBSVdBSUdBS0dnQ0ZnQ0JnQ2hvQWhZQWdZQW9hQUlXQUlHQUtHZ0NGZ0NCZ0Nob0FoWUFnWUFvYUFJV0FJR0FLR2dDRmdDQmdDaG9BaFlBZ1lBb2FBSVRCbUNEeG55TzJsL2hmOXE3eEFuODlUNGZPbC8vclVoNUVoWUFnWUFvYUFJVEF0Q1B4ZGQvMnJ5ak1xLzFCNVdvVmpUNms0bFlIU01CZ3VkYjVNWlg2VkJWUldWVmxDWlRHVmVWUmd0akJoR0srUklXQUlHQUtHZ0NFd0hRakFxMkN1ZjFPQjZmNVc1WmNxZDZqY29QS2d5aU1xVDZyOFU2VnY0b2FEb3VlcUlwanNHMVZXVWxsRFpUbVZWNmdZR1FLR2dDRmdDQmdDNDRMQW45VFFXMVF1VmJsVzVTY3FqNnYweFhnSHhYRFJXRGRRMlZBRmpYWXhGZE5nQllLUklXQUlHQUtHd05naWdLbjVmcFdyVlM1UXVWQUZjM010R2dURGZiUHV2STNLeGlvdzJrSFVxV3FNREFGRHdCQXdCQXlCa1VIZ1ByWGtYSlZUVmU2czB5cUNtT29TMTY2djhobVZUVlh3enhxekZRaEdob0FoWUFnWUFvMUQ0RlhxMGRJcXVFcng2OTZsMGxOZ1ZWMkdTK0RUamlxSHF1Q3pmYUdLa1NGZ0NCZ0Nob0FoMEdRRWNKL09VSG1iQ2xITnQ2cGdkcTVFZFJqdWdxcDVENVVEVlY2clVxY09YV1prQ0JnQ2hvQWhZQWlNSlFKb3V6TlZucTlDUUZVbHYyNnZ6QkpOZG0rVlQ2bVlWaXNRakF3QlE4QVFNQVFtRWdFQ2cxZFJJWEtab0NvMDNsTHFoZUhpbjkxTTVRZ1ZZN2Fsc05xUGhvQWhZQWdZQWhPQUFNdGhWMVFoaU9yMmJ2M3RoZUhDYkk5VUlUakt5QkF3QkF3QlE4QVFNQVNlTlNzdkx5RHVWdmxGR1NCVkdTNlpvZzVSZVV0WlpmYWJJV0FJR0FLR2dDRXdnUWk4UkgxZVJPVW1sZCttK2wrRjRXS24zbDlsQTVXNVVoWFpjVVBBRURBRURBRkRZRUlSZ0pjdXJJSWY5eklWL0xvZDFJM2g0cmZkU0dVWGxmazZycllEaG9BaFlBZ1lBb2FBSVFBQytITmZvL0pMRlh5NkhjUUpaVVRvTThrdEZpczd5WDR6QkF3QlE4QVFNQVFNQWM4cjRabFJCYldNNGFMZExxdXl1Z3IvR3hrQ2hvQWhZQWdZQW9aQUdnRjRKVHh6R1pVT3ZsbkdjTWttdGJMSzYxU01EQUZEd0JBd0JBd0JRNkE3QXZETWxWVFlwcmFOeWhqdVFqcHpOWlZ1ZnQ2MkN1MkxJV0FJR0FLR2dDRXd3UWpBTStHZCtIUGJLTVZ3VVlXeFFaTXYwc2dRTUFRTUFVUEFFREFFcWlQQUVscVdDYldabFZNTWx3VE5aTThnYU1ySUVEQUVEQUZEd0JBd0JLb2pnSFpMMnNlMnBiUXBoa3ZxUm5ZQk1qSUVEQUZEd0JBd0JBeUIzaEZZVXBlOE9IOFpPeDNFQ0s3TXJrQkcwNERBYzUvNzNPekZMMzV4OXM5Ly9qTjc2cW1uTXVkNjJuSnhHbHBzdHpRRURBRkR3QkFvSUxDd3ZwTTRxa1VwaG92VDF4aHVDNmJoLy9PODV6MHZXMnl4eGJLbGxsb3FtekZqUnJid3dndG4vL00vLzVQOTRBYy95SjUrK3VuaE44RHVZQWdZQW9hQUlUQklCSWlEYWdzNlRqRmN1UExMQjNsbnF5dU93RXRmK3RKcytlV1h6OTd4am5ka2IzM3JXN1BYdmU1MTJUenp6Sk85L09Vdno3Nzg1UzluUC9yUmo0emh4cUd6bzEwUVdIenh4Yk1OTnRqQWp5VUV1c3N1dXl6NzcvLys3eTVYamVmUHIzclZxN0lQZk9BRDJhdGYvV3B2RWJyNTVwdDlmLy8rOTcrUFo0ZW11ZFZ2ZWN0YnNvMDIyc2hqK2FjLy9TbTc4TUlMczEvOG9qUXYvelMzZUNSdi93cTFxbTFudlJURHhlNU1NbWFqSVNId25PYzhKMXRtbVdXeVhYZmROVnRycmJXeWVlZWROM3ZaeS81LzJSWm1aTTZoTklrd2w4K1FCdithMTd6R1Q0NThJblE4Ly9uUDkzMWxndno5NzMrZlBmamdnOW45OTkrZi9lNTN2ek9UZXMwQmdQREcrQUxqTUk2YXluQVJVai80d1E5bWIzN3ptejFhMy8vKzk3TXJyN3d5TTRaYmIvREFjUGZhYXk5LzhXOS8rOXZzM252dk5ZYmJPNVR3VUFLUVc1Uml1QnhQL2RhNjJQNnBqOENXVzI2WkhYamdnZDUwUE5kY2JZRnN2dEpubm5rbWUrS0pKekkrbTBSTExMRkVkdW1sbDJab1hEQlpQbUhDZ1NFZ2FORG4vLzNmLy9YTUZyUDZHV2Vja2MyWk02ZEpNRXhKWDhEMWhTOThvZGR3dVdIVFl3RVEzTEFNTVg3KzhZOS9UQW5HVGIwSlkrWGYvdTNmZlBmKytNYy8rbmlTcHZaMWlQM0NVdHpHUjl1KzVHNU1sRTZ6Vkt0YzU2YnJYNWpLYTEvNzJteS8vZmJMUHY3eGo1YzI0NjkvL1d2Mm05Lzh4Z2RObFo0NFpqOHlJUzZ3d0FLdFZoTVl4dVRJSndRRHBvQVZXajlXQUlRVFRGcWYvL3puczUvOTdHZG1ZbStoVi80UG1BWmNPYlBKRExmWXQzeS95MUdhbkY4UjdBbkc1SDM3ODUvL1hOcnhQSjdGY1ZSNm9mMVlpa0NLNFpaZVpELzJqZ0FNNU4vLy9kK3pJNDQ0SXR0NDQ0MjdWdkNYdi93bGUreXh4eG8zU2FLNUJ1TC9uL3prSjlrZGQ5emhKd0F3ZXNVclh1R0ZrZ1VYWE5EN3N2SEp2ZWhGTDhyZSs5NzNacTkvL2V1end3NDdMTHY0NG91N1RoamhIdlpwQ0V3NkFsZzYzdmpHTjNweis4eVpNNzJyaHZnUUxHaEdVNHVBTWR3cHdudUZGVmJJUHZPWnoyUnJyTEdHTjZWMnUrMnZmLzFyLzJKME8yK2NmMy84OGNlelF3NDV4R3V2UWFLRzZlTExYbVNSUmJJM3ZlbE5QbkFEQVFXbWkzL3VzNS85ckpmUUw3amdBdlBQamZQRHQ3WlBHUUlJc2QvOTduZDlRQ2JXbzltelozczN6cFExd0c3VVFzQVliZ3VLNGYyRGRQbUpUM3pDTTF0OGF0MElFdzRCUTNmZmZYZTNVOGY2ZDVoc0tLRWpmTWZjZGR0dHQvbHl6VFhYWkgvNHd4K3lqMzcwby80VUltOTMyR0dIN0thYmJzcCsrY3RmaHN2c2M4SVJRRkF6aWlQd3Q3LzlMWnR2dnZtOHE0WXorSjYzTk1XdnNxUERRTUFZN2pCUXpkVko5T1MyMjI2YnJiLysrajZBSmZkVDhsK0NGQWdXZ3RFMG1hcE1ra1FybjNEQ0NSbFJreXV2ek9aVjJ2dHE5ZFV6VEdObm5YVldWMy91QzE3d0FpL1pFNnpGMGhGODR3Z3ltTEhMMWpmajd5TEtGd0VKSVFEekcwSlFrZWdEenhnVE9JUVF3UFBqbWp4eEhpWnhBbnNnenVIY2NCNmFCNysvNUNVdjhSbzhGbzdnVWtEYnArLzR0SW02L2ZuUGY1N2RlT09OcGUzUDM3dk8vN2cvRUJUcEc4bFhIbjc0NGV5V1cyN0pXQ0pTbFRCbGdzdXl5eTdySjN6NmpqRDEwRU1QWlN6YklmcTFGK0o2Nm1LdE9nRTlqejc2cVBmcDMzNzc3UjJDV3kvMVZqMlgyQVBHSVZIZitFRi85YXRmK1g1VXdRUUxEYytYOGNnekJNOXdIZjFoYVNEakUzekFoajcxRzJITnMyUE1nRnZlcDgzeEpaZGMwbzhmQWhlSkZXRzhwWWl4Rzk1VjNvYzExMXpUdnh0Y3kvdjU0eC8vdUpaNW12aU01WlpiTHB0NzdybDlXKzY4ODg3cyt1dXZ6M0NuVFJvdHJRNC9xY0tzWWFVbUJocVE3djN2ZjcvVEpLOTV0VHJwaFhPYTdCcUp1MTZ3RmhCNjBaM1dpWGJ0cDVpUjIyYWJiWndZWk92YTczem5PMDcrM2VTMW10aWNsbHU1YjMvNzIwNk16V21wa1pNQTQyVEdkcG9vblJLS3VBMDMzTkJwSW96V29RbmR5VmZzSG5ua0VWL09QLzk4SitiUmNlNzg4OC92dnZDRkw3VE8rK1FuUCtsa0V1ODRUd3pNU1N2MzU5MXp6ejFPZ1hOdDUxQ1BsckU0TVJGL3p2dmU5ejZuU2M3dHNzc3V2djIwWFV6ZmFaSjJXaXJsKy9YS1Y3NnlyWTdpdS9yT2Q3N1RQZkRBQXkzTUZCVmZlajdYSy9tS08vcm9veDF0Rk1QM21IRnYyblgxMVZlNzdiZmYzb0ZOOFY3NTd4SldQTGFubjM2NjA5cE4zMTdhSGRvdlJ1c2tVUHBuS21aUVdsZW9WMHpKUHpNeEJvOEJkZEV1NnFkZlltYnVxcXV1Y21Jc1RvektmZVVyWDNGVjZ3NzNTSDBHVENTa09kck9mU21NcWFxWWlMazRMYTN4T041NjY2MU82Kzc5T0pHTHhORW42cU5QRXNRYzc4Vnh4eDFYQ1pkVW16bSs5OTU3KytkSWZSSVFXdVBneVNlZjlQZGdiUE51S0M2aTQxNWJiNzExNjN3Sm1tNjk5ZFp6Y29zNXVYTDg4NlNkUEZNd3VPS0tLNXlFNEk0NlVtMlQwT1FZR3hLODJ2ck51UDdoRDMvbzFsNTc3Y3AxcGU0eElzZmhvWlZTSkJ2RHJjbGs4dzk2eG93WlRsRzFyWUZiNVI5cEUrNm9vNDVxeW9EcjZFY2RoZ3VtVExnMzNIQkRDMEltaW9VV1dxaWpmczZGNFIxKytPRis0dVVDSm1Gd1paTElDei84LzZVdmZjbEpjNG5XYy9EQkI3Zk9od0hGSmdKcFBFNGFaNnRkV3VmcXBFRjAxS2Mxb3A2QmNTSjF2ZWM5NzJrN1I1cElxMzlhMXVJT09PQUFkL3p4eHpzbVI0Z0prMzdrNmRwcnIzWFNEdHJxeVkrL1hoaXVOQmN2SE41MzMzMnRXNEFaazZwTWtHMzMxckl1SjlOKzhyNkt4UGZDQXhYQi9BSnpZbkttem53L0ZFVG9wTlVuNjZJL3NtWTRXU1ZhN1FyMVVsZGdKREErbUMvZkI4Vnd5ekNCT2ViNzBRMFRXVXM4czZidDBncWRYQ1R1M0hQUGRUeHJLUFo4di9HTmJ6Z0V4L3d6N2VWL3hZdzRhY3d0alB5TjlJZDJjMS91aVJENzFhOSt0ZU1lZVlZcnk0WWZqd2dLVUt5dDFDTXR2YU9lZkhzVkllMTREeEE4SU5yQTJFQ3dBOCtBQmI5dHRkVldUaGFTMHZyeWRZL28veDBNMTB6S2VsTERvczAzMzd5MUVML3FQVEIzbm5UU1NWVlBuNWp6OUVKNk0vRGIzdmJzanBHWTkvQkxZWnJMRTZhN2ozM3NZOW0rKys3ckQrT3JBbE95TE4xMTExMFpwbVV4SXA5R2t5VVNMTS9DOUVuME02YTFQRjErK2VYWlJ6N3lFYitVQWhNbTExSlBJSzdEOUlwZk9SQm1Na3lPWWk3aGtQL0VGSWxwRDhJVUtXYnAvdzkvTkFtMklxOXA4MDQ3N2VRVGc0aXBlUE1pYmFOZTBuOWlFc1RFdC9UU1MyZDc3cmxuSnNHZ2I1OGNVZUNNTzJuTjNqd3JyY2IzbFNoeXNNYU1qem1YZ0RZSkh0bkpKNStjeVhyanpkNmhEK0VUSCtFbGwxeml6Wm40MmttMlFmc3htNU5ON2QzdmZyZHZPL2p0dHR0dW1hd0htUmhtdUx6dEU3TzJ0TDBXeHJnRU1FbExtL1dtN2tVWFhUUmpUS3kwMGtvZUUzQVJRMmlybys2WElpYjBnY3h2dUh1SW5zZTBpaWs0ajRrWVJkUThDeWFZaTNtR0xJMWphU0QvRXpoSVVna0pOaDVuM0FjOEE0aHhTdllzTWQ1YVhjQkV5M09nZlRQbGdzRWNEUEhPL1BTblAvVjRZUmJHakZ0R3RFbmFzaitGZDBnQ28zOG53SjVDSGRUTkNneXlVOFZNd3B4RGdwLzk5OS9mdnpNU0pEMk8zL3ptTjMzZnFXZVRUVGJKVmx4eHhReDN6dWMrOXptZmFBT3NKNEZNdysxVHc4WHNWcFRLa2R6S0NNbjh3eC8rOExoTGRhWHRyNnZoWWo3KzRoZS8yQWFmSnU2T2V5bWkyWnVOT1JHcEczUFhPdXVzNHpCejZzVjFtUG5YV0dNTko3OVRTME5Cc3RaYTM0NjZGTjNwTkRINWU2Sk5IWHZzc1cwYWh5Wk9wN1hCYlczaVMvRVpVZy9tYVRRTE5GYjZRVnZ5QmEzNG9vc3VhcXNMVFZqQmRnNUxDVnE3R0w0NzlOQkR2YVllVGhSRDlPYlVmRjNoLzZvYUxobys5d29rLzZIVDVPZXhvaTQwRFVXTU96U3V2SVVBa3lWNGh2dUZUODdIeEx2cXFxdDJtSFhSMk5CeThxWnV6S3JoMnVLbi9QZWhXVjViMDNJV0o2YmRPaC9jSkRSNTAyZzRjUkFhYmd5VFdiTm1PWjQ1YmNUY2o0dWhpTW1SUng0WnhRU1hnUmhnYUtML3hNV2crQTdIYjlUTHUzSGFhYWUxTUVhVHhQVVI3bG5FcHR0M05IVEdqUVRUbG5XRkczL3RhMTl6WXZiK04vbU5vMjZWdkliTE5XaWl1RTRrM1BobkN1NVNLRnBtZk01QlU4WDBIR3NYNCtHODg4N2pORytCT1BIRUV4MldrUHk1bUpvVkpPazFYZDVKek02RGNndms3ek9GLzNkb3VMcDNsSXpoRmlaRW9kUTJPTHA5bDBUcEIxY3ZmNVJSeWZHU2RLdDduSCt2eTNEeFZ4YVoyMmFiYmRhR0ZSUFQ5NzczdlpacFNscWFaeHhGdkpqME45MTAwN1pKSDhhS3lhdDRMbVpkQ0diNVgvLzFYMjNtWjh6QW1IV1pISUkvaW5PLy92V3Z0OVdENzB0UjEvemtmVjdTQXRwKzU1NElGSmdZQTJIR2xmYmEwU2JPd3k4TlU0RXdyZE9YWXJ2NVhwWGhTdXNJdC9XVDVqNzc3Tk1TVVBMMVN2dnd2dGR3c2dLMzNCdmU4SWJvdmZQWEZmK1h4dVRPUFBQTVVJMW5Lc1Z6K0k3TEFEY0FCUDc0N2JtMmVDN0NMY3dBOHlrMENJYUx5VGNRakFSTVlwTi9FUk5wajA3TDF6cmFDRlBOdXg3d1YzN29ReC9xZU44eFBjdXkwaklEWThibG5TbjJ1WmZ2TUYzdUZ3ai9kamMvZkpIaEtrRFJhVU9WdG5hRTJBcGNCUkRDWk13ZlRGdUpaWkhtNjg5RDBQaVAvL2dQTDdRVSs2RlVwTjY4ekluMEhRWmZQR2VNdm5jdzNOUit1T3FUVVQ4SVNLdnE2WElGQzJUeU8vWWRtZGpUVGNmb1pNeVJsRHhKZzgxLzlWRzFtSDB4WDJGV3hKeEpHc2tpaVVGNk0xcmVYTVdhWDB5MFJlSzVRSmdxTlduNjljSGhITXk3bUpBeGQ0dFordnZ4Mjl2Zi9uYS9iamljUnhRcWF5RWhUTTB4RTU3bWw3WklVbW1BUHAwbHBzZzhhZkwzWmsxTXpSRG1RakdtL0NrOS9VKzdNT1VGWWprV2ZTNWl5KytZSVRFUGgzc1RnWXdwdHdvUmlRcSttQXd4RTJQT0Q4UnZFb0xDMTlibnV1dXUyOElOMHl0clNXUFJ0SmhxTVoyS3FiU3U3ZWNmVFArc0tnZ1VNTUVNV3FRaUpyZ2VNSjBXaWVkTENjUjFpa25vZU44eEwxOTMzWFd0NHhJaXZkazJYRmZuRXhNdDR6Y1E3eEhtL0tvRXZpU2JJU284VCtFZEM3anpESEd4eE9yRy9BNnVZRURXT0tLYjgzaUVlbmxmQTg2NFRuZ3ZtMFRtd3gzQzAyUmc0YXVxU3J4Z0pIU1FSRmYxa29rN2owbUN5U3dRTDN2UlR3cXp4YmNHd1RCZ2JFd1dNV0pKQ25ncmVNbFAva3dTK0FKaDBubkN0OGhrRDFOZ0FnamJKbklPdmt3WW5nS05Xb255VjFsbEZYOE9UQmIvSiszbWY1WjhRTlJYbkxqOEQvcVRueFR4RjRhSkovd2VQdmxOV3B6L2luREJlS3RMK001Z25CQytZL3h6bEJpQktaaUJCMzVkN3N0U2x4UXgwVXM3OHo1YmZKMzRMR2t2L2o3K0R3VHpaVGtVZnN3OGNVMGcvTjc0SkZQclJ4RlFwQTJIMC92NnBHOUJpT2tWRS9vY0U5eG9VUDc1NGtjdEc1c0loY1FqTUg3NmViNTlBZkd2aTJWTzltT1dOaFVKWVRNSWhiU1ZjYzd6RFVKWk9KOXhBTUZrWWNyYmJMT05aOHg1VEtpZjl4Y2hBNkwveEdrMGlZemhEdUZwb3ZtRVNheXNlb0lMQ0JoaEU0UFVKRmQyL1NUOUJzUExUKzVNc0RLbnRrSEFSQmswSjE1NEdHR0tZQjVvUzB4NjRab3d5ZWF2WWJJaHE1Vk1iSDRTWmpKbFFtRWlEcHFoVE5kK2JTek1CR2JFczJkYlBCZ3VEQnJoQzRiQ1pDTnpjRlN5ejkrVC8yUFNmemluK0Z0KzBncm5WUDBFTTlvTkVaQkVYMUtNbm5OZ2ZKd0h3VndRUXBnWWl4TXNXY0UrL2VsUCt5QWFOQjhtVTg0Sm1qUEg2QWR0UjlpSjlZRmduVUFJU0dDYklnU3dJaTZwYzdzZForMXFHQk85WWdLV1hNL3pEamgxdTEveDkzdy84djhYejV1cTc3MjBJYWJkZ3NtTUdUTjhjL2xkUG54ZnVyV2ZjMk9XajI3WGpmTHZ4bkNIOEhTUThwaUV5Z2d0UlFFU21md3AzcnhTZHE3OWx2bjh5cGh2QTVIOG9jZ1k4cE0yazBSS0d3cDE4RUxuSndnaWhXT0VtWXZvVTE1K21ENGJVSEF2bUFyM2dMSEQvUGtkclJzbVJsUXZVWnRJODVpaUlUU3dWRFJ1N0w2cFk4VitwczZyY3B6KzUrdExZUkRxQXRmOEJNeTErZXM1RDQyZVpDV1kxaUcwT2FLeUwxZlVONlpFdEhNbTNTMjIyTUlMTC82a3lKOGdDUEJUL3A2UlV3ZDZhQmlZOU5MQUlwNjlYRHNkNStiYkczdE9DS2hCZ09GM0JLY3k0U24wZ2ZkYmE0WEQxMFo4R3NNZHdtUEVMNWFTelBCM2tFV0djSGkybmFzckJRK2gyU05iSlNZbUpRcndqSTVHb3Myd1BDZVlza0xEZVVINURXS3lEc3Nyd3UvNVQ4eGYvSTZXRmlnMUNlQnJ3M2VLTm9mV3hhZUNoZnd6eGp4TTFpZmFncFVDNW91UEVxYURwb08xZzA4SVAyTlJTQWozbnE1UFRJSUJNOFlzV0lOTk9GWnNGNVlHSmxBSXJSVUxRTkJhdzduc3dSdVlMVllFUlZabkNpUnJuUWREUSt0UDNTUFVrOWVhY1NkZ3ZrOVJmdEpQblZQMU9KYW5JS3oxaWdsOUFwUGkyS3g2NzZrNEw4WVVoM2xmeGdmam51Y0hQaWdaQ0xIZG5obS9OODNOWmd4M0NDT05DU3RvVGd4dUJoc2FFT2tFdFV6RnAwS0Q2UnBWUTRCQW0xbXpaclZPQmp0eUxBYy9admlCeVIyc0ExTWdmVjJLWUxha2Jzejd4MGhkR0NPRUpBS3NsSm5LYTZzdzNPQ1RZbkpseTBDSVNSWWZNTUlCRWoxcmIvR1IwaDVJeTM3ODV5ajl3VVFjR0J2Q3h3eVovbWh2Q0lRcHRoWE1RZ0FZL1VVRHlXdkZXSGRZT3dveDlsbTNTckJUbmluRHhMQUFoWGVrZUkvd25mVzJnVEQzWTZySGp4c2puZ2xtM0VFUTV1dmdYKzBWRXhnMTczb2VrMEcwcWQ4Njhzd3QvMysvOVZhNUhpWUxKZ2llekkyOHR3aXhBZU1xZFRUbG5PcWhhazNwOFJUMEEvL2kyV2VmbldtdG1VK29zUHZ1dTJjNzc3eXozOERnMUZOUDlScnVGRFJqTEc3UlRkb21oekMrd09BVGg2RmlIVUNUTEY2TG1Sa0dDS0dGd2FneDc4WUlaa3hRVHBqMFlSekZnS2x3SFl3RkJnL0JxREVsRTJERnBNcXp6ak1CVEtjd01PNi8ybXFyK1dRWmFOdlVUM0RjcUJFTUY5d2dzRUE3MTVLTmFEUFI3b2xLRHBvbTJqMTVmL01Fd3c0Qll1Q0RUeGd0T2s4d1JoaGt5Z29VemlVaU9oREJNek5uem13TG5BdS84VW03UXNCYy9uaWQvMkc0ZFRGaHJBekNiVkNuM2FscllIRDVnQ2R3bjJxbUc5NHQ3a3ZzQTY2V3FXNURDcCtwUEc0YWJnRnRCZ0dUQVNZc3BIQW1EY3krK09hcW1uL0p4cUoxZ2Y1YUpIdXVDeWFxd3UzOFZ5Wm5HQXFURlJwRWtOUjVVVEJ6SXVrakljYVdSTVRxRzVkallGdGttcUh0NElGR2lXWWJscDRnS1o5enpqbmVQQm1MU0dWSmhmSVJlejhyR01JNGxQdlhaNjNKVHpqNFlQRWY1bjNDWlBNcE1vYlFGcDRoR2k1bVpaZ04xekpoOEh5WVNQTFJ0VEFnL1BQNGV0bFdNREFuSXFaVDBjbmhQdFB4U1I4dzk3N3JYZS95dDhjRXJ2WE52bDlCZU9FSDNnWGxkMjdiWHBLK1lrN1BVeDVuR0RpTWttZVIxMll3dHl2NVNFdllTWTBEM0FhOGQ3eVBDQzM0MFhtMzBKaURWczY5bFdERFA1TTh3K1g4dWhNNm1HZzl0OStWaXZvREp0dzdyM1h6M2hZeFlUemtCUVd1bjI1aS9nSC80Tm9nTXhxWXh0NmhZYlZWQ1R5ODN4N3JDTThmTjRQU2w3WUVtMkhkZDlUcU5ZYXJKNEpFamlhRlJzSWtEZU5qWUlRWGxoZVFTWlQxZUV3d3JGT01hVmpoNFRJWjVDZUVjRHovaVpTSkgwdVpXZng5ZVFtWW5Ka29NTHRBTUNPWURQZm5oZUZsUnRNaXNobk5ZZHdKb1lZSkMzTWhmUVFUbUNIK1VkSUlvbEVGaGdYVFkvMGVld3FqZ2NTSU9wVHB4NmZFZytIeFhKWDF5UXMrcDV4eWlqZVRJdENRcG81bENjRi9Dek1zUzZmSk15RFlCOU14NndsNWJvd05oS0hpbWxxWUw4ZUlacVlmZ2RoUkJlMW5GRWtaZ0x5YmcvV2pNRWRsM2ZLV0FtWEU4a0lDUzNpMjIyNDduNFl4bUpQQldwc2N0Sm1LNlp2eUdYdWN1UWFNU09ONHVZS2xXS2ZNdUVhN0lSMGxrMjRnR0JmanZrZ0lPTXAxN1o4NXZ6RWVlRTVZRjJnelFpei9LNEdFRjU2Q3RZTDdVR2Q0ajRyMVZ2a09zK2VaNVRIaE90YktNeGJBaVYzQTJIWXpqOG1uUHZXcHlvSjVsWFlNNGh6R0w4OGxSUG5qRGlHZ2ozbU1kdzUvS3VsUGgwbFlmckJNWWVuam5rVHhNd2FVVGFvbDNPR0c0WjNGRFlNVlNabmRKb1loTno3VGxGNFN2L3NGbVlSa1ZoTnZxMDVpZms2RDFDbG5yMCs3SjhZUnpacWlBZHpLa3FJSnhXZDNJVDBmV1d5a01WVy9ZZUZNVGZRKzZ3NEo4Q1hWZDcxM3ZoM1QvYjhteUVKdjBsK2wrZmpzTkNRN0o1ay9PRmRwUHhzS3lCclF5dGJESFdUU2RhUkJsRW02ZFVNeGNiOWhBSm1neEJ4SzYxWXdVVWVtSzFMMXljVGNjUjFaZGZMRXZhV2xkNXlYNzR2OHBtMlpwc1Nra2xtY2VPN1MvUHd0cEpWN2JQSjFoZi9aaVVuTW9kV1VndzQ2S05rR0NUMCtUWjhZYWV0OE1ieldEa2Zob0NadmoyMHh5MWU0SjUvc2NBUzJlU0lURnpoQVpCd2lJeE50aDNqL2VDL3lkWVQvcFluNXNaNXZsNzhvOTBkYXRWTkFtajh2UEY4eWpuRnRxS2ZPWnd3VGFZV08zYnp5YzBZVlRFaXZxQUNnVnF0bno1N3RVenJHMmtYS3pEdzJaSDJLbmRmTE1WS2VTZ2xvM1QvOFEzOTIzSEhIanZvbGtJWlQvQmhLN2VvbDV1amZLMDRHQnpIeGFLcEkyaXFHN3pPTWhiNjFiaEQ1UjRLckUzUHVhRmN2ZlI2QmN6c3lUWFdLbFdwbGt3bXRDa2xacWRxOHlUSUV0UFRTWjdRdWtoNVFNRFBocjUwelo0NzM1eEZzZ2drSHFSSUpIK2tYcVEySkRSTXAyWE80UDcvVkplckQ3RWQ5U1BvU0d2eGVwWG16WGQyNmgzMGQvUVlqcEZ3MGtGQTRqbWtSa3lUYUU1b2lHZzVKNnBHQ1EyQlNsZmFSeFlkbEoyaFNCQzZoTldQYXBFQm9tdFJOQUJzSlIvREI2cDB2clpySVZmeDZXRHJRYmlBMG9KaFpEbDh0ZmNRTVM3MWx5UzdDVGRITzZIOTRodnlmR2lPY3l4Z0RRejVUeEhsZ0dlcE1uY2R4Zkxtc05TYXBQbG9kUzVrWVorSDlRSnZFc2tCZ0dab3ZHbUNLbExZeG15RXJFZG9zcmdFc0NWZ3hlQ2RZSXNUN2dyV0dqU1BRY25nZW1EaDVsNHFFU1JrdEV2ekoza2E3Z2paTW04QWZjNytFQ2Y4N3BtcnV3emhDeSsySGlwaWd0UlBGallVRDZnVVR4amxqSVR3THJrMDlYNDZEQ2VmenlWam9sekJ6S3crMUQyampQUWphUDFneGpvckUyQWx0WlF5VnRTR1lyS2tqekh2Rit2aE9GTCsyci9TZmJNeEFmQVh6WTdnL21GQ3dEaEx6a01JblZ2ZTRIRXZOK21pNE42ZzhPN09NUzIrNnRKTkFHY3hBbURIeHdRMktlREh3ZHpFWkVVSEx3SklVNXdOc1NFM0dmWmxZZUZtSFFVeGkybUxMKytMd1k0NHk4WUx4c3NHMG1EZ3hJd1ZUT3BNcUx6bVRLUDVxek9Zd09GN2lPZ1REd0ZXQWVSb0d3QVJNMEJYUEIvOGppU2xpREROMUx5WUkvSVgwZ2NrQVJocUxOdWMzQkNMT1k2TENGY0c5TUl1bkNLYkUybDM4aFl3bi9MMzRvL1ArNFhBdEFodW1iZkFER3dRTVNwRmdjcmhKd0pjMjRRNmgzMldFUUlxUVFqOXBDOCtKZHVPN2hFbkMzR0NDM1lqb2I0TFd5THhGUGR5Zk9BUk1pNWpjZVJiOEJxTmxRb2VCdytCU1JMQWFTNDFramZCTU4yQUVyZ2c0akJmYXpiT0dXZEJlaERXZWQ3OFVNQ0hJRHJNc2VNSVlZQXIwcHdvbTRFaTZTQVFZMm82SmwwamRtTURFbk1HOXdBenNxWjh4Mnk4eEhoRmF3QkIvTjJNSElRZi9hbEhZd1IweVUwRnFqRjh3aEdFenp4UUpMRkFpZ3Y4YzNIbVc0Sk1pK29Wcmh3QTlCRExlVTRnNUV6d1FoaDlRTUNKdU80Nk5NU0VOcjZCeVcrakRSREJjSGpDQk4zdnR0WmZYU25sNWgwVU1ZZ1lvTDBwZ0pzTzZWNzVlSm1ZbDE4K09PZVlZei9oNXFjZUJtQnlEbG90V1VwZTVsdlVWVFJOaEJ3YkZjNEdwTThrYnBSR0FJY0pvd0k3bkFtWm9XNzFTd0o1M2tESGFMYmFoVy8zVVI3c1kzMHpPTVliVnJZNjZ2NE1KZ2dUdk5ReUY5M3dRREwxdWUrcGN4L3NHODZmd3JzSFFlTDdUUll5TG9PSFNqbkdadHlyaTFjRndVOWMxeG9lckIrb1VqZXEzYWRNa3ErZlpYTkxMNzdlQnc0ZXBGMnZjL1IvVy9sd01nRjVVdzhNd3NERXdYbU9ndzRmYitIVzRtQ3hJTTRmNUtraFNLU2xqM0k4anRXSXkwbjZYZmU4d011NVlXUHNOQVVQQUVCZzFCQnJOY0RFZGF4OUg3eHNMZ1JhajlnQUczUjdNcy9peVdJWVJnb1FHZlErcnp4QXdCQXdCUTZCM0JCckxjTkgyaUZ3aytHUFNpRUFIQWlRR0dSZzJhUmhhZncwQlE4QVFHRFFDaldXNFJDS3pXSC9TaUVoZm9nNUorRUFVcEpFaFlBZ1lBb2JBYUNEUXlIVzRMTVBaWVljZFdsbUtSZ1BxNGJlQ3BVbnN0M3JjY2NmNU1QK3l0WFBEYjQzZHdSQXdCQXdCUXlDUFFPTVlMb0ZSN0ZiQ0dpOUM0Q2VGWUxhelo4LzI2ZlpZSDZoWTdFbnB1dlhURURBRURJR3hRS0J4REpmMXRpUmlIK1phMjFGN3Nxd3AvZGEzdnVWOTFpRTd6S2kxMGRwakNCZ0Noc0NrSTlBb2hzdUNkTEs1aE9UeWsvSnd5VVN6Nzc3Nyt2UjNrOUpuNjZjaFlBZ1lBdU9HUUtOc3JxUmRJNVZmeUJNNmJnK2pUbnRKVGJqYmJyc1pzNjBEbmwxakNCZ0Noc0FVSXRBWWhzczZXellJU0cyZVBZV1lUdG10OE5PeXlYMHNqKzZVTmNKdVpBZ1lBb2FBSVZBSmdjWXczSkJnUENUQ3J0VDdNVCtKcFBpbm5YYmFtUGZDbW04SUdBS0d3R1FnMEJpR3l4WnNaRmlhRkVLN0pTbzV0Um43cE9CZy9UUUVEQUZEWUZ3UWFFelFGSm90SnVWSkliWTZHOVQyWTVPQ21mVnovQkFnRUpLbGZxd3BaN2VpWWV3bU5YNm9XSXZIRllGR01GeGVTTklZc2tIMHBCQ2JwN01IYUZPSndEZUM0RmplRlV2Z0ViYjF1dlhXVzZON3hqWVZseWIzaTYzdldHSEFmcTFMTDcxME51Kzg4L3A5VnRtU2o2VnZiTVhIRm4vc3gzdkhIWGRrUC8vNXozMzh3dTkrOTdzbXcySjlheEFDaldDNDdGTkpvZ3NtNFVrZzl1Sms0KzBtVHpSTXVtVE1ldHZiM2xiNlNEbUhLRzJqOFVTQWZZclpqSnhrTlp0c3Nva1hzbnA1ajJIQWJJN09YdEJ6NXN6SjdyLy8vcWlBTnA3b1dLc25CWUd4Mmc5WDVtVDN6VzkrczdrYjNSWjZKbk95MjJDRERScTdONmEwVzdmNzdyczdaYzhxOUx6ejY5MTMzKzFrMldnc0ZwcHdHdGszbVlxZGx2QzVMM3poQys3UlJ4L3RmTEExamp6MDBFTk9nbmNqOFdycU9HaDR2enIydzIyRWhzdVNJTXhQazBLWTFGaC8yMVRDTmNEeUxuWTg2a2F2ZnZXcnN6WFdXQ1A3N25lLzIrMVUrMzFFRU1CTmdEYTcwMDQ3K1VESHVlYWFheUF0SThzYW0zY1lHUUtqaWtBam9wVEptVHhKeTRISW05emtGSTc0NDVkWlpwbEtMZ0syWVp3NWMrWkU1YzBlMWNta1NydGd0aC84NEFlekF3ODhNRnR4eFJXelFURmI3bzFaK2ZISEg2L1NqSzduVEZJZTlxNWcyQWtEUTZBeERKZUpkMUxvNmFlZnpwNTU1cGxHZGhkcnhlS0xMNTZ4NDFNVnduKy83TExMWm9zdXVtaVYwKzJjYVVTQVFEaXNFUWNmZkhBMlk4YU1TaTFobkJNc3haaVhsVGw1elpOUFB1bWo5dnZSY09lZWUyNnZlWC8yczUvTmxsdHV1ZVM5N0FkRG9DNENqVEFwMC9sSmtrZ0pLdWtsc0tUdTRKaU82ekFSRXpCRnhHb1Y0cmt2dlBEQ2ZvSWtZTVpvZEJHWWYvNzUvUVliM1ZZVEVIbCswVVVYWlQvNzJjK3llKzY1eHpOY1ZpTGdObHBzc2NWOGtOWGIzLzUydnd5UUNHYUljeDk0NElGU3BoeEQ1bVV2ZTFtMnpqcnJaTzk0eHp1eVZWZGROVnR3d1FVemxpS1JuOXpJRUJnMEFvMWd1RENmU2NxZmpCbU9DYWlKdE1BQ0MvaUpyeWhRb0xsZ1JzZDFFQ2JaMEgrU25qQUJuM3Z1dVJrUjNFYWpod0RQYysrOTkvYkxmbUt0ZStxcHAveFNuK09QUHo3Ny92ZS8zM1dwRisvN0lvc3NrcjNuUGUvSjN2Lys5MmVYWFhaWlQwbGcwTEJwejhZYmI1d3g1dkwweEJOUFdLUnpIaEQ3ZjJBSU5JTGhEZ3lOTWFtSU5KWkk1azBqdEZYTXlTenhLdEtERHo2WW5YcnFxZGsyMjJ6VGtWRU1zekxyTnRGT1NBaGlOSG9JWUs3ZGV1dXRrdzBqSC9nZWUreFJXYk1rQVFZV2pTOTk2VXQrYTBvWWVpLysyeVdXV01KcnRVVm1tMnlnL1dBSURBQ0JSdmh3U1l5QWhEd3BoRVlIMDIwYXNTWVRIeDkrM0R6eGZHR2ttQm52dSsrKy9FK3Qvd20wUXVNeEdrMEUxbDEzM2VRZTFVVGRzd2xIWFRNdTE3TW12WmNzVlBpRVl3bFZSaE05YTFWVEVHZ0V3eVdZb3A5Z2lYRjdtUGc1a2N5TGpHbmMrbEZzTDh1QTFsNTc3ZUpoSHpDRGorN2hoeC9PZnZHTFgwUUR4dEJ1MFhMUmRvMUdEd0ZNL2ltNjk5NTd2Ums1OWJzZE53U2Fna0FqR0M2U2FwT1h5UlFIR3dGRkxKdHBtbG1aelNmUVZJdEVEdDFycnJuR0I4L2NmdnZ0VVY4ZGZ0M2xsMTgrcVVVVjY3VHZVNGNBNWw1Y0JTa2lTSW9vWXlORG9Pa0l0TnZ1eHJTMzVGbEYrNWtVWWdKYmJiWFZzdm5tbTY5UkNUQUlZSWtGZ3lrVFVYYjU1WmY3Q05RUWpZcEdXNlExMTF3ekl4SjJPbmRRNHRuZ3I2UWRCTGZCU0dnL0tRakxsclVVK3pLTTc2eUJYV2loaFh5N2NNR0FFMzdQWGt5eGRkb0ZEbVdKYVJDb3BwcXdpS1VDN0hoT1U1RllCc0VaTndoTDJsaldTSHQ0SGc4bzJ2cVJSeDRaK25QcGhqbGpoWWh5MnNYOENpWjF4ekR4R1NnSXdSMUdQU2hKNUlPZmp1ZmZyZS9EK3IwUkRKY0JRVkROSkZGSThvNkpkZGdUNWxUZ3lzc0l3NDBSekRaWU1FaGFUMUZhd0k2bFlHakhxNnl5U29ZV1hIZWRNbVp0SWw5WmZzSzRDaE1NRXdiK1kvekkrY21ZaVpKSmlaelA2NjIzbmsvbWdEYkgwcEpBdFAzT08rLzA2MFMvOTczditTVXNyQzN0eFlmSTVMeldXbXY1REZ4Y0Y5cEZ0QzRNL2NJTEwyemJ6QUltQjRNbFk1ZlNnR1lycmJTU043bm5mZjh3WFpiZDREc2xVeGVmQ0FqMGU5Q0VJSktpR1lvWTV2ZlFwOVI1ZFkvekxBaTJDOHlEL3BHL0dkZE1qTUR1SXgvNWlNZXM2S0tnblZoVGlLUW0wS3NYSXNJZUpvYmJoR2VKUlFaQnBJZ05ZNWV4OXVNZi85Zy8xMnV2dmRhN3pQQTc5MHEwZi92dHQvZDlEYytWK3lIWVVqOTVxQU54TG9MaVJodHRsRzI2NmFiK0hRc0M4T21ubjU3dHUrKytYaEFJNTVkOWNoMWpqZlhNTEx1YU9YTm05b1kzdk1Gbmp3djk1WG5qZStkOVp1Y3ozZzJsYXAxSWE4ZFk1VkxXQytKbXpacmx4SGowRENlSExybmtFcWNYcEJHNVkvV1NSeCtjbUl2NzBJYysxTmJISFhiWXdVa3lqcDcvbmU5OHg4MHp6enh0NTJ0aXFQeGRtclA3d1E5K0VLMzcwa3N2ZFpvMFduWEp3dUEwbWJucnI3L2VhVEtNWGxNOEtFM1h6WjQ5MjBrYmR4SXlXblYxYTZNMEE2Y283V0oxL3JzbWZsOWZxRVBCWjA1Q2c3djQ0b3VkbUgzMG11SkJDUUJPeTZxY1VpNDZNZXJLN1FyM0xQdlVCT3ZBTGtWaSttMjRsdFZWNXpkWkhKd1lXT3IydFk3dnVPT09sVEVLZWFPMTBZWWozM012eEhNQnUyMjMzZFpKU0hDSzI2aDhYN0NTUU9qa0k0L2U4cGhqam1uVlJSczMzM3h6ZCtPTk56b3gvSTd6enp6elRDZGhvWFYrNmpsSUFQUzV6WlZOelAzd2h6OTBFdUE2NmtvZGtCYnRUajc1WkNmaDBFbW82WHF2VkJ0RzZIaEhMbVcxTFVwanhYQjVvV1ZpZFpLV1VzK3lrY2Vsb1RocGhXTS9NSGwrLy9tZi94bDlSako3dXFXV1dxcXRqOXIzMkdscnR1ajVNc1U1WmFscU8xOGp2UEozYVVFT3BoMGphZHBPdm5OZmx3SzBmSnQ3bVZCQ25RaUd0Ris1aEIwYmIxUnBIMHhVUzJCQ0ZXMmY4b0U2Slc3dzljaEU2WTQrK21qM205LzhwdTJjcWw5a3puVFNaSncwNmtydHF0SjJ6dm55bDcrY2JBTGptTi9Cdm1wOXZaeUhBSUZRTWtqU0VxZEtiVlZ3bzl0MTExMGRtMnowUXdocTU1eHpqcE9tV09tK0FSOXBtdTY2NjY2TDNscVI0YjR1eGlCak1jV1l1ZmdiMy9pR1F4Z045Y1krcFNHNzFWZGYzWDM5NjEvdmF5NldOY2pKSXVHa0laZmVMOWFHRVR2V1RJWUx5RXlBcVlFVkhXME5PYWh0K3ZyUzZFWmhnRElweWF3VWZTSXk0WGIwRDZsZEp0Q29KSTVHakRaUXQxOW9RNm1kcHhTNDVXUWk4MHczZFU2MEU0bUQ3UHEwMTE1N1ZaTG0wVUNPT09JSUo3TmdSMjEzM1hXWDIzREREUjNNRnUyNVgwSnczWC8vL1FmS2ROR2N5d2pCNnRPZi92UlFMRFl3WE42VFFWSVZob3RHaXZDalpVc0R1L1hOTjkvczN2M3VkMWNlMzNLRnVDdXZ2REo2ZjhZS0RKbXgwMDBncU1KdzExOS9mU2NUdGVNZDdKZllRVXFKU1hxeUF0Vjk1NGQ0WFFmRGJVU1VzZ0R6ZnJYVUdrMStieW9SMmJ2bm5udU9kZmNJQU1PL0ZpUDh0L2c3ODhSM2ZFLzRJSXVFZndnZmJGM0NIMDRRWG96NERUOGN1OXhvMG91ZDB0TXhBbVkrL3ZHUForOTg1enU3WG9mL2pYNEhQMXorQW83aGY5dHV1KzJ5elRiYkxQOVRyZjlsa3ZkajZzTWYvbkN0NjJNWGhiMXFZNzl4ak9mUHZzWml1dDd2TjhqTWNmamZpOW5KVXUyb2VyemJrang4eEJLbU1yay9rcjdpcXZmS24wZnNCcm1lVS9FTytYUDVIMzkvYWp6ek8ydmZ3YjBzaXB6enVoRWJVUngxMUZFKzR4dnZZSkY0ZHdpUXdoK043MWh1bU5MZ1JuemJaQUtUbWJ0Unl4OGJFVFRGd3lVd2hXQVpTVllkUVFqRmg5KzA3L0p4K29DWDg4NDdieXk3Um5SeGJDcytJbnZsVStwZ3VIUVNoa3NLdnRqU0tBSTBZQm9rUk9pVm1LQlNBVmN3QlppdHpHWitvc3JYVFZ0SnppRlRycC9naU1Za2lDc1ZtQk91aGVsKzduT2Z5NjYrK21vZlFCS09Geitac0FMREphZ25Ud1J1TVRFUlNNYi9lU0lJU243RDdGZS8rcFdQQm1VaW02RWdwWlNBRTY0bDBucWZmZmJ4N2JycHBwdkM0ZHFmQkpwcDc5dE1wdU5rSFdCRk5pbzJveUNBNXR2Zi92WkFnaUhCanZ1REg4d0hBWVdnSHNaT2pMRXpoNEFiUVVyRjMyRW1NTyt5QUNiR25ueThHZThsREMxRnRJbEFOVm5tUFBNaE1BNUd6ZnZBMkVreGRibFlmRTVxK25YKytlZW5xbThkVDdXVlNHMFNrcEJzcGh1QlE0eVJjaDJCVm9jZmZuZzBReHkvUC9iWVk1NFo4ODZ5MDFuQUgrR1YrMis1NVphKzM1eWJKOFlEUWgrQm9kTFM4ejgxN3YreDh1RUtmVzlpZWU5NzMxdmJkOVd2Q1dTNnI3L2lpaXQ4c0VIQVlsdyt0U1RDU2VxTndpZXRLT21QMVFTUU5KVlJtZkxyVmphNzViSENkS3Q4dmxHekdNRWsrQnMxMGJYYWkva1ZYNWlpbzcwNVZJek1hYUp3WW14T2pNUC9WaVcyNEl0Zi9HTFg5dTY4ODg1T0UxYnIzdUdmMEM1TlpPR1EwMlR1empqakRLY0p6UWU3RUhSRnUvakVMQzV0eE9IdjdrYVk5SHNOMU1uam1mK2ZJRE1DdWJvUkpra3hSKzltMkcrLy9ad0VoSzdZNU85VC9CK3pLaTRuUlpJN1dZUjhUQUErUW9KMFlrU2dHWUY1WE1QNXhVSlFEMWdXNzhOMy9KaGJiYldWYjMrczduQU1YSWs3b1I3ODVRUitNdmJ3MWVNYTBQYUY0ZFRrSjhGOStTQytXSHM0UmpCY2pCVFo3azNBc2Q4WVU3Z3FDS0xDdDN2S0thYzRYRCt4ZTV4MDBrbE9na3lzR2lkaHpZbWhlOU93R0hiYjlYekhQYVJOSXh6dmVvd0lSdVRkR0hRZ1g2d2ZRempXWVZMV1BhSTBsZ3lYRjBQbWl0aHptNGhqK0trVXp1OEhzWjVxMitBZTFlOUVsOGNtZnBpYVRHZE9tbSt5SHpDZ0ZFbnlyOFVvbURDbGNVWjlwY1Y3TWRaZ1h0MndWWllsUjBSNVdZQVZHTWkwWEZxWHBQMUtBaVhqb0Z0ZHRGbm1TVDhaUzlNcGRxMzFYZXRDbmN6ZXJqaFpkdXR6NnZmWHYvNzEvcDRJTGxXSmdDR2laUEUxSXFEeGpGTDFWejJPZ0pTS0cwQllJWXE4YWwzNTg4QTB4Y2pwcjdROTc1dUVzZWF2aS8ydjVVUHVsbHR1U2NJRVV5U1FybHRVZmlvSU1DODRjaFA2alNEQU81a1BrRUs0eGRkYkhBTjh4MjhiaTd5bWJ0NFBtYXE3OXBPK0l3eEoyNDhLdXRSUERBQ0NVd3luRVQ3V2JJWkx3QXZhU1Y3U1Q0N1dodjVBaEIrTVNGdldqZnpnWk9KRU9vNU52Z1RSb0tXV3ZXUktRTyswYUQ3NkpIbEpxNzdzK1JlV3llV1FRdzVKU3V6aFpqSnp0U0tXODllbi9uL1RtOTZVMUNhb2s4bVR3QlFrL2xRZFRJUUVrNVFSMm5TSVdFN1Zrejh1MDZVWEJsSjFNbkhPa2ZhQnhwNi9ydTcvVE5KTXJnUzlsVEg2V0hzSVB0SW04KzRESC9oQVV0dXEyaTZpZmRIZ1lnU0RmOWU3M2xXcnYyaUNLZUxaTUxiS2hNaDgreG1MV2tQdEdHc3A0bjNIaWxGa2h2bDZ6anJyck5UbHJlTllUbGkyeEhqSVgxdjJQOUhOcWZtV1pWZ3NUU3Q3Zi9OMWM5NEJCeHlRRkVvSkdCekRxT1VPaHR1WW9DazlQTzhma0hSZnkzZkg5VTBnZGtGaGcyOThLZ1FqaWFtTmJMZklGaVd6bmM5OFZHd2tDK0RKc1l0UE5VVWtiU0F0WUl4WWRCL0x5eHc3dDNpczdKNmNpeDlRNndXVDl5N1d4M2N0QThvVStldjl6ckhmOGRmSlFwUGhuK3VITk9GbjBxWXJWMEdnSWUwU000aGVvNG5RKzN6eER3K0NOTU43dnp6QlViU1ZwQjBjcTBJeXYvcUFPTGJ3dys4dHBoajE0VmVwYXhqblNQdE9CcTNodDhSWHErVnZYYmNlREcyVHNPTVRRaWlhT0prTVFoYURhRXhCcUlOUE1lUDgxNDcvQ1Q3RUY0eVB2WmZBVTNiMVlvNlJZTkJXcDRUSFRPWnVuNDYxMjdzVUx1UThyVGRPN3ZaRmtoQXk2NDA3TllyaDh1S1MvWVdKZUpLSm9BMENFWGlCRGpyb0lMK2hleW9BWXpweElrQ0VVaVNlSTlsbnRDYTArRlBiZHlZa21jRGFqb1V2QkE4UkRGSU1NQXEvbDMxMm02Qmc4a3dPdlJLQkh6THZKUzhqK0lTSnBTN0pMSjFwdVZMUGw5OXd3dzBabVlSU3hFUkhwcXJpeEpvNnY4cHhuaTlSclVUeXdvaDZJY2EzRWl0azh1MzVhR29DejBhQmlCd21FQ2hHQkNqeGJIck5pRWRnSUZuRVVDUml4RE1oaUk4Z3ZicEVVQkpiWC9heXRhWDh6WDV2WXdUOEl0RkhWaGYwR3JUSWU4VTdIMlBTQ09ZODkyN3ZackV0by9hOVVRd1hjRW1oZDl0dHR5VWpUVWZ0QVF5elBhUWJaTm1KMXFVbUl4NkhlZit5dW9uMDVDV0tTYTFNTXZKZFZkcmZGSWFMUkYwa29sQ3BuekpvSXRxUzNMSjFpSW1OYU5rWUVkRktoRzRkSVlINldISlJ0MTB3WENKSVkwUjdtRmhqenlwMmZ0VmphTGRFSXlzeGhMZklNUEZYSlFSSXRMdGRkdG5GTHlXS1RmeFY2eHJFZVRBQ1VtaW1DQUhqZ2dzdVNQMWNlaHdGQW1FdEZXMk1aWVJVcEZnamVpVTBiNWJvRUMzZEN4SEZqaEFXVzI0RjR5Ym5lYStFVU1MOGpjWmRKS0xxU1EwNXloYTdZcHRqMzN0L1FyRmFSdWdZaWJEclNGY2oxSVdCTllWSmdPVlNEUDdVeXpxd20vVllFY3RURkowWTFacVFrQkdhcXBnYTc5Y201Q216Y3I4YVk2eExDQU5vaEN3RHFrT1k3TGcrUmdnSjhyMzdyUmRqdjVjZEF5dTBvTHJQbVRXU3FVbVhjUVN6eFFVd2FLSzlMUDA2OU5CRE02MHk4T1p0bmoyTW9Bb3hFV1BOd1pMRGxwWFRSYXhqTFJQdWxPYXc5aGFpTUNJRVVEYWJpRkVRMUdMTUwzWisvaGhMazlDZ1kwSnIvcnppLzVqM01Ta1hDV2FKK3dSTnRRNXhYZXpabzhsakRSdEZTMTB2L1d6TU90elFhU1llQmpmcjRKaHdKNTFZZzNuWlpaZFZZbDVUaVJYUEJnbTVTSmlKZVdGaEhsVTBQVjV3ekxRa0JDZ1Nrd0w3c0dwNVRPM0pybGduNjJ6UnpHS1RRdkhjMkhjRVFyUVZ6TjB4b3MwSUl3Z1N2UkFUSjM3dnV1MENSOXFscU5Qb2JUSG5EWk9od1hnUm5DakhIbnVzSHhzS212T0o5TUdrVExPQjBXeXh4UmJldDc3NzdydTNiUzRSN2N3UURzSjhNTE9taUhld0xqR25FYy9BdTR4QUZpTVlQZ0picjhSNll6VGNYZ2dCREVFSG4zV1JhQ3ZtYlJMRHdCdzV0d3B4SFV3Zm9TWEZWQm1EZzNSclZHblhvTTlwSE1NRklMYTRRbXJEMUtMMVc0UEdiR3pxWXdDemoyd3ZwcnFwNkJ3VEE2YlRtTzhOaGt0Q0FrV2llaE5adHhlV0Y1WEpocy9pdVpqWU1MVmhiaHhFOGdhd1Fkdm9aenN4bm9taVkvME9UN0hKQTk5ekxBbEl0K2RDdXlqZ1VJY0lCS05kZk1hWUc4K2tUcnZxdEFWOEZSbnR5OWUrOWpXZjFJTnNYRHpMTXFhbXRiWGViTXZPUjFOTmFQOHgzR2dId2dRbTVYNElmMmlaVmFYcy9tWDNoWkhqKysrRmVIL1JObU56Szg4SDRZY3lhQ0lRTXZiT0RQbyt3Nnl2a1F3WHdNaFNNMnZXck9pZ0dDYWdvMVEzMnRqWlo1ODlTazN5YmNFRWx0THdtTFMwM3JLdjlJejVEcE94UjVzZFpNcEJXNXNaNWV0RElLakwxS2dIaG92SkhPWVlZMkJNV0xIc1dmazJ4UDZuVGYyMEM4MFkveS9DYXN4WHl5UmJ4ZUlRYTFzL3g5QytDSVFrNnZWakgvdVlqMHd1TTUyeXJSN0Nkc3BQM2s5YnlxN0ZZcE5pQmtTQXAvempaWFhtZjRQWkJvR3FLRmh5SHNGYWRYeTR0SXN4M1F1aGdlTERuV3JpdWNmNlB0WHQ2T2QramZQaEJqQ1kxTml6Y3BJSjdiWlhjOUZVNElYSktjVnd1WCtkaVNQVmJzeXo3QWtiWTI2cGE4cU85L3ZDd3hUUjRQQ3R4d2pHUnFsRC9iWU5wc3VrSGlPZVNZcWh4TTRmNURHMGJ2THZzbnhKTzlHVVdoZ1FybUt1aWtHMkoxWVh6Q0ExYnZIN3h5SnZZL1dram1IeXgveWJJb1NoT3MrL2pwQkdQeEdhcDVycXRIV3EyOWp0Zm8xbHVIU2N2SzJwUUlOdXdJejc3N3pnSkRtdjY5TWJadjh4RDhJSXA0SmdFaXkxSWNKeFZJaUpJL1ZjK0cwNko1YVV0alBkN2VMWllmSldjZ1N2N2FhZUpTWjVKZjVJL1R5MDQyWCt5dFN6N3FVeDRGL0d0T3VPbVRwTW1uYlhGUXA3NlhQeFhIQXN3NkI0L2loK2I2eEpHYkF4cVo1d3dnbVpzcnVNSXZaRGJaUHlwL3JOSElaNms1cVZ3M0Nua2tnbVFZQUgwY0YxSjZaQnRoZXplY3Bzak1tNWJxUnh2MjJFYWNDd1lzUkVOd2pHRWF1N2wyT1laMG1hUVZCT3pNU05TVjVadmZ4eUZiVENxU0tlVzJwc3hkclphN3RnY0dYK2ErNC9WY3lJZm1KMWlCRmpoSWgzQ3N5OExrTXYxczA3UTZSMjZyN0Y4MGYxZTZNWkxxQ1QyWVZkTzBaSnd4bjJZTUFQZC9EQkI0L0VCRm5zNjR3Wk03SzExbHFyZUxqMW5iWXpjZlR5b2pJQkJHWVJDMXpCdjhVU0pKSlY5T3RMUzAycXJRNTArUWR6SENiMWxJa2I4MlBkTnZiVE52QW1DQ2JsbThNTVhtYlM3Tkx0Z2Y3TVdrMmlmbVByWGdPK1JORVMxVHRWaE04NHhmQjQzb3pMZnBnRkpsekdUT3E5UUJCSjNYL1FHRERPVWk0UnhnZ1p4TWgwWjlTSlFPTVpMaE00R1plVTVEdTZTTHNUa3ZFK3dzdUFuNHZvdzFFa3R1T0NPY2FJTGVRKzhZbFArR1Vkdlppc01JTXlHWkhrZzMwNVk1UFNDaXVzNEplSjFXVm1vYjFNNkpTNnhNU0x4cDNxSHhOV25UYlM1MWkvcTdhVDlyQWtneTNpWXNRRTIydm1vRmc5Z3pyR3NyRVl3NlYrM0FobDJ1Q2cycEN2aDdFTFE0MVpDQkJrc0xEMHMxcUFKVEd4cU9EUUJvU0xxYktNOEw2eDVSNXpUWEhNb2MyempJdDNmQlFzSWdHZlVmbU16M3lqMHJvQnRBUEpuS2hGdEZ4U29EV2RXSDdBc2dqNlBXckVwRjYyT2J5MkdNeVVhTDFXczJHQ01GWHQzaE5sWmdUVGtKbUlQWlA3SVpZbWxFWEpkcXViQ1htWlpaYUpub2FHUXN4QnI4czBxQXhHU2R1WUFPdG91bHdmUzJRUUdzb0VXNmRkNGZwQmY1WnAyK0E0MVpNOUNSc3c2OGFJWjRLWnV4K0d5L3BiR0ZtS1dJUGRqd2FkcWpkMm5INlNUWXJJNmFJUXdMdkJraUcwZXN6S1J1MEkxQmZWMitzWjZXOGtLaUE1UXRNRHFKaUV0T09NOTNYVW1YU0gvUkJaTDh2YTZCUWhHTlVsSmxtV2o2UzBNQmpLSUFRdUpwS3lKU0RkMnMvMU0yZk9qSjZHa0VSZ0VGYVpYZ2tObjRrdXBUbDNxNCtKTTJYcVI2TmhncDFLRTIyMzlxWk0zNHg3ZkxlWTV1c1NHbkt2Vmd5eVk2VWl2R2xIM1kwMHVCYXJDTmFIVk9JUitrckNrQlREcDQ1QkV1OGF3bGRxUENBY3NCelBxQk9CaVdDNFNMdm5uSE9PMzBWbHFpWGZUc2lIZDRRY3YvUXo1VjhaM3AycjFiek9PdXQ0TFN4Mk5tMyswWTkrRlB1cDhqR1NXNkNKcFFoemR0RUVsam8zZFJ4ZkdrSUQybVFkUXNOUHBVakVENGZRa0lvVUxyc2ZUSUpzVzNXMWJ5SjdaOGkvSGlOTTNHVC9La3U4RUx0dW1NZXdac1FJN0REdmtubXJqTkFHWVJ3eHdpeWFDbXFMbmM4eHREbWVYWW9Rc3VwbXZpTkJERXVkVW1PT1o4TWE2bFIvVW0zcTV6anZHVUpHakJDc2FXOHNuaUoyL2lRZG13aUd5d1BsaFNDQXFxazdDU0Z0c2h2SnFQYVBsNCt0dkZMcjk5Z3hCb2JURDJHeVE5SlBtZGJJT01WazBBL0JzR0hjc1N4WjNlcEZLOXR0dDkyU3AyR0J1ZXFxcTVLL2Qvc0JmRk5hVU5tMU1HbDg1ekR0R1BGY0xyLzg4dGhQMDNJTTAzZUs0YUxsTVFhNkNkYjRPMU9DRGY1SGZLYTlFTXhPZS9VbUwrRzViTFhWVnNuZlV6K2dhU1BnOFd4VDFNOW1HcWs2dXgySDRUSldZMW8xd3NwR0cyM2tzOGwxcTJmU2ZwOFloc3VEWldDZWVPS0pYYVhmY1JzRURIbzBXM1plU1UwaTA5MG5Ka2w4cUNrTmsxMS8raldETTRuQ0dGSlpodEJjK2pIdEJRenh3Ykk5WEsvRUhxNHBMWWMyazh1NEh6OHA1bW9ZWjY5RTR2K1VDUkRHeFhJTU1uWDFRMkNQU1QvRjFLdldqWmJIdG40cFRSNUxDUWxmdWhGbTU3SjNwY3oxa2FxYmR6QWxOR0t5MzN6enpYMk1RZXI2MlBFbGwxelM3NGlVOHQ4U0hNbThWbWJPanRYYjd6SGVOY1lGMm5XUmVNY0pYcHlsVEg5RWl4dDFSMkJwblVKYUV4S3pOcTRvWk4xSkM5TDgzZ3pTY2hlbnBTOGorNXowQXJvOTl0akRTU3FPQWk3Tnptbloxa0RhcjN5N1RwTlE5RDRjdlBycXE1MGlXSlAzRWtOd1dsTFZkWHhJbzNFNzdMQ0QwMFNhckl0M1I5cVNXMmloaGR4Sko1M2tORWtsMnlWenBKUHZxN1F1VFdCTzhRakpPc0lQaHgxMm1GTjZ4dEs2cERrNUpSOXhFZ0tjbUUrNHRPTlRsaE1uODJCcFhWWG1DR1g3OHBqS2t1RjIybWtucHlBMko2M1B5ZWZzR0I5bGRmQzdHSzJUWmNGSktIRmlsQjN0REFla1pUcjZWbFlmdjRtQk9TMHRTdFlsdjZoVG9GUFhlb3IzNFJtbDhLVGQybGpGU1R0M0VrQzYxczM5dFRGODZGckhKL2RSamdHblFMelN1cFRtdHVQYWNFQUJscVhYRnZ1WC84NTlsWWdrMlYvdW9XeC9Uc3pYU1VEcStUN1VMeUhTajVIOGZjZm9mM2hvNTVaS09saWtSak5jSnR6enpqdlBNV21PTzhtTTZyVHZiYytEV1E5OHlxNUJHUGpXdDc3bHBDMUY0ZWFsbExsMUlPMWhjcWErRk1IY3l4aElWWVpML2RLbUhNeHQ1WlZYZHBMa0hkY0dYR1ZDZC9LSnV2ZTk3MzIrUFV6Z0tXSWlWZzdnMXJXaGp1Sm5WWWFyNEN0Mzhza25PNlhQOUV3TnBoL3FvbDN5SVR2dEN1Um16NTd0RktDVmFwWS9mc3d4eDdTdURYWFUrZFNTcmRaOXBNMDdCSXpUVGp2TjkxdFdCOCtBRVpaZ3dreXlDQXd5Mnp0Rm5UdHQ3TzZPUFBKSXA2ME5TOTlaK3FLRUdKWGF5emo1eWxlK1Vzb3NZTWhnU0xzUVRtZ1RncUdXZFNYdmdRQ200TDlXWDR2L3lCcmxHVDE5VXFCYlZOamdmZEV1VjA3NzV4WXZiMzFIWWJqa2trc3FDUVhEWXJpTUExbDduTGIvTEgwdTBvU2Q5aTMyZ2diUEYyR2pLR1R4N3NqZDVKKy9Bc1RjZXV1dDUvYmVlMjh2L0NvWU1JbDNuYkU0aGRkME1OekdMd3NTdUIxRU5PZ25QL2xKYjViQ0h6ZXVoRG1KL0xMc0p6cktSSVFsL2xPOVZORm00Z3RLbVlHakY1UWMxSXlVWVo3ZVpKTk5vbWV4TEljQW9kVGVyOUdMRWdmeFZlMjU1NTdlcDB2QURENWtnblZvQTZZMGNqaUxHWHQvcnlhWVJDMlpUMVhJMnVsQkVlYldiYmZkTmx0bGxWVzhLWmhFRVVSdjQyZkU3TXdTS1hacklxb1pmMldLQ0VKakRYdS9oQjh5LzU2eFJoWnNLSmptaVlCbUpRRitRZDVOWENSY1F6L3dmYktHVlZhQzBzaGhyaUdHZ2FWbFZZaG54RFBEekl1NU8wWml0ajZKQTZaVFROVmdoV2tZY3lwYkI4YUk4ejcvK2MvN2R0Ty9JbEVIMGVEMDUrS0xMODVrY2ZGcjVqRnhnd3V4QVR3M3hpaExpV0pFMjltKzhmampqL2YrNnRnNVUzV013Q215K2RGbnNJa1IvVGppaUNQOHZ0ekVtRHlnSlZSa0FRUkhDRXg0bDhDRU9BYzJ6OERGSVlIVjc3TEUvRENxZVFWaS9hMXpyTkVhcmdEeFpnbzBFL2svTkg3SGp6Ukp1YTIzM3Jxck9ZbStUbWRCa2tWN1M1bVQ5ZUk1UlhCMlNMejl0Qm5UTEZwZWpOQ3lOZEY1N1NKMmoyNGFMdlhHVElab3FXaXhhTkFVTGRHSzNiN2pHTm9CV2x5c0xjVmpaUm91V3FQOGVCMmFCbFljam92aE9yQkdLNjlDWXRKT2ZpcUt0d0FBQ3RWSlJFRlVrMzZsZGhYYldmeXVRRFVuQmxIbHRyWE80WmxpR2tVekttcE94YmJrdjZPNThoNzFTcmdzOHZVVS8wZURreURodENhK3RHcTBYVEVmSjUrelUreUJ1L2JhYTcwN0pEVjJRMldNcisyMjI2NnltWGFZR2k1OTE1STdwM1Nib1hsZFAra2Yxb2p3cmpBMmVYZGlyZ0pGWHp2bFVDakZ1NGovQ0gzdjBIRFZ0aWcxbnVHcTF3N3ptcVJOTjJmT25LNkRwT29KdlB4YVJ1RW5HRXdwa3VpY0FpbTYrZ1NyMXM5NVd1VHVwTUg0Z1U0L1JybGdLc2E4bVRMZjQ5T1NORHZRUHVERGs2YVRoQlJtQXBPUDRkYU40V3IzSmFmVWRVNVI3OG42cS82Z2FGcTMyV2FiUmRzUmExc1p3MlZ5VjBDZ0gydFY3NTg2RDcvdHBwdHVXcmxkc2JibWoyRk9oT2tQZ3hBMHRQYmN5WUxTWnRMUDN6LzFQK01FbDBDdmhCdW5HMlBIdEx6bGxsczZudkVnQ1NhbENPRFNPSVJpZjRmTmNMa2ZQbkg4eVRGaHRKLys4M3hseFJ0WFAyNEh3NTJvS0dVTmpEWmkrUWdSZmdybzhXWklNY3UyMzZ0K3dUUWlmMHBHdEtkOE05Nk1TQmcvWmlFaU00bllJMkgvWG52dGxiR3BRTGMxZ21YM3hUeUlPVnd2MGNqa3RpMXJyN1FJYnhwTG1WUXg3ZFpKOUZCMlQweW41RTFPRVpIQ3JCT3NRNWorNVB2TVRqLzk5RHFYdDY1aDZjbysrK3pqTjB4dkhlempIeEpleU9lWHllZmFSeTJaTjFYdXUrKyszdHpaVjBXNWkzay9NUGtPbWpCTFlxb2tNaHRUcFRTa25tN0JPSkZ2T0NOTlpDK0VDVHJsSGduMThJNnpGN1dFallHNEw2Z1hFN2hpQW56bVBHbUo0VllqOFlrN0FQZkQ3cnZ2UHRDbGliZ1ZjRW5oQ21reVRZU0dxd2ZZa3VJSllDRGlEbTAwWnRySVMybVlncFFFd0duM0dTY20yN09HUmdER3JydnU2c1JzdkdtbG0xVEkvWWhPSmNobFVORzgrYjRQNjM4c0NOdHZ2NzAzNzRKcHZxRHhZbWF1R3VUU2F4dmxvL1JXaGZ3OXcvL2NtNEFVZ29lSzlYYlRjT1hYZFBLeCtldkVtTHlabHVkSG5XWEU3MGpybURDUFBmWllIMUJWdkhlMzcyVWFMbHFwY2d2N2RtR0NrMi9ObTdYcGN6ZWkvVnFPNURWRmdtQzZ0YVBPNzBUY2Z2V3JYL1hqR1BPaG1IQlh6SXJ0NWozQWVxVEVGazZUdXcvWXFkT1c0alc0SUJnUGFPRlY4T0k1ZG9zTXp0K0RJRTJDdnNBWVYwT1ZlOUIzeGd6OVJVdEd5K3NXZVo2L1ovNy9FQ0FheG4vNHBINmlvUFBuRHVKLytkemQwVWNmN1MxeDlMZmJ1MUY4emdTRThTekFpemx5eHgxM1RMcUFCdEhlSWRiUm9lR21JeWJVaWtraXN1akl2SlNoUWJKQW5YV2pMSDRueUVZRHdpK2sxeUR3Mmhocnp6U0l2UmFRU2lWWWhoMlNPUUVQcEpza2dFSVJvMTZLWTFjYlVoQ2lyUkEwZ21aQUVBWkJHK3pBUVNZbTJqSXVoQ1pBZjFnWG1aZkkwWGJSRUI1ODhNSG9PcjVCOUk5RUlGcUs0NThqV21tZ2NHOHk4eERrUVZhaVhnajh3elBRcE9LZnlSWmJiT0UxWmdLbENQNlFvTkZLM280VmhiNHpUZ2lRVWJSMlJqRFNvRW1UV3F2S004ODgwMk5PUUpKTTV6NFloWVFqUVRQalhOb0ZMbVNSWXR2Q004NDR3MXQ3OHZXMEtoekFQN3d6bWpoOTRwRTExMXpUcjBjbENRbnJTd2tXb2pBbUNLQUoxaEFzVHJ3RDRNZDdRTnBMRXFSZ1RlbzNKM2ErUzR5VldWb3pTcUFabGloU0U3TGVGKzBLRW9QeUdqcHRrYkRnQTNsNjBkaHAvMzc3N2VmVHJoTE1Gd0xwU01kSnY3a1BmUVo3NmhWRDkvMGx1SWkrTXRmMGs5Q0dvRXJldytJN3lIMng4QTJhQ0lKVGhMSHZMMVkrbmpmQllMU0IvdktNZzRVZ1lFdS9TVTFMb2ErMFdlNGJiMzNnMlRlRlVxR1RhTGczcUx5a0tSM3RwUis4Q0VRb0VsMUg1QnlEQXJNbkE0bVhIdE1PekhkUXhNRG5KY2Qwd3Nic3ZPd01TQ1pEb3ZOZ1dIbW1NYWo3RHJzZWhBWVlFSDBCdzhDb3VDKy9jV3lRT0JiN0E0TkJZQ3E2Q3BqY3VEOFRHNHduVDdTVi9WYVpJQkY4aWdTemxIVWlVNEJMNnlmT0k1cVdTR3crRWRTWVZLaWJad2h6SjRJWkFhTWZoZ1pUd0lUS0dDa1NkWC8wb3gvMTVzYndHMzFFQ0dCM0lzWVg3UUlUeGhLNGsyU0R5YTJPT1RiY28rNG5tTkUyelB0TXhrSFlSRmpoTjhZR2t5K0NNTWtrWUQ0d3hqelRxSHZ2MUhYZ0JiYmh2UWN2eGdyM3BDMllUY01jd05pcFN3Z1pqQlhjTFl3WEJELzZEVVBIRkMwL3JSOHZDUCtNbjM0cE1QWGllOEFZNVo3OTlLVksyNWpQRUs1bUtPcVlLR1RtQk1aaEVQd1lpL1NiOFVqaGZlbEZvS25TaG1rNmgwR3lnc3B0M2U0L2NTWmxBZEpoV3RITDVnT3JOREM3QmtuRXJyZGpuWmlPT2laaXVLV0pMeVI1KzNXMzA5RVBNZHhrNGd0TTFjR2tQQjF0czN2Mk45YVphd3pEL2pBY1Fmek1wS3lIVXBuUXlJb2FVT1dMN1VSRHdCQXdCQ29pa0xmK1ZMekVUaHREQkNZNlNua01uNWMxMlJBd0JBd0JRMkJNRVVneFhIeTc0eE9kTTZiZ1c3TU5BVVBBRURBRUpnZUJGTU5sUWVyZ0Y4NU5EcTdXVTBQQUVEQUVESUhKUmdBZTJzWkhVd3lYVmRXanRiSjZzaCtjOWQ0UU1BUU1BVU5ndkJBZ2FPci8xeVRxUzRyaHdwV2ZHSysrV1dzTkFVUEFFREFFRElHUlFRQWVXa25ESlVmYW95UFRiR3VJSVdBSUdBS0dnQ0V3WGdnOG91YTI1UnN0MDNBZkhLKytXV3NOQVVQQUVEQUVESUdSUWVCaHRlVFpQUWovMWFRVXc4WHVmS3VLUlNyL0N5ajdNQVFNQVVQQUVEQUVLaUlBNzd4WnBSTEQ1YVRyVlg2dlltUUlUQlFDcFBpanhJalVqNVRwb0h3TzJ1TDkrUzNWNXVLNTl0MFFNQVNHanNBZmRZZWZxclF4M05UbUJXUkN4NlRNQmV1cUdCa0NFNE1BZVYzdnUrOCszOTk4QmlEeTZtb2YzR25MODBwT1gzSW1rMSszMkM3YWJGblJKbWFJV2tkSEg0RWIxVVRpb05xc3hDbUdTM2QrcThKV0VtdXBUSTlJcnhzYkdRSlRpUUFKMWRsWGxzMEdvRHhqUTRNa21mN2RkOTg5bFUxcTNldktLNi8wbTJpUTNEKy9DUUtDQUVubzJWVER5QkF3QktZZEFRS2w0SjBkVzVHbGRndWl4ZnkydHNxSktvdXJHQmtDaG9BaFlBZ1lBb1pBT1FKSTZ6dXJYS3JTcHVIR0hWWFBWc2FKYkN0MFJmR2laMysydjRhQUlXQUlHQUtHZ0NHUVF3QytDYy9FcE56R2JEbW5qT0h5T3pib2kxVHU1NHVSSVdBSUdBS0dnQ0ZnQ0NRUmdGZkNNd21hNnFCdURCY09mYjdLQlNya1Z6WXlCQXdCUThBUU1BUU1nVTRFL3F4RDhFcDRab2QyeStsVmdxR0lXR1lCN3pJcUMxYThScWNaR1FLR2dDRmdDQmdDRTRQQXRlcnBRU29FSEVlcENzUGxRaXBnVGU3cUtxOVVNVElFREFGRHdCQXdCQXlCWnhINHBUNE9WN215REpDcURKYzY3bEhCcDd1aFN0bHlJdjFzWkFnWUFvYUFJV0FJVEFRQzdLeTNpOHJaM1hyYkM4T2xMcGp1QzFSV1Vlbm0vOVVwUm9hQUlXQUlHQUtHUUdNUllNM3RVU3FucUxSdFZCRHJjYThNbDhDcG42amcxMTFlQmVaclpBZ1lBb2FBSVdBSVRCb0NhTFl3MjVOVi9sQ2w4NzB5WE9wa1k0UHJWQjVUV1VMbFZTcEdob0FoWUFnWUFvYkFKQ0RBSHJmNGJBOVRPVTRGWGxpSjZqQmNLdWFHTjZrOHBQSmFGWmp1aTFTTURBRkR3QkF3QkF5QnBpTHdkM1hzR3BVRFZNNVM0WHRscXN0d3VRSHJqTzVRUWR0OWpzcThLa1F3ODcrUklXQUlHQUtHZ0NIUUZBVGdkL2Vybks1eWhNclZLaHpyaWZwaHVPRkdMQmNpRlBvQmxiK3F2RlRsNVNxRHFGdlZHQmtDaG9BaFlBZ1lBdE9DQU5iY2UxVklabkdDQ3NGUnYxYXBSWVBVUm9sYW5sdmxyU29ycTZ5ajhtYVZWNmdZR1FLR2dDRmdDQmdDNDRMQW45UlEzS1pYcUpEUTRuYVZSMVFJR0s1TmcyUzRvUkV3WHJUYytWVVdWbGxCWlNtVlJWWHc5NzVFNWNVcUwxVHBXU1hYTlVhR2dDRmdDQmdDaHNBZ0VFQ0RKZG9ZNnl6V1dzekc3TDk1bFFxYUxFejJMeW9ENFZYRFlMaHFXNHVvbjJBcW1PdGNLcGlaV1VvRTB6V0dLeENNREFGRHdCQXdCS1lGQWZnVERQZkpmMzJ5anBidnJNU2hESVRKcWg0alE4QVFNQVFNQVVQQUVEQUVEQUZEd0JBd0JBd0JRNkJoQ1B3ZmUwOXZaTmE5clpNQUFBQUFTVVZPUks1Q1lJST0iCiAgLz4KPC9kZWZzPgo8L3N2Zz4=%0A%20%20%20%20%20%20%20%20"
          alt="App Image"
        />
      </section> -->

      <footer style="margin-top: 50px">
        <p>Copyright &copy; 2023</p>
        <p style="font-weight: bold"><span>PortfolioOne</span></p>
      </footer>
    </div>
  </body>
</html>
'''
            mail.send(message)


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
        if cursor is not None:  # Check if cursor is not None before closing it
            cursor.close()
        if connection is not None:  # Check if connection is not None before closing it
            connection.close()

    return jsonify(result)


@app.route('/api/verifyEmail', methods=['GET'])
def verify_email():
    try:
        token = request.args.get('token')  # Assuming the token is passed as a query parameter
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 400
        
        # Verify and decode the token to extract the email
        decoded_token = jwt.decode(token, "EmailVerificationSecret", algorithms=['HS256'])
        email = decoded_token.get('email')
        
        if not email:
            return jsonify({'error': 'Invalid token or email not found in token'}), 400
        
        # Assuming you have a user table in your database
        # Update the 'is_email_verified' field to True for the user with this email
        # Perform the database update here based on your database structure

        # Create a database connection
        connection = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['db']
        )

        if connection is None:
            result = {
                'status': 500,
                'Message': 'Failed to connect to the database'
            }
            return jsonify(result)
        cursor = connection.cursor(dictionary=True)
        query_check = "SELECT * FROM user_details WHERE email = %s"
        cursor.execute(query_check, (email,))
        existing_user = cursor.fetchone()
        # return jsonify(existing_record)

        if not existing_user:
            result = {
                'status': 404,
                'Message': 'user not found'
            }
            return jsonify(result)


         
        query = f"UPDATE user_details SET is_email_verified = TRUE WHERE email = %s"
        cursor.execute(query, (email,))
        connection.commit()


        
        # For demonstration purposes, a success message is returned
        return jsonify({'message': f'Email {email} has been verified'}), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/addLeaseData', methods=['POST'])
@token_required
def addNewLeaseData():
    try:
        data = request.get_json()

        # Your existing code remains the same until before the insertion part

        # Generate a UUID
        generated_uuid = str(uuid.uuid4())

        # Update the data dictionary with the generated UUID
        data['lease_id'] = generated_uuid  # Assuming the column in the database is named 'uuid'

        auth_header = request.headers.get('Authorization')
      # Get the token by removing 'Bearer ' from the header
        token = auth_header.split(' ')[1]
        
        # Assuming `token` holds the JWT token you received or retrieved
        decoded_token = jwt.decode(token, "PortfolioOne", algorithms=['HS256'])

        # Access the 'user_id' from the decoded token
        user_id = decoded_token.get('user_id')
        data['user_id'] = user_id 
        

        # Create a database connection
        connection = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['db']
        )

        if connection is None:
            result = {
                'status': 500,
                'Message': 'Failed to connect to the database'
            }
            return jsonify(result)

        cursor = connection.cursor(dictionary=True)

        # Insert data into the database dynamically
        try:
            insert_fields = ', '.join(data.keys())
            insert_values = ', '.join(['%s' for _ in data.values()])
            query = f"INSERT INTO lease_data ({insert_fields}) VALUES ({insert_values})"
            insert_data = tuple(data.values())
            cursor.execute(query, insert_data)
            connection.commit()

            result = {
                'status': 200,
                'Message': 'Lease data inserted successfully'
            }
        except Exception as e:
            result = {
                'status': 500,
                'Message': str(e)
            }
        finally:
            cursor.close()
            connection.close()

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/updateLeaseData/<lease_id>', methods=['PUT'])
@token_required
def updateLeaseData(lease_id):
    try:
        data = request.get_json()

        # Create a database connection
        connection = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['db']
        )

        if connection is None:
            result = {
                'status': 500,
                'Message': 'Failed to connect to the database'
            }
            return jsonify(result)

        cursor = connection.cursor(dictionary=True)

        # Check if the record associated with the provided lease_id exists
        query_check = "SELECT * FROM lease_data WHERE lease_id = %s"
        cursor.execute(query_check, (lease_id,))
        existing_record = cursor.fetchone()
        # return jsonify(existing_record)
        print(existing_record)

        if not existing_record:
            result = {
                'status': 404,
                'Message': 'Lease data not found'
            }
            cursor.close()  # Close cursor before returning
            connection.close()  # Close connection before returning
            return jsonify(result)

        # Update the updated_at timestamp
        updated_at = datetime.datetime.now()

        # Update data in the database based on lease_id and update the updated_at column
        try:
            update_fields = ', '.join([f"{key} = %s" for key in data.keys()])
            query = f"UPDATE lease_data SET {update_fields}, updated_at = %s WHERE lease_id = %s"
            updated_at = tuple(list(data.values()) + [updated_at, lease_id])
            cursor.execute(query, updated_at)
            connection.commit()

            result = {
                'status': 200,
                'Message': 'Lease data updated successfully'
            }
            
        except Exception as e:
            # print(e) #this is what is creating the error
            result = {
                'status': 500,
                'Message': str(e)
            }
        finally:
          if cursor is not None:  # Check if cursor is not None before closing it
              cursor.close()
          if connection is not None:  # Check if connection is not None before closing it
              connection.close()

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/deleteLeaseData/<lease_id>', methods=['PUT'])
@token_required
def deleteLeaseData(lease_id):
    try:
        # Create a database connection
        connection = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['db']
        )

        if connection is None:
            result = {
                'status': 500,
                'Message': 'Failed to connect to the database'
            }
            return jsonify(result), 500

        cursor = connection.cursor(dictionary=True)

                # Check if the record associated with the provided lease_id exists
        query_check = "SELECT * FROM lease_data WHERE lease_id = %s"
        cursor.execute(query_check, (lease_id,))


        # data = cursor.fetchone()
       
        existing_record = cursor.fetchone()
        # return jsonify(existing_record['is_deleted'])
        # return jsonify(existing_record)

        if not existing_record:
            result = {
                'status': 404,
                'Message': 'Lease data not found'
            }
            return jsonify(result),404


        # Update the updated_at timestamp
        updated_at = datetime.datetime.now()

        # Soft delete the record by updating the is_deleted column
        try:
            updated_is_deleted = False
            delete_status = 'Un-Deleted'
            if existing_record['is_deleted']==1:
                # return jsonify(1)
                updated_is_deleted = False
                delete_status = 'Un-Deleted'
            else:
                # return jsonify(existing_record['is_deleted'])
                updated_is_deleted = True
                delete_status = 'Deleted'
            
            query = f"UPDATE lease_data SET is_deleted = {updated_is_deleted}, updated_at = %s WHERE lease_id = %s"
            cursor.execute(query, (updated_at, lease_id))
            connection.commit()

            result = {
                'status': 200,
                'Message': f'Lease data {delete_status} successfully'
            }
            return jsonify(result)
        except Exception as e:
            result = {
                'status': 500,
                'Message': str(e)
            }
        finally:
            cursor.close()
            connection.close()

        

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/verifyResetToken', methods=['GET'])
def verify_reset_token():
    try:
        reset_token = request.args.get('token')
        # Verify and decode the reset token
        decoded_token = jwt.decode(reset_token, "ResetPasswordSecret", algorithms=['HS256'])
        email = decoded_token.get('email')

        if not email:
            return jsonify({'error': 'Invalid token or email not found in token'}), 400

        # Validate the token's expiration time (current time should be before the token expiration time)
        current_time = datetime.datetime.utcnow()
        token_exp_time = datetime.datetime.utcfromtimestamp(decoded_token['exp'])

        if current_time > token_exp_time:
            return jsonify({'error': 'Token has expired'}), 400

        # Check if the email exists in the database
        connection = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['db']
        )
        cursor = connection.cursor(dictionary=True)

        query_check_email = "SELECT email FROM user_details WHERE email = %s"
        cursor.execute(query_check_email, (email,))
        existing_email = cursor.fetchone()

        cursor.close()
        connection.close()

        if not existing_email:
            return jsonify({'error': 'Email does not exist in our records'}), 404

        # Return success if the token is valid and email exists
        return jsonify({'Message': 'Token verified and email found', 'status': 200}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 400

    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/setNewPassword', methods=['POST'])
def set_new_password():
    try:
        reset_token = request.json.get('token')
        new_password = request.json.get('new_password')

        # Verify and decode the reset token
        decoded_token = jwt.decode(reset_token, "ResetPasswordSecret", algorithms=['HS256'])
        email = decoded_token.get('email')

        if not email:
            return jsonify({'error': 'Invalid token or email not found in token'}), 400

        # Validate the token's expiration time (current time should be before the token expiration time)
        current_time = datetime.datetime.utcnow()
        token_exp_time = datetime.datetime.utcfromtimestamp(decoded_token['exp'])

        if current_time > token_exp_time:
            return jsonify({'error': 'Token has expired'}), 400

        # Check if the email exists in the database
        connection = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['db']
        )
        cursor = connection.cursor(dictionary=True)

        query_check_email = "SELECT email FROM user_details WHERE email = %s"
        cursor.execute(query_check_email, (email,))
        existing_email = cursor.fetchone()

        if not existing_email:
            return jsonify({'error': 'Email does not exist in our records'}), 404

        # Update the user's password in the database
        update_query = "UPDATE user_details SET password = %s WHERE email = %s"
        cursor.execute(update_query, (new_password, email))
        connection.commit()

        cursor.close()
        connection.close()

        # Return success after updating the password
        return jsonify({'Message': 'Password updated successfully', 'status': 200}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired, time-limit was 10 min, please resend the link & complete the process within 10 min'}), 400

    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/checkEmailVerification', methods=['POST'])
def check_email_verification():
    try:
        data = request.get_json()
        email_to_check = data.get('email')

        if not email_to_check:
            return jsonify({'error': 'Email not provided in the request'}), 400

        # Check if the email exists in the database and is verified
        connection = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['db']
        )
        cursor = connection.cursor(dictionary=True)

        query_check_email = "SELECT is_email_verified FROM user_details WHERE email = %s"
        cursor.execute(query_check_email, (email_to_check,))
        checkEmail = cursor.fetchone()
        existing_email = None
        if checkEmail:
          existing_email = checkEmail['is_email_verified']
        else:
          return jsonify({'Message': 'Email not found in our records','status': 404})
        
        
        print('existing_email', existing_email)
        if not existing_email:
            return jsonify({'Message': 'Email found in our records but unverified','status': 404})
        else:
            return jsonify({'Message': 'Email found in our records & verified', 'status': 200})


    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sendPasswordResetEmail', methods=['POST'])
def send_password_reset_email():
    try:
        data = request.get_json()
        email = data['email']  # Assuming email is sent in the request JSON
        
        # Check if the email exists in the user_details table
        connection = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['db']
        )
        cursor = connection.cursor(dictionary=True)

        query_check_email = "SELECT * FROM user_details WHERE email = %s"
        cursor.execute(query_check_email, (email,))
        existing_email = cursor.fetchone()
        print(existing_email, "user existing")
        # return jsonify({'existing_email': existing_email['fullname']})

        cursor.close() 
        connection.close()

        if not existing_email:
            return jsonify({'error': 'Email does not exist in our records'}), 404
        
        # Generate token with a 10-minute expiry containing the email
        payload = {
            'email': email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        }
        token = jwt.encode(payload, "ResetPasswordSecret", algorithm='HS256')
        
        # Construct the link with the token
        reset_link = f"https://www.portfolioone.io/reset_password?token={token}"
        
        # Send email with the reset link
        # Use your email sending functionality here (code to send an email)
        # Example using Flask-Mail:
        message = Message(subject='Password Reset Link', recipients=[email])
        # message.body = f"Click on the link to reset your password: {reset_link}"
        html_content = f''' 
        <!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Document</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;700&display=swap"
      rel="stylesheet"
    />
    <style>
.logo {{
  max-width: 80%;
}}
.greet {{
  font-size: 52px;
  line-height: normal;
}}
.main-content {{
  font-size: 24px;
}}
h2 {{
  font-size: 42.21px;
}}

.app-advt > p {{
  font-size: 24px;
}}
.app-advt {{
  padding: 40px 0;
}}
/* Media query for mobile devices */
@media screen and (max-width: 480px) {{
  .logo {{
    max-width: 60%;
  }}
  .greet {{
    font-size: 24px;
    line-height: 24px;
  }}
  .main-content {{
    font-size: 18px;
    padding: 0 20px;
  }}
  h2 {{
    font-size: 29.21px;
  }}
  .app-advt > p {{
    font-size: 20px;
  }}
  .app-advt {{
    padding: 40px 20px;
  }}
}}
    </style>
  </head>

  <body
    style="
      text-align: center;

      background-color: #eaf0f3;
      font-family: 'Barlow', serif;
      margin: 100px 0;
    "
  >
    <div class="mail" style="text-align: center">
      <header>
        <div class="header" style="padding-bottom: 55px; margin: auto">
          <img
            class="logo"
            src="data:image/svg+xml;base64,%0APHN2ZwpjbGFzcz0ibG9nbyIKd2lkdGg9IjQ2NCIKaGVpZ2h0PSI2MCIKdmlld0JveD0iMCAwIDQ2NCA2MCIKZmlsbD0ibm9uZSIKeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgo+CjxwYXRoCiAgZD0iTTAgNTUuNjUxNlYzLjAwNzVIMjAuNzY5OUMyNC43NjI3IDMuMDA3NSAyOC4xNjQzIDMuNzcwMDkgMzAuOTc0OCA1LjI5NTI1QzMzLjc4NTEgNi44MDMyOSAzNS45MjcyIDguOTAyNTUgMzcuNDAxIDExLjU5MzFDMzguODkxOSAxNC4yNjYzIDM5LjYzNzUgMTcuMzUwOSAzOS42Mzc1IDIwLjg0NjlDMzkuNjM3NSAyNC4zNDI3IDM4Ljg4MzUgMjcuNDI3NSAzNy4zNzU0IDMwLjEwMDdDMzUuODY3NCAzMi43NzQxIDMzLjY4MjMgMzQuODU2MiAzMC44MjA0IDM2LjM0NzFDMjcuOTc1OSAzNy44MzggMjQuNTMxMyAzOC41ODMzIDIwLjQ4NzEgMzguNTgzM0g3LjI0ODg2VjI5LjY2MzdIMTguNjg3N0MyMC44Mjk3IDI5LjY2MzcgMjIuNTk1IDI5LjI5NTMgMjMuOTgyOCAyOC41NTg0QzI1LjM4ODEgMjcuODA0NCAyNi40MzM2IDI2Ljc2NzYgMjcuMTE5MSAyNS40NDhDMjcuODIxNSAyNC4xMTE1IDI4LjE3MjggMjIuNTc3NyAyOC4xNzI4IDIwLjg0NjlDMjguMTcyOCAxOS4wOTkgMjcuODIxNSAxNy41NzM2IDI3LjExOTEgMTYuMjcxNEMyNi40MzM2IDE0Ljk1MTggMjUuMzg4MSAxMy45MzIxIDIzLjk4MjggMTMuMjEyNEMyMi41Nzc4IDEyLjQ3NTUgMjAuNzk1NSAxMi4xMDcxIDE4LjYzNjMgMTIuMTA3MUgxMS4xMzAzVjU1LjY1MTZIMFpNNjMuODY0NSA1Ni40MjI4QzU5Ljg3MTcgNTYuNDIyOCA1Ni40MTg3IDU1LjU3NDQgNTMuNTA1NCA1My44Nzc5QzUwLjYwOTIgNTIuMTY0MyA0OC4zNzI4IDQ5Ljc4MjQgNDYuNzk2MiA0Ni43MzJDNDUuMjE5NiA0My42NjQ2IDQ0LjQzMTQgNDAuMTA4NSA0NC40MzE0IDM2LjA2NDNDNDQuNDMxNCAzMS45ODU5IDQ1LjIxOTYgMjguNDIxMyA0Ni43OTYyIDI1LjM3MUM0OC4zNzI4IDIyLjMwMzYgNTAuNjA5MiAxOS45MjE2IDUzLjUwNTQgMTguMjI0OUM1Ni40MTg3IDE2LjUxMTIgNTkuODcxNyAxNS42NTQ0IDYzLjg2NDUgMTUuNjU0NEM2Ny44NTczIDE1LjY1NDQgNzEuMzAxOSAxNi41MTEyIDc0LjE5ODEgMTguMjI0OUM3Ny4xMTE0IDE5LjkyMTYgNzkuMzU2MyAyMi4zMDM2IDgwLjkzMjkgMjUuMzcxQzgyLjUwOTQgMjguNDIxMyA4My4yOTc3IDMxLjk4NTkgODMuMjk3NyAzNi4wNjQzQzgzLjI5NzcgNDAuMTA4NSA4Mi41MDk0IDQzLjY2NDYgODAuOTMyOSA0Ni43MzJDNzkuMzU2MyA0OS43ODI0IDc3LjExMTQgNTIuMTY0MyA3NC4xOTgxIDUzLjg3NzlDNzEuMzAxOSA1NS41NzQ0IDY3Ljg1NzMgNTYuNDIyOCA2My44NjQ1IDU2LjQyMjhaTTYzLjkxNTkgNDcuOTQwMUM2NS43MzIzIDQ3Ljk0MDEgNjcuMjQ5MSA0Ny40MjYgNjguNDY1OSA0Ni4zOTc4QzY5LjY4MjQgNDUuMzUyNCA3MC41OTkzIDQzLjkzIDcxLjIxNjMgNDIuMTMwN0M3MS44NTA0IDQwLjMzMTQgNzIuMTY3NCAzOC4yODM0IDcyLjE2NzQgMzUuOTg3MUM3Mi4xNjc0IDMzLjY5MDggNzEuODUwNCAzMS42NDMgNzEuMjE2MyAyOS44NDM3QzcwLjU5OTMgMjguMDQ0MiA2OS42ODI0IDI2LjYyMTggNjguNDY1OSAyNS41NzY2QzY3LjI0OTEgMjQuNTMxMyA2NS43MzIzIDI0LjAwODcgNjMuOTE1OSAyNC4wMDg3QzYyLjA4MjQgMjQuMDA4NyA2MC41NDAxIDI0LjUzMTMgNTkuMjg5IDI1LjU3NjZDNTguMDU1MSAyNi42MjE4IDU3LjEyMTMgMjguMDQ0MiA1Ni40ODcyIDI5Ljg0MzdDNTUuODcwMiAzMS42NDMgNTUuNTYxOSAzMy42OTA4IDU1LjU2MTkgMzUuOTg3MUM1NS41NjE5IDM4LjI4MzQgNTUuODcwMiA0MC4zMzE0IDU2LjQ4NzIgNDIuMTMwN0M1Ny4xMjEzIDQzLjkzIDU4LjA1NTEgNDUuMzUyNCA1OS4yODkgNDYuMzk3OEM2MC41NDAxIDQ3LjQyNiA2Mi4wODI0IDQ3Ljk0MDEgNjMuOTE1OSA0Ny45NDAxWk05MC40MTgxIDU1LjY1MTZWMTYuMTY4NkgxMDEuMDM0VjIzLjA1NzZIMTAxLjQ0NkMxMDIuMTY1IDIwLjYwNzEgMTAzLjM3MyAxOC43NTYyIDEwNS4wNyAxNy41MDUxQzEwNi43NjYgMTYuMjM3MSAxMDguNzIgMTUuNjAzIDExMC45MzEgMTUuNjAzQzExMS40NzkgMTUuNjAzIDExMi4wNyAxNS42MzczIDExMi43MDQgMTUuNzA1OEMxMTMuMzM5IDE1Ljc3NDQgMTEzLjg5NSAxNS44Njg3IDExNC4zNzUgMTUuOTg4NlYyNS43MDUyQzExMy44NjEgMjUuNTUxIDExMy4xNSAyNS40MTM3IDExMi4yNDIgMjUuMjkzOEMxMTEuMzMzIDI1LjE3MzkgMTEwLjUwMiAyNS4xMTQgMTA5Ljc0OCAyNS4xMTRDMTA4LjEzNyAyNS4xMTQgMTA2LjY5OCAyNS40NjUxIDEwNS40MyAyNi4xNjc3QzEwNC4xNzkgMjYuODUzMiAxMDMuMTg1IDI3LjgxMzEgMTAyLjQ0OCAyOS4wNDY4QzEwMS43MjggMzAuMjgwNyAxMDEuMzY4IDMxLjcwMzEgMTAxLjM2OCAzMy4zMTM5VjU1LjY1MTZIOTAuNDE4MVpNMTQzLjAxNyAxNi4xNjg2VjI0LjM5NDNIMTE5LjI0VjE2LjE2ODZIMTQzLjAxN1pNMTI0LjYzOCA2LjcwOTA0SDEzNS41ODlWNDMuNTE4OEMxMzUuNTg5IDQ0LjUyOTggMTM1Ljc0MyA0NS4zMTgxIDEzNi4wNTEgNDUuODgzN0MxMzYuMzYgNDYuNDMyMSAxMzYuNzg4IDQ2LjgxNzcgMTM3LjMzNiA0Ny4wNDA0QzEzNy45MDIgNDcuMjYzMSAxMzguNTUzIDQ3LjM3NDYgMTM5LjI5IDQ3LjM3NDZDMTM5LjgwNCA0Ny4zNzQ2IDE0MC4zMTggNDcuMzMxNiAxNDAuODMyIDQ3LjI0NkMxNDEuMzQ2IDQ3LjE0MzIgMTQxLjc0MSA0Ny4wNjYyIDE0Mi4wMTUgNDcuMDE0OEwxNDMuNzM3IDU1LjE2MzNDMTQzLjE4OSA1NS4zMzQ2IDE0Mi40MTcgNTUuNTMxNyAxNDEuNDI0IDU1Ljc1NDRDMTQwLjQzIDU1Ljk5NDMgMTM5LjIyMiA1Ni4xNCAxMzcuNzk5IDU2LjE5MTRDMTM1LjE2IDU2LjI5NDIgMTMyLjg0NyA1NS45NDI5IDEzMC44NTkgNTUuMTM3NUMxMjguODg4IDU0LjMzMiAxMjcuMzU0IDUzLjA4MTIgMTI2LjI1NyA1MS4zODQ1QzEyNS4xNjEgNDkuNjg4IDEyNC42MjEgNDcuNTQ1OSAxMjQuNjM4IDQ0Ljk1ODNWNi43MDkwNFpNMTcxLjM4MyAxNi4xNjg2VjI0LjM5NDNIMTQ3LjAxNFYxNi4xNjg2SDE3MS4zODNaTTE1Mi41OTIgNTUuNjUxNlYxMy4zMTUyQzE1Mi41OTIgMTAuNDUzNSAxNTMuMTQ5IDguMDc5OTggMTU0LjI2MyA2LjE5NDkzQzE1NS4zOTQgNC4zMDk4OSAxNTYuOTM3IDIuODk2MSAxNTguODkgMS45NTM1OUMxNjAuODQ0IDEuMDExMDYgMTYzLjA2MyAwLjUzOTgwNSAxNjUuNTQ4IDAuNTM5ODA1QzE2Ny4yMjcgMC41Mzk4MDUgMTY4Ljc2MSAwLjY2ODMzOCAxNzAuMTQ5IDAuOTI1MzhDMTcxLjU1NCAxLjE4MjQ1IDE3Mi42IDEuNDEzNzkgMTczLjI4NSAxLjYxOTQxTDE3MS4zMzEgOS44NDUwMUMxNzAuOTAzIDkuNzA3OTYgMTcwLjM3MiA5LjU3OTM1IDE2OS43MzggOS40NTk0OEMxNjkuMTIxIDkuMzM5NTQgMTY4LjQ4NyA5LjI3OTU2IDE2Ny44MzYgOS4yNzk1NkMxNjYuMjI1IDkuMjc5NTYgMTY1LjEwMiA5LjY1NjU2IDE2NC40NjggMTAuNDEwNkMxNjMuODM0IDExLjE0NzUgMTYzLjUxNyAxMi4xODQzIDE2My41MTcgMTMuNTIxVjU1LjY1MTZIMTUyLjU5MlpNMTk0LjQ5OCA1Ni40MjI4QzE5MC41MDUgNTYuNDIyOCAxODcuMDUyIDU1LjU3NDQgMTg0LjEzOSA1My44Nzc5QzE4MS4yNDMgNTIuMTY0MyAxNzkuMDA3IDQ5Ljc4MjQgMTc3LjQzIDQ2LjczMkMxNzUuODU0IDQzLjY2NDYgMTc1LjA2NSA0MC4xMDg1IDE3NS4wNjUgMzYuMDY0M0MxNzUuMDY1IDMxLjk4NTkgMTc1Ljg1NCAyOC40MjEzIDE3Ny40MyAyNS4zNzFDMTc5LjAwNyAyMi4zMDM2IDE4MS4yNDMgMTkuOTIxNiAxODQuMTM5IDE4LjIyNDlDMTg3LjA1MiAxNi41MTEyIDE5MC41MDUgMTUuNjU0NCAxOTQuNDk4IDE1LjY1NDRDMTk4LjQ5MSAxNS42NTQ0IDIwMS45MzYgMTYuNTExMiAyMDQuODMyIDE4LjIyNDlDMjA3Ljc0NSAxOS45MjE2IDIwOS45OSAyMi4zMDM2IDIxMS41NjcgMjUuMzcxQzIxMy4xNDMgMjguNDIxMyAyMTMuOTMxIDMxLjk4NTkgMjEzLjkzMSAzNi4wNjQzQzIxMy45MzEgNDAuMTA4NSAyMTMuMTQzIDQzLjY2NDYgMjExLjU2NyA0Ni43MzJDMjA5Ljk5IDQ5Ljc4MjQgMjA3Ljc0NSA1Mi4xNjQzIDIwNC44MzIgNTMuODc3OUMyMDEuOTM2IDU1LjU3NDQgMTk4LjQ5MSA1Ni40MjI4IDE5NC40OTggNTYuNDIyOFpNMTk0LjU1IDQ3Ljk0MDFDMTk2LjM2NiA0Ny45NDAxIDE5Ny44ODMgNDcuNDI2IDE5OS4xIDQ2LjM5NzhDMjAwLjMxNiA0NS4zNTI0IDIwMS4yMzMgNDMuOTMgMjAxLjg1IDQyLjEzMDdDMjAyLjQ4NCA0MC4zMzE0IDIwMi44MDEgMzguMjgzNCAyMDIuODAxIDM1Ljk4NzFDMjAyLjgwMSAzMy42OTA4IDIwMi40ODQgMzEuNjQzIDIwMS44NSAyOS44NDM3QzIwMS4yMzMgMjguMDQ0MiAyMDAuMzE2IDI2LjYyMTggMTk5LjEgMjUuNTc2NkMxOTcuODgzIDI0LjUzMTMgMTk2LjM2NiAyNC4wMDg3IDE5NC41NSAyNC4wMDg3QzE5Mi43MTYgMjQuMDA4NyAxOTEuMTc0IDI0LjUzMTMgMTg5LjkyMyAyNS41NzY2QzE4OC42ODkgMjYuNjIxOCAxODcuNzU1IDI4LjA0NDIgMTg3LjEyMSAyOS44NDM3QzE4Ni41MDQgMzEuNjQzIDE4Ni4xOTYgMzMuNjkwOCAxODYuMTk2IDM1Ljk4NzFDMTg2LjE5NiAzOC4yODM0IDE4Ni41MDQgNDAuMzMxNCAxODcuMTIxIDQyLjEzMDdDMTg3Ljc1NSA0My45MyAxODguNjg5IDQ1LjM1MjQgMTg5LjkyMyA0Ni4zOTc4QzE5MS4xNzQgNDcuNDI2IDE5Mi43MTYgNDcuOTQwMSAxOTQuNTUgNDcuOTQwMVpNMjMyLjAwMiAzLjAwNzVWNTUuNjUxNkgyMjEuMDUyVjMuMDA3NUgyMzIuMDAyWk0yNDAuNzc0IDU1LjY1MTZWMTYuMTY4NkgyNTEuNzIzVjU1LjY1MTZIMjQwLjc3NFpNMjQ2LjI3NSAxMS4wNzg5QzI0NC42NDYgMTEuMDc4OSAyNDMuMjQ5IDEwLjUzOTIgMjQyLjA4NCA5LjQ1OTQ4QzI0MC45MzggOC4zNjI3NCAyNDAuMzY0IDcuMDUxNzYgMjQwLjM2NCA1LjUyNjZDMjQwLjM2NCA0LjAxODU2IDI0MC45MzggMi43MjQ3NCAyNDIuMDg0IDEuNjQ1MTNDMjQzLjI0OSAwLjU0ODM3IDI0NC42NDYgMCAyNDYuMjc1IDBDMjQ3LjkwNCAwIDI0OS4yOTEgMC41NDgzNyAyNTAuNDQgMS42NDUxM0MyNTEuNjA1IDIuNzI0NzQgMjUyLjE4NyA0LjAxODU2IDI1Mi4xODcgNS41MjY2QzI1Mi4xODcgNy4wNTE3NiAyNTEuNjA1IDguMzYyNzQgMjUwLjQ0IDkuNDU5NDhDMjQ5LjI5MSAxMC41MzkyIDI0Ny45MDQgMTEuMDc4OSAyNDYuMjc1IDExLjA3ODlaTTI3OC4zMzUgNTYuNDIyOEMyNzQuMzQ0IDU2LjQyMjggMjcwLjg4OSA1NS41NzQ0IDI2Ny45NzYgNTMuODc3OUMyNjUuMDgxIDUyLjE2NDMgMjYyLjg0NCA0OS43ODI0IDI2MS4yNjkgNDYuNzMyQzI1OS42OTEgNDMuNjY0NiAyNTguOTAyIDQwLjEwODUgMjU4LjkwMiAzNi4wNjQzQzI1OC45MDIgMzEuOTg1OSAyNTkuNjkxIDI4LjQyMTMgMjYxLjI2OSAyNS4zNzFDMjYyLjg0NCAyMi4zMDM2IDI2NS4wODEgMTkuOTIxNiAyNjcuOTc2IDE4LjIyNDlDMjcwLjg4OSAxNi41MTEyIDI3NC4zNDQgMTUuNjU0NCAyNzguMzM1IDE1LjY1NDRDMjgyLjMyOCAxNS42NTQ0IDI4NS43NzQgMTYuNTExMiAyODguNjY5IDE4LjIyNDlDMjkxLjU4MSAxOS45MjE2IDI5My44MjggMjIuMzAzNiAyOTUuNDAzIDI1LjM3MUMyOTYuOTgxIDI4LjQyMTMgMjk3Ljc2OCAzMS45ODU5IDI5Ny43NjggMzYuMDY0M0MyOTcuNzY4IDQwLjEwODUgMjk2Ljk4MSA0My42NjQ2IDI5NS40MDMgNDYuNzMyQzI5My44MjggNDkuNzgyNCAyOTEuNTgxIDUyLjE2NDMgMjg4LjY2OSA1My44Nzc5QzI4NS43NzQgNTUuNTc0NCAyODIuMzI4IDU2LjQyMjggMjc4LjMzNSA1Ni40MjI4Wk0yNzguMzg4IDQ3Ljk0MDFDMjgwLjIwNSA0Ny45NDAxIDI4MS43MiA0Ny40MjYgMjgyLjkzNiA0Ni4zOTc4QzI4NC4xNTUgNDUuMzUyNCAyODUuMDcxIDQzLjkzIDI4NS42ODcgNDIuMTMwN0MyODYuMzIxIDQwLjMzMTQgMjg2LjYzNyAzOC4yODM0IDI4Ni42MzcgMzUuOTg3MUMyODYuNjM3IDMzLjY5MDggMjg2LjMyMSAzMS42NDMgMjg1LjY4NyAyOS44NDM3QzI4NS4wNzEgMjguMDQ0MiAyODQuMTU1IDI2LjYyMTggMjgyLjkzNiAyNS41NzY2QzI4MS43MiAyNC41MzEzIDI4MC4yMDUgMjQuMDA4NyAyNzguMzg4IDI0LjAwODdDMjc2LjU1NCAyNC4wMDg3IDI3NS4wMTIgMjQuNTMxMyAyNzMuNzYgMjUuNTc2NkMyNzIuNTI3IDI2LjYyMTggMjcxLjU5MyAyOC4wNDQyIDI3MC45NTkgMjkuODQzN0MyNzAuMzQxIDMxLjY0MyAyNzAuMDMyIDMzLjY5MDggMjcwLjAzMiAzNS45ODcxQzI3MC4wMzIgMzguMjgzNCAyNzAuMzQxIDQwLjMzMTQgMjcwLjk1OSA0Mi4xMzA3QzI3MS41OTMgNDMuOTMgMjcyLjUyNyA0NS4zNTI0IDI3My43NiA0Ni4zOTc4QzI3NS4wMTIgNDcuNDI2IDI3Ni41NTQgNDcuOTQwMSAyNzguMzg4IDQ3Ljk0MDFaIgogIGZpbGw9IiMwMDcyQjIiCi8+CjxwYXRoCiAgZD0iTTM5My4zNTggMzIuODI4NFY1NS42NTQ1SDM4Mi40MDhWMTYuMTcxNUgzOTIuODQ0VjIzLjEzNzRIMzkzLjMwN0MzOTQuMTgxIDIwLjg0MTEgMzk1LjY0NSAxOS4wMjQ3IDM5Ny43MDEgMTcuNjg3OUMzOTkuNzU5IDE2LjMzNDEgNDAyLjI1MiAxNS42NTczIDQwNS4xODEgMTUuNjU3M0M0MDcuOTI0IDE1LjY1NzMgNDEwLjMxNSAxNi4yNTcxIDQxMi4zNTQgMTcuNDU2NkM0MTQuMzkzIDE4LjY1NjIgNDE1Ljk3OCAyMC4zNjk4IDQxNy4xMSAyMi41OTc2QzQxOC4yMzkgMjQuODA4MyA0MTguODA2IDI3LjQ0NzUgNDE4LjgwNiAzMC41MTQ5VjU1LjY1NDVINDA3Ljg1NFYzMi40Njg0QzQwNy44NzEgMzAuMDUyMSA0MDcuMjU2IDI4LjE2NzIgNDA2LjAwNCAyNi44MTM0QzQwNC43NTQgMjUuNDQyNCA0MDMuMDMxIDI0Ljc1NjkgNDAwLjgzOCAyNC43NTY5QzM5OS4zNjMgMjQuNzU2OSAzOTguMDYgMjUuMDczOSAzOTYuOTMxIDI1LjcwOEMzOTUuODE2IDI2LjM0MjEgMzk0Ljk0MyAyNy4yNjc1IDM5NC4zMDggMjguNDg0QzM5My42OTEgMjkuNjgzNyAzOTMuMzc1IDMxLjEzMTcgMzkzLjM1OCAzMi44Mjg0Wk00NDUuNDMgNTYuNDI1NkM0NDEuMzY5IDU2LjQyNTYgNDM3Ljg3MyA1NS42MDMxIDQzNC45NDEgNTMuOTU4QzQzMi4wMjkgNTIuMjk1OCA0MjkuNzg1IDQ5Ljk0NzggNDI4LjIwNyA0Ni45MTQ2QzQyNi42MzEgNDMuODY0MyA0MjUuODQyIDQwLjI1NzEgNDI1Ljg0MiAzNi4wOTNDNDI1Ljg0MiAzMi4wMzE0IDQyNi42MzEgMjguNDY2OSA0MjguMjA3IDI1LjM5OTRDNDI5Ljc4NSAyMi4zMzIgNDMyLjAwMiAxOS45NDE2IDQzNC44NjQgMTguMjI3N0M0MzcuNzQ1IDE2LjUxNDEgNDQxLjEyIDE1LjY1NzMgNDQ0Ljk5MyAxNS42NTczQzQ0Ny41OTYgMTUuNjU3MyA0NTAuMDIxIDE2LjA3NzEgNDUyLjI2OCAxNi45MTY4QzQ1NC41MjkgMTcuNzM5MyA0NTYuNSAxOC45ODE3IDQ1OC4xNzkgMjAuNjQ0MkM0NTkuODc1IDIyLjMwNjQgNDYxLjE5NSAyNC4zOTcxIDQ2Mi4xMzkgMjYuOTE2MkM0NjMuMDggMjkuNDE4IDQ2My41NTMgMzIuMzQ4NSA0NjMuNTUzIDM1LjcwNzRWMzguNzE0OEg0MzAuMjEyVjMxLjkyODZINDUzLjI0NUM0NTMuMjQ1IDMwLjM1MjEgNDUyLjkwMiAyOC45NTU1IDQ1Mi4yMTcgMjcuNzM4N0M0NTEuNTI5IDI2LjUyMTkgNDUwLjU3OSAyNS41NzEgNDQ5LjM2MyAyNC44ODU1QzQ0OC4xNjMgMjQuMTgyOSA0NDYuNzY2IDIzLjgzMTYgNDQ1LjE3MiAyMy44MzE2QzQ0My41MTEgMjMuODMxNiA0NDIuMDM3IDI0LjIxNzEgNDQwLjc1MSAyNC45ODgzQzQzOS40ODQgMjUuNzQyMyA0MzguNDkgMjYuNzYyIDQzNy43NjkgMjguMDQ3MUM0MzcuMDUgMjkuMzE1MyA0MzYuNjgxIDMwLjcyOSA0MzYuNjY0IDMyLjI4ODZWMzguNzQwNkM0MzYuNjY0IDQwLjY5NCA0MzcuMDIzIDQyLjM4MjEgNDM3Ljc0NSA0My44MDQ1QzQzOC40ODEgNDUuMjI2OCA0MzkuNTE4IDQ2LjMyMzUgNDQwLjg1NSA0Ny4wOTQ2QzQ0Mi4xOTIgNDcuODY1OCA0NDMuNzc3IDQ4LjI1MTQgNDQ1LjYxMSA0OC4yNTE0QzQ0Ni44MjcgNDguMjUxNCA0NDcuOTM5IDQ4LjA4IDQ0OC45NTIgNDcuNzM3NEM0NDkuOTYzIDQ3LjM5NDUgNDUwLjgyNyA0Ni44ODA0IDQ1MS41NDkgNDYuMTk0OUM0NTIuMjY4IDQ1LjUwOTYgNDUyLjgxNSA0NC42Njk3IDQ1My4xOTIgNDMuNjc1OUw0NjMuMzIxIDQ0LjM0NDJDNDYyLjgwNyA0Ni43Nzc2IDQ2MS43NTMgNDguOTAyNiA0NjAuMTU4IDUwLjcxOUM0NTguNTgyIDUyLjUxODUgNDU2LjU0MyA1My45MjM3IDQ1NC4wNDEgNTQuOTM0N0M0NTEuNTU2IDU1LjkyODYgNDQ4LjY4NSA1Ni40MjU2IDQ0NS40MyA1Ni40MjU2WiIKICBmaWxsPSIjMDA3MkIyIgovPgo8cGF0aAogIGQ9Ik0zMjkuMTI5IDMyLjUzNkMzMjkuMTI5IDMyLjM3MjYgMzI4Ljg1NCAzMi4yNDA2IDMyOC41MTcgMzIuMjQwNkMzMjguMTgxIDMyLjI0MDYgMzI3LjY2NyAzMi4wNDk1IDMyNy4zNzggMzEuODE3OUMzMjcuMDg4IDMxLjU4NiAzMjYuNjk3IDMxLjU4NiAzMjYuNTEyIDMxLjgxNzlDMzI2LjMyNiAzMi4wNDkgMzI2LjQwMyAzMi4yNDA2IDMyNi42OCAzMi4yNDA2QzMyNi45NTggMzIuMjQwNiAzMjcuMzQ5IDMyLjM3MjYgMzI3LjU0NyAzMi41MzZDMzI3Ljc0NSAzMi42OTc5IDMyOC4xODEgMzIuODMwOCAzMjguNTE3IDMyLjgzMDhDMzI4Ljg1NCAzMi44MzA2IDMyOS4xMjkgMzIuNjk2OSAzMjkuMTI5IDMyLjUzNloiCiAgZmlsbD0iIzE3NTQyRiIKLz4KPHBhdGgKICBkPSJNMzMxLjI4NCAzMy4xMjcxQzMzMS4wNzQgMzIuOTY1NCAzMzAuODY2IDMyLjcxODEgMzMwLjgyMSAzMi41Nzg5TDMzMC4zOTggMzIuODMxMkwzMjkuOTc2IDMzLjA4NDRDMzI5LjUxIDMzLjI4NjMgMzI4Ljc1IDMzLjc3ODggMzI4LjI4NyAzNC4xODE3SDMyOS4xMzJIMzI5LjYzOEgzMzEuMjg0QzMzMS40OTQgMzQuMTgxNyAzMzEuNjY1IDM0LjAxMTYgMzMxLjY2NSAzMy44MDMxQzMzMS42NjUgMzMuNTkzNyAzMzEuNDk0IDMzLjI4OTcgMzMxLjI4NCAzMy4xMjcxWiIKICBmaWxsPSIjMTc1NDJGIgovPgo8cGF0aAogIGQ9Ik0zNTAuMDcyIDE5LjQ3NDZWMTkuNDk0MUMzNDkuODA5IDE5Ljg4ODkgMzQ5LjU5MiAyMC40MDI2IDM0OS41OTIgMjAuNjM1MkMzNDkuNTkyIDIwLjg2NjUgMzQ5LjYzMyAyMS4xOCAzNDkuNjg2IDIxLjMzMkMzNDkuNzM3IDIxLjQ4MjggMzUwLjAxNyAyMS4zOTY5IDM1MC4zMDYgMjEuMTQwOUMzNTAuNTk2IDIwLjg4NTYgMzUwLjkyOSAyMC42MTk3IDM1MS4wNDQgMjAuNTQ5N0MzNTEuMTYgMjAuNDggMzUxLjI1NCAyMC4xOTM2IDM1MS4yNTQgMTkuOTE1NlYxOS43NDdDMzUxLjI1NCAxOS41NzgxIDM1MC45NiAxOS4xNTY4IDM1MC44NzYgMTguOTg3NEMzNTAuNzkxIDE4LjgxODggMzUwLjUzOCAxOC40ODE0IDM1MC41MTYgMTguMjI4MUwzNTAuNDk3IDE3Ljk3NUMzNTAuMzMzIDE3LjYyNjggMzUwLjAzMSAxNy4zNDA5IDM0OS44MjQgMTcuMzQwOUgzNDkuNzhDMzQ5LjczNCAxNy4zNDA5IDM0OS42OTMgMTcuODA2MyAzNDkuNjA5IDE3LjkzMjNMMzQ5LjUyNCAxOC4wNTk5QzM0OS42NjQgMTguNDc4MSAzNDkuOTEgMTkuMTA0NCAzNTAuMDcyIDE5LjQ1MzhWMTkuNDc0NloiCiAgZmlsbD0iIzE3NTQyRiIKLz4KPHBhdGgKICBkPSJNMzQ4LjM4MSAyMC40Njc2TDM0OC41OTQgMjAuNDI0OUMzNDguODA0IDIwLjMwODYgMzQ5LjA1IDE5LjkzODUgMzQ5LjE0NCAxOS42MDIxQzM0OS4yMzYgMTkuMjY0MyAzNDkuMjkzIDE4Ljc5ODkgMzQ5LjI2OSAxOC41NjdMMzQ4Ljk3MyAxOC43MzYyQzM0OC42NzggMTguOTA0OCAzNDguMzgxIDE4Ljk4ODUgMzQ4LjM4MSAxOS4yNDI0QzM0OC4zODEgMTkuNDk1NSAzNDguMTcxIDIwLjUwOTYgMzQ4LjM4MSAyMC40Njc2WiIKICBmaWxsPSIjMTc1NDJGIgovPgo8cGF0aAogIGQ9Ik0zNjUuNDM4IDQyLjgzNzVDMzY0LjgxMyA0My42NTYyIDM2NC4yMTIgNDQuNDA5NSAzNjQuMTA0IDQ0LjUxMTNDMzYzLjk5NyA0NC42MTI5IDM2My42NjcgNDUuMDkzNSAzNjMuMzcgNDUuNTgzM0wzNjMuMjg2IDQ1Ljc1MjVMMzYzLjIwMSA0NS45MjExQzM2My40MzMgNDYuMjQ0IDM2My42ODYgNDYuNTEyMyAzNjMuNzY2IDQ2LjUxMjNDMzYzLjg0NSA0Ni41MTIzIDM2NC4wMDkgNDYuNTMwMSAzNjQuMTMgNDYuNTUzOEwzNjQuMjE1IDQ2LjUxMjNDMzY0LjI5OSA0Ni40NjkzIDM2NC4zODMgNDYuNDI3NiAzNjQuNDY4IDQ2LjIxNTVDMzY0LjU1MiA0Ni4wMDUzIDM2NC42MzcgNDUuOTYyNCAzNjQuNjc4IDQ1LjYyNTNDMzY0LjcyMSA0NS4yODc1IDM2NS4zMTIgNDQuMzE2NiAzNjUuMzUzIDQ0LjE0ODFMMzY1LjM5NyA0My45NzhDMzY1LjYwNCA0My4yODI5IDM2NS45MyA0Mi4yNzUzIDM2Ni4xMTYgNDEuNzQwOEwzNjUuNzc4IDQyLjI4OTNMMzY1LjQzOCA0Mi44Mzc1WiIKICBmaWxsPSIjMTc1NDJGIgovPgo8cGF0aAogIGQ9Ik0zNDUuNTM3IDAuMTYxMTMzQzMyOS4wNCAwLjE2MTEzMyAzMTUuNjE3IDEzLjU4MzEgMzE1LjYxNyAzMC4wODA2QzMxNS42MTcgNDYuNTc4IDMyOS4wNCA2MCAzNDUuNTM3IDYwQzM2Mi4wMzMgNjAgMzc1LjQ1NiA0Ni41NzggMzc1LjQ1NiAzMC4wODA2QzM3NS40NTYgMTMuNTgzMSAzNjIuMDMzIDAuMTYxMTMzIDM0NS41MzcgMC4xNjExMzNaTTM2MS40MTEgNi4zNDA0OUMzNjIuMjk0IDYuOTMzMDEgMzYzLjE0MSA3LjU3MzIxIDM2My45NTIgOC4yNTc3MkMzNjMuODQxIDguNDU4MTggMzYzLjgwOSA4LjYxMzMyIDM2My45MTUgOC42ODk1QzM2NC4xNDcgOC44NTg2NiAzNjMuNjYyIDkuNzM5OTQgMzYzLjMxMiAxMC4zMDg2TDM2Mi40ODkgOS42MTgzM0MzNjIuNDg5IDkuNjE4MzMgMzYxLjcyOSA3LjU5MzE5IDM2MS40NzYgNy4zMzg1MUMzNjEuMzE3IDcuMTc5NjMgMzYxLjM1OCA2LjY4NDkgMzYxLjQxMSA2LjM0MDQ5Wk0zNTUuMTQ1IDI2LjMzN0wzNTUuNjYxIDI1LjYyNEgzNTYuMzI1TDM1Ny42NzYgMjYuMDgyN0wzNTcuNTkxIDI1LjA2OTNIMzU4LjE4MkwzNTkuMzY1IDI2LjExN0gzNjEuNDc2QzM2MS40NzYgMjYuMTE3IDM2MS4yMjMgMjYuOTI3MiAzNjEuMDU0IDI3LjIzODlDMzYwLjg4NSAyNy41NTI5IDM1OS43ODcgMjcuODU1NyAzNTkuNzg3IDI3Ljg1NTdIMzU4LjI2N0wzNTcuNTA3IDI3Ljc3MTJMMzU2LjU3OCAyOC4zNjE0TDM1NS42NjEgMjcuOTM5OUMzNTUuNjYxIDI3LjkzOTkgMzU0LjU1NCAyNy4wMTE0IDM1NC40NjcgMjYuNzU3MUMzNTQuMzgyIDI2LjUwNDcgMzUzLjExOCAyNi4zMzQ2IDM1Mi44NjUgMjYuMjUwMkMzNTIuNjExIDI2LjE2NTUgMzUyLjE4OSAyNS45OTY4IDM1MS4xNzMgMjYuMjUwMkMzNTEuMTczIDI2LjI1MDIgMzUwLjc1MyAyNi41ODggMzQ5Ljk5MyAyNi43NTcxQzM0OS4yMzMgMjYuOTI3MiAzNTAuNzUzIDI1Ljc0MyAzNTEuMTczIDI1LjYyMjZDMzUxLjU5OCAyNS41MDE5IDM1MS43NjcgMjQuNzMwNSAzNTIuMDIgMjQuMTM5NEMzNTIuMjcxIDIzLjU0ODIgMzUzLjM2OSAyNC4xMzk0IDM1My4zNjkgMjQuMTM5NEgzNTQuMDQ0QzM1NC4wNDQgMjQuMTM5NCAzNTQuODA0IDI0LjY0NTYgMzU1LjA2IDI1LjA2NzlDMzU1LjMxMSAyNS40OTAzIDM1NC44OTEgMjUuMzIxMiAzNTQuNzIgMjUuNjIxNkMzNTQuNTU0IDI1LjkyNTQgMzU1LjE0NSAyNi4zMzcgMzU1LjE0NSAyNi4zMzdaTTM1OC44NTggMjMuMjk2OEMzNTguODU4IDIzLjI5NjggMzU5LjQ0OSAyMy4wNDM3IDM1OS43MDMgMjIuNzQ1NUMzNTkuOTU2IDIyLjQ0NjMgMzYwLjQ2MyAyMi43NDU1IDM2MC40NjMgMjIuNzQ1NUwzNjAuOTI2IDIxLjYwODVDMzYwLjkyNiAyMS42MDg1IDM2MS4zOTIgMjIuNDUyNiAzNjEuNDc2IDIyLjcwNjZDMzYxLjU2IDIyLjk2IDM2Mi40ODkgMjMuMzgyNSAzNjIuNDg5IDIzLjM4MjVMMzYxLjk4MyAyMy44ODM5TDM2MC42MzIgMjMuODc4NkMzNjAuNjMyIDIzLjg3ODYgMzYwLjA0IDIzLjg4ODUgMzU5LjM2NSAyMy44Nzg2TDM1OC44NTggMjMuMjk2OFpNMzYxLjg5OCAyOS4yOTE2QzM2MS44OTggMjkuMjkxNiAzNjIuMzIxIDI5Ljg4MzIgMzYyLjQ4OSAzMC40MzQ1QzM2Mi42NTggMzAuOTg3MSAzNjMuNjcyIDMxLjkwOTggMzYzLjg0MSAzMi43MjU4QzM2NC4wMSAzMy41NDE2IDM2My44NDEgMzQuMTg4NSAzNjMuODQxIDM0LjE4ODVDMzYzLjg0MSAzNC4xODg1IDM2My4wODEgMzMuMjYwMiAzNjIuODI3IDMyLjgzOEMzNjIuNTc0IDMyLjQxNTUgMzYxLjgxNCAzMS42NTYyIDM2MS40NzYgMzEuNDAyOEMzNjEuMTM4IDMxLjE1MDQgMzYxLjA1NCAyOS4yOTE4IDM2MS4wNTQgMjkuMjkxOEwzNjEuODk4IDI5LjI5MTZaTTM0Mi4zNzYgMTMuNzcwNEwzNDIuMzkzIDEzLjc1NjRMMzQyLjUzMyAxMy42NTI2QzM0Mi40ODQgMTMuNjkgMzQyLjQ0MSAxMy43MjM2IDM0Mi40MDcgMTMuNzQ5NkMzNDIuNDY4IDEzLjcwNCAzNDIuNDk0IDEzLjY3OTkgMzQyLjM5MyAxMy43NTY0QzM0Mi4zNzYgMTMuNzcwNiAzNDIuMzU0IDEzLjc4OSAzNDIuMzM1IDEzLjgwNjNDMzQyLjM0NCAxMy43OTc5IDM0Mi4zNTcgMTMuNzg5NCAzNDIuMzY2IDEzLjc4QzM0Mi4zNDkgMTMuNzk1IDM0Mi4zMzUgMTMuODA2MyAzNDIuMzMyIDEzLjgwNzhDMzQyLjMzMiAxMy44MDc4IDM0Mi4zMzUgMTMuODA3OCAzNDIuMzM1IDEzLjgwNjNDMzQyLjMxNSAxMy44MjEzIDM0Mi4yOTkgMTMuODM1MyAzNDIuMjgyIDEzLjg0NzhDMzQyLjI5OSAxMy44MzMzIDM0Mi4zNTkgMTMuNzg0OSAzNDIuMzc2IDEzLjc3MDRaTTMxNi45NzMgMzAuNDgxOEMzMTcuMDI5IDMwLjUzMDYgMzE3LjA2MiAzMC41NTk1IDMxNy4wNjIgMzAuNTU5NUMzMTcuMDYyIDMwLjU1OTUgMzE3LjAyNCAzMC41ODcgMzE2Ljk3NiAzMC42MzI5QzMxNi45NzYgMzAuNTgyIDMxNi45NzYgMzAuNTMyIDMxNi45NzMgMzAuNDgxOFpNMzE2Ljk5NyAzMS4yNzU5QzMxNy4wMTcgMzEuMjkwOSAzMTcuMDM2IDMxLjMwNTMgMzE3LjA2MiAzMS4zMjAzQzMxNy42NTQgMzEuNjU4MSAzMTcuMDYyIDMxLjQwNDMgMzE3LjY1NCAzMS42NTgxQzMxOC4yNDUgMzEuOTExNyAzMTguMjQ1IDMxLjkxMTQgMzE4LjI0NSAzMS45MTE0QzMxOC4yNDUgMzEuOTExNCAzMTguMTYgMzEuNzQyNSAzMTguMjQ1IDMxLjQwNDNDMzE4LjMyOSAzMS4wNjY1IDMxOC42NjcgMzEuNjU3NiAzMTguMzI5IDMxLjA2NjVDMzE3Ljk5MSAzMC40NzQ4IDMxOC4xNiAzMS4xNTExIDMxNy45OTEgMzAuNDc0OEwzMTcuODIzIDI5Ljc5ODNDMzE3LjgyMyAyOS43OTgzIDMxNy42NTQgMjkuMzc1OCAzMTcuOTA3IDI5LjM3NThDMzE4LjE2IDI5LjM3NTggMzE4LjQ3NiAzMC4zMDUyIDMxOC40NzYgMzAuMzA1MkMzMTguNDc2IDMwLjMwNTIgMzE4LjkyIDMxLjMxOTMgMzE5LjE3NCAzMS40ODhMMzE5LjQyNyAzMS42NTY2QzMxOS40MjcgMzEuNjU2NiAzMTkuNzY1IDMxLjk5NDQgMzE5Ljg0OSAzMi4zMzI1QzMxOS45MzQgMzIuNjcwMyAzMTkuNDI3IDMyLjc1NDcgMzE5Ljg0OSAzMy4wMDgxQzMyMC4yNjkgMzMuMjYwNSAzMTkuNjggMzIuNzU0NyAzMjAuMjY5IDMzLjI2MDVDMzIwLjg2MyAzMy43Njc0IDMyMS4yMDEgMzMuNjgyIDMyMS40NTQgMzMuODUxNkMzMjEuNzA3IDM0LjAyMDggMzIxLjc5MiAzMy4zNDU0IDMyMi4wNDUgMzMuODUxNkMzMjIuMjk4IDM0LjM1NzYgMzIxLjUzOCAzMy44NTE2IDMyMi4yOTggMzQuMzU3NkMzMjMuMDU2IDM0Ljg2NiAzMjMuNDc4IDM1LjExOTMgMzIzLjQ3OCAzNS4xMTkzQzMyMy40NzggMzUuMTE5MyAzMjMuNTYzIDM0LjYxMjIgMzI0LjA3MiAzNS4xMTkzQzMyNC41NzkgMzUuNjI0OCAzMjUuMTcgMzUuNzA5NSAzMjUuMTcgMzUuNzA5NUMzMjUuMTcgMzUuNzA5NSAzMjUuMjU0IDM1Ljk2NDEgMzI1LjY3NiAzNi4zMDA5QzMyNi4wOTkgMzYuNjM5IDMyNS42NzYgMzYuMTMyMyAzMjYuMDk5IDM2LjYzOUwzMjYuNTIxIDM3LjE0NDRMMzI3LjI4MSAzNy42NTE0SDMyNy42MTlMMzI3Ljg3MiAzOC4wNzM5TDMyOC41NDggMzguOTE3NFYzOS41MDk4QzMyOC41NDggMzkuNTA5OCAzMjguMTI1IDM4LjkxNzQgMzI4LjEyNSAzOS41MDk4QzMyOC4xMjUgNDAuMTAwOSAzMjguMjEgMzkuNTk0IDMyOC4xMjUgNDAuMTAwOUwzMjguMDQxIDQwLjYwNzFMMzI4LjU0OCA0MS4yODQyVjQyLjQ2NkMzMjguNTQ4IDQyLjQ2NiAzMjkuMDU0IDQzLjA1NzIgMzI5LjMwOCA0My4yMjQ4QzMyOS41NTkgNDMuMzkzNSAzMjguODg2IDQyLjgwMzMgMzI5LjU1OSA0My4zOTM1TDMzMC4yMzQgNDMuOTg1MUwzMzEuMTYzIDQ0LjgyOTlWNDUuMTY3N0MzMzEuMTYzIDQ1LjE2NzcgMzMxLjc1NCA0NC43NDU0IDMzMi4wMDggNDUuMTY3N0MzMzIuMjYxIDQ1LjU5MDcgMzMyLjU5OSA0Ni4wMTI3IDMzMi41OTkgNDYuMDEyN1Y0Ni4zNTA1QzMzMi41OTkgNDYuMzUwNSAzMzIuOTM3IDQ1LjY3NDkgMzMzLjEwNiA0Ni4zNTA1QzMzMy4yNzUgNDcuMDI1MyAzMzMuMTA2IDQ3LjM2MzEgMzMzLjEwNiA0Ny4zNjMxQzMzMy4xMDYgNDcuMzYzMSAzMzMuNjE1IDQ3Ljc4NTQgMzMzLjY5NyA0OC4wMzg3QzMzMy43ODEgNDguMjkyMSAzMzMuNTI4IDQ4LjU0NSAzMzMuNjk3IDQ4Ljc5OUMzMzMuODY2IDQ5LjA1MjQgMzM0LjExOSA1MC4xNTEgMzM0LjExOSA1MC4xNTFMMzM0Ljc5NSA1MS41MDE0QzMzNC43OTUgNTEuNTAxNCAzMzQuNjI2IDUyLjAwNjkgMzM0Ljc5NSA1Mi4yNjAzQzMzNC45NjQgNTIuNTEzNiAzMzUuMjE3IDUzLjAyMDYgMzM1LjIxNyA1My4wMjA2QzMzNS4yMTcgNTMuMDIwNiAzMzQuNjI2IDUzLjUyNjUgMzM1LjIxNyA1NC4xMTg3QzMzNS44MDggNTQuNzEwMyAzMzUuNDcgNTQuMTE4NyAzMzUuODA4IDU0LjcxMDNDMzM2LjE0NiA1NS4zMDE5IDMzNi4zOTkgNTUuODkyOCAzMzYuMzk5IDU1Ljg5MjhMMzM3LjQ5OSA1Ny4xNTg5TDMzOC4yMTYgNTcuNjk4MUMzMjYuMzY5IDU0LjU1MjIgMzE3LjUyMSA0My45Njk5IDMxNi45OTUgMzEuMjc1MkwzMTYuOTk3IDMxLjI3NTlaTTM0NS41MzcgNTguNjQ4NkMzNDMuMzI0IDU4LjY0ODYgMzQxLjE2OSA1OC4zOTY3IDMzOS4wOTcgNTcuOTE3MkgzMzkuMjdMMzM4LjQyNiA1Ni4yMjg1QzMzOC40MjYgNTYuMjI4NSAzMzguNTk1IDU1LjcyMjIgMzM4LjM0MiA1NS40NjkxTDMzOC4wODggNTUuMjE1OEwzMzcuODM1IDU0Ljc5MjhWNTQuMjAyNkMzMzcuODM1IDU0LjIwMjYgMzM4LjE3MyA1My43Nzk5IDMzNy44MzUgNTMuNjExMkMzMzcuNDk3IDUzLjQ0MTkgMzM3LjQ5NyA1My45NDkgMzM3LjQ5NyA1My40NDE5VjUyLjkzNDlDMzM3LjQ5NyA1Mi45MzQ5IDMzNy45MTkgNTIuNTk4MSAzMzguMDg4IDUyLjM0NDdDMzM4LjI1NyA1Mi4wOTE2IDMzOC4wMDQgNTIuNjgxNiAzMzguMjU3IDUyLjA5MTZDMzM4LjUxIDUxLjUwMDUgMzM4LjY3OSA1MC43NDA3IDMzOC42NzkgNTAuNzQwN0wzMzkuMjcgNTAuMjM0NFY0OS4xMzY0QzMzOS4yNyA0OS4xMzY0IDMzOS4xODYgNDguODg0IDMzOS4yNyA0OC41NDM4QzMzOS4zNTUgNDguMjA2IDMzOS4yNyA0Ny43IDMzOS4yNyA0Ny43QzMzOS4yNyA0Ny43IDMzOS41MjQgNDcuNTMyMyAzMzkuNzc3IDQ3LjM2MjJDMzQwLjAzMSA0Ny4xOTM1IDM0MC43MDYgNDYuNjAyOCAzNDAuNzA2IDQ2LjYwMjhDMzQwLjcwNiA0Ni42MDI4IDM0MC4yODQgNDYuMzUwNSAzNDAuNzA2IDQ2LjA5NjZDMzQxLjEyOCA0NS44NDM1IDM0MS4zODIgNDUuNTg5NyAzNDEuMjk3IDQ1LjI1MTlDMzQxLjIxMyA0NC45MTQxIDM0MS4zODQgNDUuNzU5OCAzNDEuMjEzIDQ0LjkxNDFDMzQxLjA0NCA0NC4wNjkxIDM0MC45NTkgNDQuMTU0NSAzNDAuOTU5IDQzLjU2MzFDMzQwLjk1OSA0Mi45NzA1IDM0MC42MjIgNDMuNDc3NSAzNDAuOTU5IDQyLjk3MDVDMzQxLjI5NyA0Mi40NjUgMzQxLjgwNCA0MS40OTM0IDM0MS44MDQgNDEuNDkzNEMzNDEuODA0IDQxLjQ5MzQgMzQxLjIxMyA0MC44NjE3IDM0MC45NTkgNDAuNzc2QzM0MC43MDYgNDAuNjkyMSAzNDAuNDUzIDQwLjUyMjQgMzQwLjAzMSA0MC4zNTIzQzMzOS42MDggNDAuMTg0NyAzMzguNDI4IDM5Ljc2MjIgMzM4LjQyOCAzOS43NjIyQzMzOC40MjggMzkuNzYyMiAzMzcuODM3IDM5LjUwODggMzM3LjU4NCAzOS40MjQ0QzMzNy4zMzEgMzkuMzM5NyAzMzYuNDg2IDM4LjE1NjkgMzM2LjQ4NiAzOC4xNTY5QzMzNi40ODYgMzguMTU2OSAzMzYuNDAyIDM4LjE1NjkgMzM1LjY0MiAzNy45MDM4QzMzNC44ODEgMzcuNjUwNCAzMzQuNzEzIDM3LjU2NTcgMzM0LjQ1OSAzNy4zMTM2QzMzNC4yMDYgMzcuMDYwMiAzMzMuNTMgMzYuNDY4NiAzMzMuNTMgMzYuNDY4NkwzMzMuMzYxIDM2LjA0NzFDMzMzLjM2MSAzNi4wNDcxIDMzMy4xMDggMzYuMjk5NSAzMzIuMzQ4IDM2LjIxNTdDMzMxLjU4OCAzNi4xMzEzIDMzMC45MTIgMzUuNTM5NyAzMzAuOTEyIDM1LjUzOTdDMzMwLjkxMiAzNS41Mzk3IDMzMC40OSAzNS41Mzk3IDMzMC4xNTIgMzUuNzA4M0MzMjkuODE0IDM1Ljg3NyAzMjkuMjIzIDM2LjI5OTkgMzI5LjIyMyAzNi4yOTk5TDMyOC42MzIgMzYuNDY4NkwzMjcuNTM0IDM2LjM4NDZMMzI2Ljc3NCAzNS45NjMxTDMyNi4zNTIgMzUuMDMzMkMzMjYuMzUyIDM1LjAzMzIgMzI2LjI2OCAzNC42MTE3IDMyNi4wMTQgMzQuNDQxNkMzMjUuNzYzIDM0LjI3MzkgMzI1LjA4OCAzMy43NjY5IDMyNS4wODggMzMuNzY2OUwzMjUuNDI1IDMyLjc1MzNDMzI1LjQyNSAzMi43NTMzIDMyNS4wODggMzIuMzMwOCAzMjQuNzUgMzIuNTAwOUMzMjQuNDEyIDMyLjY2ODYgMzIzLjkwNSAzMy4yNTk3IDMyMy45MDUgMzMuMjU5N0MzMjMuOTA1IDMzLjI1OTcgMzIzLjY1MiAzMy40Mjg2IDMyMy4zOTkgMzMuMzQ0NEMzMjMuMTQ1IDMzLjI1OTcgMzIyLjcyMyAzMy4wOTExIDMyMi4zMDEgMzIuNjY4OEMzMjEuODc5IDMyLjI0NzMgMzIxLjc5NCAzMS44MjQ4IDMyMS43OTQgMzEuNTcxNUMzMjEuNzk0IDMxLjMxODQgMzIyLjMwMSAzMC4yMjA1IDMyMi4zMDEgMzAuMjIwNUwzMjMuNzM2IDI5LjIwNjZIMzI0LjU4MUwzMjUuNTEgMjguNzg0MUwzMjYuNDM2IDI5Ljk2NzRMMzI3LjE5NyAzMC44OTU0QzMyNy4xOTcgMzAuODk1NCAzMjguMTI1IDMwLjMwNDIgMzI3LjkxNiAzMC4wNTE5QzMyNy43MDMgMjkuNzk3MyAzMjcuMzY1IDI5LjI5MTEgMzI3LjM2NSAyOS4yOTExQzMyNy4zNjUgMjkuMjkxMSAzMjcuNzg4IDI4LjYxNTUgMzI3LjkxNiAyOC4zNjI2QzMyOC4wNDMgMjguMTA5NSAzMjguMjEgMjguMDI1OCAzMjguNTQ4IDI3LjUxOTNDMzI4Ljg4NiAyNy4wMTIxIDMyOS4wNTQgMjYuNzU5IDMyOS4yMjMgMjYuNTA1N0MzMjkuMzkyIDI2LjI1MTggMzMwLjA2OCAyNS4wNzAzIDMzMC4wNjggMjUuMDcwM0wzMzAuNzQzIDI0LjU2MjFMMzMxLjMzNSAyMy44MDI4TDMzMS43NTcgMjMuMzgxNUgzMzIuNDMyTDMzMy42MTUgMjIuNzg5OUgzMzQuMzc1TDMzMy42OTkgMjEuOTQ2M0wzMzMuMjc3IDIxLjQzODRDMzMzLjY5OSAyMS4wMTU1IDMzNC44NzkgMjAuNzYzNiAzMzQuODc5IDIwLjc2MzZDMzM0Ljg3OSAyMC43NjM2IDMzNi4wNjEgMjAuMDg3NSAzMzUuOTc5IDIwLjM0MDhDMzM1Ljg5NSAyMC41OTM5IDMzNC45NjQgMjEuNzc3MiAzMzQuOTY0IDIxLjc3NzJMMzM1LjYzOSAyMi4yODM0QzMzNS42MzkgMjIuMjgzNCAzMzYuMzk5IDIyLjQ1MjEgMzM2LjU2OCAyMi4xOTkyQzMzNi43MzcgMjEuOTQ1OSAzMzYuODIxIDIxLjM1NDIgMzM2LjgyMSAyMS4zNTQyTDMzNi41NjggMjAuMjg0NlYxOS4wNzMxQzMzNi41NjggMTguNjUxNiAzMzYuMzk5IDE3LjU1NDUgMzM2LjE0NiAxNy43MjI2QzMzNS44OTUgMTcuODkxOCAzMzUuNjM5IDE2Ljk2MzggMzM1LjYzOSAxNi45NjM4VjE1Ljc4MDVMMzM0LjcxIDE2LjYyNDVDMzM0LjcxIDE2LjYyNDUgMzM0LjAzNSAxNi41Mzk5IDMzNC4xMTkgMTYuMjg2NUMzMzQuMjAzIDE2LjAzMzQgMzM0LjYyNiAxNS43Nzk2IDMzNC42MjYgMTUuNzc5NkwzMzMuNjk3IDE1LjAxODhDMzMzLjY5NyAxNS4wMTg4IDMzMi42ODMgMTQuMzQ0MiAzMzIuNTE0IDE0LjU5NjVDMzMyLjM0NiAxNC44NDk2IDMzMi4wOTIgMTUuNTI1IDMzMi4wOTIgMTUuNTI1TDMzMS42NyAxNi40NTQ0VjE3LjA0NjFMMzMxLjMzMiAxNy44ODk4TDMzMC4zMTkgMTguOTAzNUwzMjkuODEyIDE5LjkxNTlDMzI5LjgxMiAxOS45MTU5IDMyOS42NDMgMTguNjUwMSAzMjkuNjQzIDE4LjM5NzNDMzI5LjY0MyAxOC4xNDQyIDMyOC41NDUgMTcuMTMxNSAzMjguNTQ1IDE3LjEzMTVMMzI4LjI5MiAxNi4xMTc2QzMyOC4yOTIgMTYuMTE3NiAzMjguNjMgMTUuNDQxOCAzMjguNjMgMTUuMTg4OUMzMjguNjMgMTQuOTM2NyAzMjkuMDUyIDE0LjQyOTYgMzI5LjM5IDE0LjA5MThDMzI5LjcyOCAxMy43NTQgMzMwLjU3MiAxMy4wNzc5IDMzMC44MjUgMTIuOTA5OUMzMzEuMDc5IDEyLjc0MTMgMzMxLjY3IDEyLjQwMyAzMzEuNjcgMTIuNDAzTDMzMS41MDEgMTMuODM4MkwzMzIuNTk5IDEzLjY2OTNMMzMyLjQzIDEyLjkwOTlMMzMzLjM1OSAxMi40MDNMMzMzLjg2NiAxMS4wNTExQzMzMy44NjYgMTEuMDUxMSAzMzQuMzcyIDkuODY5MjcgMzM0LjYyNiAxMC4wMzcyQzMzNC44NzcgMTAuMjA2MyAzMzUuNDY4IDEwLjk2NzEgMzM1LjQ2OCAxMC45NjcxTDMzNC41MzkgMTIuODIzNkgzMzMuNzgxTDMzMy41MjggMTMuNTgzOUMzMzMuNTI4IDEzLjU4MzkgMzMzLjk1IDEzLjY2ODUgMzM0LjI4OCAxMy45MjE3QzMzNC42MjYgMTQuMTc1IDMzNS4yMTcgMTQuODQ5NiAzMzUuMjE3IDE0Ljg0OTZMMzM2LjIzIDE0LjA5MDhWMTMuNDE1MkgzMzYuOTg4TDMzNy40OTcgMTIuMzE3MUwzMzcuMzI2IDExLjU1NjhDMzM3LjMyNiAxMS41NTY4IDMzNy4zMjYgMTEuMzAzNSAzMzcuNDEzIDEwLjk2NjZMMzM3LjQ5NyAxMC42MjgzTDMzNy4xNTkgMTAuMDIxOFY4LjUxNzU4TDMzNi42NSA3LjU5MDQ5SDMzNS4wNDhMMzMyLjQzIDYuMzIyN0gzMzEuNzU0TDMzMC41OTEgNS43NDA5MUMzMzIuNTk5IDQuNTA0OTUgMzM0Ljc3IDMuNTExOTQgMzM3LjA2NSAyLjc5NzU0QzMzNi44IDIuOTg0OTIgMzM2LjY1MyAzLjE1MzYzIDMzNi42NTMgMy4yOTQ3M0MzMzYuNjUzIDMuODkxOTIgMzM2LjgzMyA0LjY4NTM5IDMzNy4wNTMgNS4wNTU0OUMzMzcuMjczIDUuNDI3IDMzNy42NjQgNS43Njk5OSAzMzcuOTE5IDUuODE1NzhMMzM4LjI1NyA1LjczMDI1QzMzOC41OTUgNS42NDcwOCAzMzkuMjcgNC44MDIyNCAzMzkuNDM3IDQuNTQ5OUMzMzkuNjA4IDQuMjk2NjMgMzQwLjc5MSAzLjYyMTQxIDM0MS4xMjggMy40NTE3NkwzNDEuMjggMy4zNzUxM0MzNDEuNDkzIDMuMzc1MTMgMzQxLjcwNSAzLjM2NTM0IDM0MS43NTEgMy4zNTQ1N0wzNDEuODA0IDMuMzY4MTNMMzQxLjk5IDMuNDEyNTNDMzQxLjgxMSAzLjM5MzM3IDM0MS41MjkgMy42MzQ0OSAzNDEuMzYgMy45NTI3TDM0MC43OTEgNC4zNzk4TDM0MC4xMTUgNC44ODY4MUMzMzkuOTI3IDUuMzcxODQgMzM5LjkyNyA2LjA1NTQ4IDM0MC4xMTUgNi40MDY0TDM0MC42MTkgNy4yNTEyN0MzNDAuNjY1IDcuNDgzOTYgMzQwLjcwNCA3Ljc0OTg2IDM0MC43MDQgNy44NDM3N1Y4LjA5NzA0QzM0MC43MDQgOC4zNTAzIDM0MC42MTkgOS4xMDk2NSAzNDAuNjE5IDkuMzYyOUMzNDAuNjE5IDkuNjE2MTYgMzQwLjExMyAxMC45NjgxIDM0MC4xMTMgMTEuMjIwN0MzNDAuMTEzIDExLjQ3NDEgMzM5Ljk2NSAxMi4xNTcxIDMzOS43ODIgMTIuOTkzN0wzMzkuMjczIDEzLjMzMTVDMzM4Ljc2MSAxMy42NjkzIDMzOS4xOTEgMTMuOTIyNiAzMzkuMjczIDE0LjM0NTFDMzM5LjM1MyAxNC43NjY2IDMzOC42ODQgMTQuNjgyOSAzMzkuMjczIDE1LjE4ODlDMzM5Ljg1OSAxNS42OTYxIDMzOS42MDYgMTUuMTg4OSAzMzkuODU5IDE1LjY5NjFDMzQwLjExMyAxNi4yMDMgMzM5Ljk0NCAxNS44NjUyIDM0MC40NSAxNS42OTYxTDM0MC45MjYgMTUuNTM4QzM0MS42OTEgMTQuNTkzNiAzNDIuMjk5IDEzLjgzNzkgMzQyLjI4MiAxMy44NDc4QzM0Mi4yOTQgMTMuODM5NCAzNDIuMzAzIDEzLjgyOTUgMzQyLjMyIDEzLjgxNkMzNDIuMzI1IDEzLjgxMTkgMzQyLjMzIDEzLjgwOSAzNDIuMzMyIDEzLjgwNTRDMzQyLjMzNSAxMy44MDI5IDM0Mi40MTcgMTMuNzQxNyAzNDIuNTI1IDEzLjY1ODdMMzQyLjczMSAxMy40OTk3QzM0My44MjggMTIuNjU2MSAzNDMuMTUzIDEzLjA3NzIgMzQzLjgyOCAxMi42NTYxQzM0NC41MDQgMTIuMjMzOSAzNDMuNjU5IDEyLjQ4NzUgMzQ0LjUwNCAxMi4yMzM5TDM0NS4zNDggMTEuOThDMzQ1LjkwNiAxMS43MDA2IDM0Ni42NjYgMTEuMDE3NSAzNDcuMDM3IDEwLjQ1OTRMMzQ3LjEyMiAxMC4yMDcxQzM0Ny4yMDYgOS45NTM5NiAzNDcuMzczIDkuOTUzOTYgMzQ3LjEyMiA5LjYxNjE2QzM0Ni44NjkgOS4yNzgyNCAzNDYuNTMxIDEwLjEyMzEgMzQ2Ljg2OSA5LjI3ODI0QzM0Ny4yMDYgOC40MzQ3NyAzNDcuMDUyIDguNDM0NzcgMzQ3LjI1NSA4LjA5NjkzQzM0Ny40NiA3Ljc1OTA4IDM0Ni44ODMgOC4yNjQ2NyAzNDcuMjU1IDcuMzM2MThDMzQ3LjYyOSA2LjQwNzY4IDM0Ny42MjkgNi40MDc2OCAzNDcuNjI5IDYuNDA3NjhDMzQ3Ljc2OSA2LjE3NjM5IDM0Ny42NTMgNS44MzQzMiAzNDcuMzc1IDUuNjQ4MzNMMzQ3Ljg4MiA1LjMxMDUxQzM0OC4zODkgNC45NzI2NiAzNDguNTIxIDQuNzgyNDUgMzQ4LjY4NSA0LjU1MTYyQzM0OC44NDcgNC4zMTg5MiAzNDguNzg5IDMuOTM5MDIgMzQ4LjU1OCAzLjcwNzdMMzQ4Ljk4IDMuNDU0NDRDMzQ5LjQwMiAzLjIwMTE2IDM0OS4zMTggMy42MzQ4IDM0OS41NzEgMi45NTM5N0MzNDkuODIyIDIuMjcxMjcgMzQ5LjU3MSAyLjg2Mzc3IDM0OS44MjIgMi4yNzEyN0MzNDkuOTA2IDIuMDc4NzUgMzQ5Ljk2MiAxLjk0ODM4IDM0OS45OTggMS44NjA5OUMzNTQuMTI2IDIuNTEyMzkgMzU3Ljk2MyA0LjA0OTc3IDM2MS4zMDcgNi4yNzEyMUMzNjEuMjAzIDYuNDE0MiAzNjEuMDQ3IDYuNTg4NDggMzYwLjgxNyA2Ljc0NzM3QzM2MC4zMjcgNy4wODUyMSAzNjAuOTY5IDcuNzYxMzkgMzYwLjgxNyA4LjA5OTI3QzM2MC42NjUgOC40MzcxMSAzNjAuODE3IDguOTQyNyAzNjAuODE3IDguOTQyN0MzNjAuODE3IDguOTQyNyAzNjEuOTgzIDkuODcxMiAzNjIuMzY2IDEwLjAzOTlDMzYyLjU0NSAxMC4xMTg1IDM2Mi43ODYgMTAuNDAxMSAzNjMuMDQ0IDEwLjczMDJDMzYzLjAxMyAxMC43NzQxIDM2Mi45OTYgMTAuNzk5NyAzNjIuOTk2IDEwLjc5OTdDMzYyLjk5NiAxMC43OTk3IDM2Mi45MTkgMTAuODg0NCAzNjIuMzY2IDExLjEzNzVDMzYxLjgxMSAxMS4zOTA4IDM2MC44MTcgMTEuODk2OCAzNjAuODE3IDExLjg5NjhDMzYwLjgxNyAxMS44OTY4IDM1OS43ODcgMTIuMjM1MyAzNTkuNzAzIDExLjg5NjhDMzU5LjYxOCAxMS41NTkgMzU4Ljg1OCAxMS4zOTA4IDM1OC44NTggMTEuMzkwOEMzNTguODU4IDExLjM5MDggMzU4LjUyIDExLjA1MyAzNTguMSAxMC44ODM5QzM1Ny42NzYgMTAuNzE0NyAzNTcuMTY5IDEwLjI5MjIgMzU3LjE2OSAxMC4yOTIyQzM1Ny4xNjkgMTAuMjkyMiAzNTYuNDExIDEwLjAzODkgMzU2LjA3MSAxMC4zNzY3QzM1NS43MzMgMTAuNzE0NyAzNTQuNzIyIDEwLjk2OTMgMzU0LjU1NCAxMS41NTk1QzM1NC4zODUgMTIuMTUwNiAzNTQuMTMxIDEyLjc0MjcgMzU0LjA0NyAxMy4wNzkxQzM1My45NiAxMy40MTY5IDM1Mi45NDkgMTQuNjgzMiAzNTIuNjExIDE1LjAyMDJDMzUyLjI3MyAxNS4zNTggMzUxLjg1MSAxNi4wMzQ0IDM1Mi4xMDQgMTYuMzcyMkMzNTIuMzU4IDE2LjcxIDM1My4wMzMgMTcuNTU0OSAzNTMuMjg3IDE3LjM4NkwzNTMuNTQgMTcuMjE2OUwzNTQuNzIyIDE4LjA2MDlDMzU0LjcyMiAxOC4wNjA5IDM1NS42OTUgMTUuOTc4NiAzNTUuNjMyIDE1Ljk2NDZDMzU1LjU2NyAxNS45NDk3IDM1NS4yNTEgMTQuNzY2NiAzNTUuNjYxIDE0LjUxNDNDMzU2LjA3NCAxNC4yNjA5IDM1Ni4zMjcgMTIuOTkzNyAzNTYuNTggMTMuMjQ3QzM1Ni44MzQgMTMuNTAwMSAzNTYuMjQzIDE1LjM1NzggMzU2LjI0MyAxNS4zNTc4TDM1Ny42NzggMTUuOTY0NEMzNTcuNjc4IDE1Ljk2NDQgMzU4LjY4OSAxNS40NzEyIDM1OC4yNjkgMTUuOTY0NEMzNTcuODQ3IDE2LjQ1NTkgMzU3LjA4NyAxNi45NjMzIDM1Ny4wMDMgMTcuMjE2MkMzNTYuOTE4IDE3LjQ2OTUgMzU1LjYzMiAxOC45MDQ5IDM1NS42MzIgMTguOTA0OUgzNTQuNTU2QzM1NC41NTYgMTguOTA0OSAzNTMuNjI1IDE4LjU2NzEgMzUzLjAzMyAxOC45MDQ5QzM1Mi40NDIgMTkuMjQyNyAzNTEuMjYgMjAuNDI0NiAzNTEuMjYgMjAuNDI0NlYyMS42MDcxQzM1MS4yNiAyMS42MDcxIDM1MC40MTUgMjEuMTAwMiAzNTAuMjQ3IDIxLjYwNzFDMzUwLjA3OCAyMi4xMTQzIDM1MC4yNDcgMjIuNzQ0IDM1MC4yNDcgMjIuNzQ0TDM1MC41ODQgMjMuNDY0M0MzNTAuNTg0IDIzLjQ2NDMgMzUwLjQyIDIzLjc4MjggMzQ5Ljc4NiAyMy44NzY5QzM0OS4xNTEgMjMuOTcxMiAzNDguOTggMjMuMzY5IDM0OC44MTMgMjMuODgxOUMzNDguNjQyIDI0LjM5NDIgMzQ4LjgxMyAyNS4xNTQgMzQ4LjgxMyAyNS4xNTRMMzQ4LjczNiAyNi4xMTk5QzM0OC43MzYgMjYuMTE5OSAzNDkuMTUxIDI0LjgwNjggMzQ5LjA2NyAyNi4xMTk5QzM0OC45OCAyNy40MzI5IDM0OS42NTggMjYuMzM1NiAzNDguOTggMjcuNDMyOUMzNDguMzA3IDI4LjUzMDEgMzQ4Ljk4IDI3LjY4NjMgMzQ4LjMwNyAyOC41MzAxQzM0Ny42MzEgMjkuMzc0MSAzNDcuNjMxIDI5LjcxOTggMzQ3LjEyNCAzMC40MzMzQzM0Ni42MTUgMzEuMTQ5MiAzNDYuNDU4IDMxLjkwODUgMzQ2LjE1OSAzMi4xMTg5QzM0NS44NTggMzIuMzMxIDM0Ni4yMDUgMzIuNTAwMiAzNDYuMTU5IDMyLjgzNzVDMzQ2LjExMSAzMy4xNzUzIDM0Ni4xNTkgMzQuMTg4IDM0Ni4xNTkgMzQuMTg4QzM0Ni4xNTkgMzQuMTg4IDM0Ni43ODcgMzUuNDU1MiAzNDYuOTU1IDM1LjcwODZDMzQ3LjEyNCAzNS45NjMxIDM0Ny4yMDkgMzYuMjE2NSAzNDcuNTQ3IDM2LjYzOEMzNDcuODg0IDM3LjA2MDUgMzQ3Ljg4NCAzNy4wNjA1IDM0Ny44ODQgMzcuMDYwNUMzNDcuODg0IDM3LjA2MDUgMzQ4LjY0NCAzNi44MDcxIDM0OC44OTggMzcuMDYwNUMzNDkuMTUxIDM3LjMxMzYgMzQ5LjE1MSAzNy4zMTM2IDM0OS4xNTEgMzcuMzEzNkgzNTAuMzMzQzM1MC41ODcgMzcuMzEzNiAzNTAuNzU2IDM3LjQ4MjMgMzUxLjAwOSAzNy4zMTM2QzM1MS4yNiAzNy4xNDM1IDM1MS45MzYgMzYuODkxMyAzNTEuOTM2IDM2Ljg5MTNMMzUyLjk1MSAzNy4zODY5TDM1My43OTMgMzcuNzM1MUMzNTQuMDQ3IDM4LjQwOTUgMzUzLjYyNSAzOS4yNTM4IDM1My44NzggMzkuNTkxOEMzNTQuMTMxIDM5LjkyOTYgMzU0LjcyMiA0MC43NzQ4IDM1NC45NzggNDAuNzc0OEMzNTUuMjI5IDQwLjc3NDggMzU1LjYzMiA0MS4xMTI5IDM1NS42MzIgNDEuMTEyOVY0Mi43MTUzTDM1NS4yMzIgNDMuNjQzN0wzNTUuMTQ3IDQ0LjE1MjFDMzU1LjE0NyA0NC4xNTIxIDM1NC45NzggNDQuOTk1NCAzNTUuMTQ3IDQ1LjUwMzFDMzU1LjMxNCA0Ni4wMDkgMzU1LjQwOCA0Ny4xOTEzIDM1NS43IDQ3LjQ0MzdDMzU1Ljk4OSA0Ny42OTY4IDM1Ni4xNTggNDguNTQxOCAzNTYuMTU4IDQ4LjU0MThMMzU2LjgzNCA0OS45NzgyQzM1Ni44MzQgNDkuOTc4MiAzNTguMzU0IDQ5LjQ3MTMgMzU4Ljg2IDQ5LjMwMjZDMzU5LjM2NyA0OS4xMzM5IDM1OS43ODkgNDguNzEgMzYwLjEyNyA0Ny44NjZDMzYwLjQ2NSA0Ny4wMjI3IDM2MC40OTkgNDYuMDk0MiAzNjAuODIgNDUuODQwOUMzNjEuMTQxIDQ1LjU4NzUgMzYxLjU2MyA0NS4xNjQ1IDM2MS45MDEgNDQuNzQyM0MzNjIuMjM4IDQ0LjMxOTggMzYyLjk5NiA0My4zMDcxIDM2My4wODEgNDIuOTY3OUMzNjMuMTY3IDQyLjYzMSAzNjIuOTE0IDQwLjUxOTggMzYyLjkxNCA0MC41MTk4QzM2Mi45MTQgNDAuNTE5OCAzNjIuNzQ1IDM5LjkyODYgMzYzLjA4MSAzOS41OTEzQzM2My40MjEgMzkuMjUzNSAzNjQuNTE2IDM4LjA3MTcgMzY0LjY4NSAzNy43MzQ2QzM2NC44NTQgMzcuMzk2NCAzNjUuOTU0IDM2LjA0NjEgMzY2LjAzNiAzNS43OTIzQzM2Ni4xMjEgMzUuNTM4OSAzNjYuMjkgMzQuMzU1OSAzNjYuMDM2IDM0LjUyNDZDMzY1Ljc4MyAzNC42OTUyIDM2NC43NyAzNS4yMDA2IDM2NC43NyAzNS4yMDA2QzM2NC43NyAzNS4yMDA2IDM2NC4wMSAzNC4xMDIxIDM2NC4zNDcgMzQuMTg2NUMzNjQuNjg1IDM0LjI3MjIgMzY2LjAzNiAzMy45OTEzIDM2Ni43OTYgMzMuNDU2MkMzNjcuNTU2IDMyLjkyMTIgMzY4LjU3IDMxLjczODkgMzY4LjU3IDMxLjczODlWMzAuNDMyNkMzNjguNTcgMzAuNDMyNiAzNjguMTQ4IDMwLjEzNDQgMzY3Ljg5NCAzMC4wNTAyQzM2Ny42NDEgMjkuOTY1NyAzNjYuODgxIDI5Ljg4MSAzNjYuODgxIDI5Ljg4MUwzNjYuMjA1IDI5LjI4OTZDMzY2LjIwNSAyOS4yODk2IDM2NC41MTYgMjguMTkyMyAzNjUuMTA3IDI4LjI3NkMzNjUuNjk5IDI4LjM2IDM2Ny45NzkgMjkuMjg5NiAzNjcuOTc5IDI5LjI4OTZDMzY3Ljk3OSAyOS4yODk2IDM2OS40MTQgMjkuMzczNiAzNjkuNjY4IDI5LjI4OTZDMzY5LjkyMSAyOS4yMDQ5IDM3MS4zNTcgMzAuMjI1NiAzNzEuNjEgMzAuNDMyNkMzNzEuODYzIDMwLjY0MTMgMzcyLjUzNyAzMS42NTQgMzcyLjg3NCAzMi4xMThDMzczLjIxMiAzMi41ODM0IDM3My44OSAzMy40NTU5IDM3My44OSAzMy40NTU5QzM3My44OSAzMy40NTU5IDM3My44OTMgMzMuNDczOCAzNzMuOSAzMy41MDQ0QzM3Mi4yMDEgNDcuNjUxNSAzNjAuMTMgNTguNjQ4NiAzNDUuNTM3IDU4LjY0ODZaIgogIGZpbGw9IiMwMDNENzEiCi8+Cjwvc3ZnPg==%0A"
            alt="Portfolioone"
            style="box-sizing: border-box; margin-bottom: 20px"
          />

          <div
            class="greet"
            style="
              box-sizing: border-box;
              letter-spacing: 0;

              text-align: center;
              width: 60%;
              margin: auto;
            "
            width="60%"
          >
            <p style="margin: 0; padding: 0">
              Hi <span style="font-weight: bold">{existing_email['fullname']}</span>,
            </p>
            <p style="margin: 0; padding: 0">
              You recently requested to reset your password for PorfolioOne
              account. Please click below button to proceed :
            </p>
          </div>
        </div>
      </header>

      <section
        class="main-content"
        style="
          background-color: white;
          border-radius: 6px;
          padding: 63px, 267px, 146px, 266px;
          text-align: center;
          max-width: 80%;
          min-height: 350px;
          margin: auto;
        "
      >
        <div style="display: inline-block; margin: auto">
          <div
            class="content"
            style="
              margin: 20px;
              padding: 10px;
              border-bottom: 1px solid #e5e5e5;
              max-width: 579px;
            "
          >
            <a
              class="button"
              href="https://www.portfolioone.io/reset_password?token={token}"
              style="
                background-color: #3490ec;
                border-radius: 60px;
                color: white;
                margin: auto;
                padding: 20px 100px;
                display: block;
                width: 30%;
                margin-top: 40px;
                margin-bottom: 40px;
                text-decoration: none;
                text-transform: uppercase;
              "
              >reset password</a
            >
            <p>
              This button link will expire in 10 minutes. If this request
              wasn't initiated by you, please disregard this email.
            </p>
          </div>
          <p
            style="
              margin: 0;
              padding: 0;
              max-width: 579px;
              padding-bottom: 50px;
            "
          >
            You can now access PortfolioOne online or on any device by going to
            <a href="https://portfolioone.io">https://portfolioone.io</a>
          </p>
        </div>
      </section>

      <!-- <section
        class="app-advt"
        style="
          background-color: white;
          border-radius: 6px;
          margin: auto;
          margin-top: 40px;
          text-align: center;
          max-width: 80%;
        "
      >
        <h2>Get the PortfolioOne app!</h2>
        <p style="margin: 0; padding: 0; max-width: 669px; margin: auto">
          Get the most out of PortfolioOne by installing our mobile app. You can
          log in using your existing email address and password.
        </p>
        <img
          style="margin-top: 40px"
          src="data:image/svg+xml;base64,ICAgICAgICA8c3ZnCndpZHRoPSIyNzkiCmhlaWdodD0iMTAwIgp2aWV3Qm94PSIwIDAgMjc5IDEwMCIKZmlsbD0ibm9uZSIKeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgp4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayIKPgo8cmVjdAogIHg9IjAuODE5NjcyIgogIHk9IjAuODE5NjcyIgogIHdpZHRoPSIyNzcuMzYxIgogIGhlaWdodD0iOTguMzYwNyIKICByeD0iNDkuMTgwMyIKICBmaWxsPSJibGFjayIKLz4KPHJlY3QKICB4PSIwLjgxOTY3MiIKICB5PSIwLjgxOTY3MiIKICB3aWR0aD0iMjc3LjM2MSIKICBoZWlnaHQ9Ijk4LjM2MDciCiAgcng9IjQ5LjE4MDMiCiAgc3Ryb2tlPSIjMDAwMDFFIgogIHN0cm9rZS13aWR0aD0iMS42MzkzNCIKLz4KPHJlY3QgeD0iMjIuNSIgeT0iMTMiIHdpZHRoPSIyMzQiIGhlaWdodD0iNzQiIGZpbGw9InVybCgjcGF0dGVybjApIiAvPgo8ZGVmcz4KICA8cGF0dGVybgogICAgaWQ9InBhdHRlcm4wIgogICAgcGF0dGVybkNvbnRlbnRVbml0cz0ib2JqZWN0Qm91bmRpbmdCb3giCiAgICB3aWR0aD0iMSIKICAgIGhlaWdodD0iMSIKICA+CiAgICA8dXNlCiAgICAgIHhsaW5rOmhyZWY9IiNpbWFnZTBfMTcxN180MCIKICAgICAgdHJhbnNmb3JtPSJtYXRyaXgoMC4wMDIxMjI0MSAwIDAgMC4wMDY3MTE0MSAtMC4wMDUxMzM5NCAwKSIKICAgIC8+CiAgPC9wYXR0ZXJuPgogIDxpbWFnZQogICAgaWQ9ImltYWdlMF8xNzE3XzQwIgogICAgd2lkdGg9IjQ3NiIKICAgIGhlaWdodD0iMTQ5IgogICAgeGxpbms6aHJlZj0iZGF0YTppbWFnZS9wbmc7YmFzZTY0LGlWQk9SdzBLR2dvQUFBQU5TVWhFVWdBQUFkd0FBQUNWQ0FZQUFBRHlnMHZsQUFBTVBXbERRMUJKUTBNZ1VISnZabWxzWlFBQVNJbVZWd2RZVThrV25sdVNrSkNFRWdoRlN1aE5FSkdPbEJCYXBFb1ZiSVFrUUNnaEJvS0t2U3dxdUhZUkFVWFJWUkVGMXdMSVdoRzdpMkR2Q3lvcXlycFlzSmMzS2FEcnZ2SzkrYjY1ODk5L3p2em56TGx6NzUwQlFPTVlUeUxKUVRVQnlCVVhTR05EQTFuamtsTllwRWVBREppd0dnTTlIajlmd282SmlRQ3dETFovTDIrdUFVVGVYbmFVYS8yei83OFdMWUV3bnc4QUVnTnhtaUNmbnd2eGZnRHdLcjVFV2dBQVVjNWJUQzJReURHc1FFY0tBNFI0c1J4bktIR1ZIS2NwOFI2RlRYd3NCK0kyQU5Tb1BKNDBBd0I2QitSWmhmd01xRUh2aDloWkxCQ0pBZEJnUWV5WG01c25nRGdWWWx0b0k0RllydStaOXAxT3h0ODAwNFkwZWJ5TUlheWNpNktvQllueUpUbTg2ZjluT3Y1M3ljMlJEZnF3aHBXYUtRMkxsYzhaNXUxR2RsNjRIRk1oN2hPblJVVkRyQTN4TzVGQVlROHhTc21VaFNVbzdWRWpmajRINWd3K2FZQTZDM2hCNFJBYlFSd2l6b21LVVBGcDZhSVFMc1J3aGFEVFJBWGNlSWoxSVY0c3pBK09VOWxza3ViRnFueWhqZWxTRGx2Rm4rRkpGWDdsdnU3SnNoUFlLdjJYbVVLdVNoK2pGMlhHSjBGTWdkaXlVSlFZQlRFZFlxZjg3TGh3bGMzb29reE8xS0NOVkJZcmo5OFM0bGloT0RSUXFZOFZwa3REWWxYMkpibjVnL1BGTm1XS3VGRXF2TGNnTXo1TW1SK3NqYzlUeEEvbmduVUl4ZXlFUVIxaC9yaUl3YmtJaEVIQnlybGpUNFRpaERpVnpqdEpRV0NzY2l4T2tlVEVxT3h4YzJGT3FKdzNoOWcxdnpCT05SWlBMSUFMVXFtUHAwc0tZdUtWY2VKRldid3hNY3A0OEJVZ0FuQkFFR0FCR2F4cElBOWtBVkY3WDFNZnZGUDJoQUFla0lJTUlBU09LbVp3UkpLaVJ3eXZjYUFJL0FtUkVPUVBqUXRVOUFwQkllUS9EN0hLcXlOSVYvUVdLa1prZzBjUTU0SndrQVB2WllwUjRpRnZpZUFoWkVULzhNNkRsUS9qellGVjN2L3YrVUgyRzhPR1RJU0trUTE2WkdrTVdoS0RpVUhFTUdJSTBRNDN4UDF3SHp3Q1hnTmdkY0U5Y2EvQmVYeXpKendpZEJMdUU2NFN1Z2czSjR2bVMzK0lNaEowUWYwUVZTN1N2czhGYmcwMTNmQkEzQmVxUTJXY2lSc0NSOXdWK21Iai90Q3pHMlE1cXJqbFdXSDlvUDIzR1h6M05GUjJaR2N5U3RZakI1QnRmeHhKdDZlN0RhbkljLzE5ZnBTeHBnM2xtelBVODZOL3puZlpGOEEyL0VkTGJERzJEenVOSGNmT1lvZXdKc0RDam1MTjJBWHNzQndQcmE2SGl0VTE2QzFXRVU4MjFCSDl3OS9nazVWbk10KzV6cm5YK1pPeXIwQTRUZjZOQnB3OHlYU3BLQ096Z01XR2Z3UWhpeXZtT3cxbnVUaTd1QUFnLzc4b1AxK3ZtSXIvQnNJODk0MmJjZ3dBcnhKSVpuemplQllBSEh3RUFPUE5OODdpSlh4dFZnQnd1SU12a3hZcU9WeCtJY0N2aEFaODB3eUFDYkFBdG5BK0xzQWQrSUFBRUF6R2dHZ1FENUxCSkJoOUpsem5VakFWekFUelFERW9CU3ZBV2xBQnFzRVdzQVBzQm50QkV6Z0Vqb05UNER6b0FGZkJiYmg2ZXNBejBBL2VnSThJZ3BBUUdzSkFEQkJUeEFweFFGd1FUOFFQQ1VZaWtGZ2tHVWxGTWhBeElrTm1JZ3VRVW1RVlVvRnNSbXFSWDVHRHlISGtMTktKM0VTNmtWN2tKZklCeFZBcXFvTWFvOWJvQ05RVFphUGhhRHc2RWMxQXA2QkY2RUowR1ZxTzFxQzcwRWIwT0hvZXZZcDJvYy9RQVF4ZzZoZ1RNOE1jTVUrTWcwVmpLVmc2SnNWbVl5VllHVmFEMVdNdDhEbGZ4cnF3UHV3OVRzUVpPQXQzaENzNERFL0ErZmdVZkRhK0ZLL0FkK0NOZUJ0K0dlL0crL0V2QkJyQmlPQkE4Q1p3Q2VNSUdZU3BoR0pDR1dFYjRRRGhKSHlYZWdodmlFUWlrMmhEOUlEdllqSXhpemlEdUpTNGdkaEFQRWJzSkQ0Z0RwQklKQU9TQThtWEZFM2lrUXBJeGFUMXBGMmtvNlJMcEI3U096VjFOVk0xRjdVUXRSUTFzZHA4dFRLMW5XcEgxQzZwUFZiN1NOWWtXNUc5eWRGa0FYazZlVGw1SzdtRmZKSGNRLzVJMGFMWVVId3A4WlFzeWp4S09hV2VjcEp5aC9KS1hWM2RYTjFMZmF5NlNIMnVlcm42SHZVejZ0M3E3Nm5hVkhzcWh6cUJLcU11bzI2bkhxUGVwTDZpMFdqV3RBQmFDcTJBdG94V1N6dEJ1MGQ3UjJmUW5laGN1b0EraDE1SmI2UmZvai9YSUd0WWFiQTFKbWtVYVpScDdOTzRxTkduU2RhMDF1Um84alJuYTFacUh0Uzhyam1neGRBYXFSV3RsYXUxVkd1bjFsbXRKOW9rYld2dFlHMkI5a0x0TGRvbnRCOHdNSVlGZzhQZ014WXd0akpPTW5wMGlEbzJPbHlkTEoxU25kMDY3VHI5dXRxNnJycUp1dE4wSzNVUDYzWXhNYVkxazh2TVlTNW43bVZlWTM3UU05Wmo2d24xbHVqVjYxM1NlNnMvVEQ5QVg2aGZvdCtnZjFYL2d3SExJTmdnMjJDbFFaUEJYVVBjME41d3JPRlV3NDJHSnczN2h1a004eG5HSDFZeWJPK3dXMGFva2IxUnJORU1veTFHRjR3R2pFMk1RNDBseHV1TlR4ajNtVEJOQWt5eVROYVlIREhwTldXWStwbUtUTmVZSGpWOXl0SmxzVms1ckhKV0c2dmZ6TWdzekV4bXR0bXMzZXlqdVkxNWd2bDg4d2J6dXhZVUMwK0xkSXMxRnEwVy9aYW1scEdXTXkzckxHOVprYTA4clRLdDFsbWR0bnByYldPZFpMM0l1c242aVkyK0RkZW15S2JPNW80dHpkYmZkb3B0amUwVk82S2RwMTIyM1FhN0RudlUzczArMDc3Uy9xSUQ2dUR1SUhMWTROQTVuRERjYTdoNGVNM3c2NDVVUjdaam9XT2RZN2NUMHluQ2FiNVRrOVB6RVpZalVrYXNISEY2eEJkbk4rY2M1NjNPdDBkcWp4d3pjdjdJbHBFdlhleGQrQzZWTGxkRzBVYUZqSm96cW5uVUMxY0hWNkhyUnRjYmJneTNTTGRGYnExdW45MDkzS1h1OWU2OUhwWWVxUjVWSHRjOWRUeGpQSmQ2bnZFaWVBVjZ6ZkU2NVBYZTI5Mjd3SHV2OTE4K2pqN1pQanQ5bm95MkdTMGN2WFgwQTE5elg1N3ZadDh1UDVaZnF0OG12eTUvTTMrZWY0My8vUUNMQUVIQXRvREhiRHQyRm5zWCszbWdjNkEwOEVEZ1c0NDNaeGJuV0JBV0ZCcFVFdFFlckIyY0VGd1JmQy9FUENRanBDNmtQOVF0ZEVib3NUQkNXSGpZeXJEclhHTXVuMXZMN1Ivak1XYldtTFp3YW5oY2VFWDQvUWo3Q0dsRVN5UWFPU1p5ZGVTZEtLc29jVlJUTklqbVJxK092aHRqRXpNbDVyZXh4TEV4WXl2SFBvb2RHVHN6OW5RY0kyNXkzTTY0Ti9HQjhjdmpieWZZSnNnU1doTTFFaWNrMWlhK1RRcEtXcFhVTlc3RXVGbmp6aWNiSm91U20xTklLWWtwMjFJR3hnZVBYenUrWjRMYmhPSUoxeWJhVEp3Mjhld2t3MGs1a3c1UDFwak1tN3d2bFpDYWxMb3o5Uk12bWxmREcwampwbFdsOWZNNS9IWDhaNElBd1JwQnI5Qlh1RXI0T04wM2ZWWDZrd3pmak5VWnZabittV1daZlNLT3FFTDBJaXNzcXpycmJYWjA5dmJzcnpsSk9RMjVhcm1wdVFmRjJ1SnNjVnVlU2Q2MHZFNkpnNlJZMGpYRmU4cmFLZjNTY09tMmZDUi9ZbjV6Z1E3Y3lGK1EyY3Ara25VWCtoVldGcjZibWpoMTN6U3RhZUpwRjZiYlQxOHkvWEZSU05Fdk0vQVovQm10TTgxbXpwdlpQWXM5YS9Oc1pIYmE3Tlk1Rm5NV3p1bVpHenAzeHp6S3ZPeDV2ODkzbnI5cS91c0ZTUXRhRmhvdm5Mdnd3VStoUDlVVjA0dWx4ZGNYK1N5cVhvd3ZGaTF1WHpKcXlmb2xYMG9FSmVkS25VdkxTajh0NVM4OTkvUEluOHQvL3Jvc2ZWbjdjdmZsRzFjUVY0aFhYRnZwdjNMSEtxMVZSYXNlckk1YzNiaUd0YVpremV1MWs5ZWVMWE10cTE1SFdTZGIxMVVlVWQ2ODNuTDlpdldmS2pJcnJsWUdWalpVR1ZVdHFYcTdRYkRoMHNhQWpmWFZ4dFdsMVI4MmlUYmQyQnk2dWJIR3VxWnNDM0ZMNFpaSFd4TzNudjdGODVmYWJZYmJTcmQ5M2k3ZTNyVWpka2RiclVkdDdVNmpuY3ZyMERwWlhlK3VDYnM2ZGdmdGJxNTNyTi9jd0d3bzNRUDJ5UFk4L1RYMTEydDd3L2UyN3ZQY1Y3L2Zhbi9WQWNhQmtrYWtjWHBqZjFObVUxZHpjblBud1RFSFcxdDhXZzc4NXZUYjlrTm1oeW9QNng1ZWZvUnlaT0dScjBlTGpnNGNreHpyTzU1eC9FSHI1TmJiSjhhZHVOSTJ0cTM5WlBqSk02ZENUcDA0elQ1OTlJenZtVU5udmM4ZVBPZDVydW04Ky9uR0MyNFhEdnp1OXZ1QmR2ZjJ4b3NlRjVzN3ZEcGFPa2QzSHJua2YrbjQ1YURMcDY1d3I1eS9HblcxODFyQ3RSdlhKMXp2dWlHNDhlUm16czBYdHdwdmZidzk5dzdoVHNsZHpidGw5NHp1MWZ4aDkwZERsM3ZYNGU2ZzdndjM0KzdmZnNCLzhPeGgvc05QUFFzZjBSNlZQVFo5WFB2RTVjbWgzcERlanFmam4vWThreno3MkZmOHA5YWZWYzl0bisvL0srQ3ZDLzNqK250ZVNGOThmYm4wbGNHcjdhOWRYN2NPeEF6Y2U1UDc1dVBia25jRzczYTg5M3gvK2tQU2g4Y2ZwMzRpZlNyL2JQZTU1VXY0bHp0ZmM3OStsZkNrUE1WV0FJTVZUVThINE9WMkFHakpjTzhBejJlVThjcnpuNklneWpPckFvSC9oSlZuUkVWeEIyQjdBQUFKY3dHSWdIdVVqYkJhUVV5RnJYd0xIeDhBMEZHamh1cmdXVTF4cnBRWElqd0hiTEtYbzR1ajZkWGdoNkk4YzM0WDk0OHRrS3U2Z2gvYmZ3RU5BM20zNWFRdk9RQUFBRGhsV0VsbVRVMEFLZ0FBQUFnQUFZZHBBQVFBQUFBQkFBQUFHZ0FBQUFBQUFxQUNBQVFBQUFBQkFBQUIzS0FEQUFRQUFBQUJBQUFBbFFBQUFBRHpHeHlHQUFCQUFFbEVRVlI0QWUyZENkeDFVNzNIZDZPbTJ5Qmw1blZMaHRRdE1vZlhsRWdoU2Nyd2txRkNwaWhEcGlRaGlreHg2OVdBVW5FUkVyMjRobXVzWk00VWlnWXFwY2l0ZFgvZnBYWHVQdnVzdGM4Kys1enpQT2ZzOC85L1B1czV6OWxuNzdYWCt1MjExMzljLzVWbFJvYUFJV0FJR0FLR2dDRmdDQmdDaG9BaFlBZ1lBb2FBSVdBSUdBS0dnQ0ZnQ0JnQ2hvQWhZQWdZQW9hQUlXQUlHQUtHZ0NGZ0NCZ0Nob0FoWUFnWUFvYUFJV0FJR0FLR2dDRmdDQmdDaG9BaFlBZ1lBb2FBSVRCbUNEeG55TzJsL2hmOXE3eEFuODlUNGZPbC8vclVoNUVoWUFnWUFvYUFJVEF0Q1B4ZGQvMnJ5ak1xLzFCNVdvVmpUNms0bFlIU01CZ3VkYjVNWlg2VkJWUldWVmxDWlRHVmVWUmd0akJoR0srUklXQUlHQUtHZ0NFd0hRakFxMkN1ZjFPQjZmNVc1WmNxZDZqY29QS2d5aU1xVDZyOFU2VnY0b2FEb3VlcUlwanNHMVZXVWxsRFpUbVZWNmdZR1FLR2dDRmdDQmdDNDRMQW45VFFXMVF1VmJsVzVTY3FqNnYweFhnSHhYRFJXRGRRMlZBRmpYWXhGZE5nQllLUklXQUlHQUtHd05naWdLbjVmcFdyVlM1UXVWQUZjM010R2dURGZiUHV2STNLeGlvdzJrSFVxV3FNREFGRHdCQXdCQXlCa1VIZ1ByWGtYSlZUVmU2czB5cUNtT29TMTY2djhobVZUVlh3enhxekZRaEdob0FoWUFnWUFvMUQ0RlhxMGRJcXVFcng2OTZsMGxOZ1ZWMkdTK0RUamlxSHF1Q3pmYUdLa1NGZ0NCZ0Nob0FoMEdRRWNKL09VSG1iQ2xITnQ2cGdkcTVFZFJqdWdxcDVENVVEVlY2clVxY09YV1prQ0JnQ2hvQWhZQWlNSlFKb3V6TlZucTlDUUZVbHYyNnZ6QkpOZG0rVlQ2bVlWaXNRakF3QlE4QVFNQVFtRWdFQ2cxZFJJWEtab0NvMDNsTHFoZUhpbjkxTTVRZ1ZZN2Fsc05xUGhvQWhZQWdZQWhPQUFNdGhWMVFoaU9yMmJ2M3RoZUhDYkk5VUlUakt5QkF3QkF3QlE4QVFNQVNlTlNzdkx5RHVWdmxGR1NCVkdTNlpvZzVSZVV0WlpmYWJJV0FJR0FLR2dDRXdnUWk4UkgxZVJPVW1sZCttK2wrRjRXS24zbDlsQTVXNVVoWFpjVVBBRURBRURBRkRZRUlSZ0pjdXJJSWY5eklWL0xvZDFJM2g0cmZkU0dVWGxmazZycllEaG9BaFlBZ1lBb2FBSVFBQytITmZvL0pMRlh5NkhjUUpaVVRvTThrdEZpczd5WDR6QkF3QlE4QVFNQVFNQWM4cjRabFJCYldNNGFMZExxdXl1Z3IvR3hrQ2hvQWhZQWdZQW9aQUdnRjRKVHh6R1pVT3ZsbkdjTWttdGJMSzYxU01EQUZEd0JBd0JBd0JRNkE3QXZETWxWVFlwcmFOeWhqdVFqcHpOWlZ1ZnQ2MkN1MkxJV0FJR0FLR2dDRXd3UWpBTStHZCtIUGJLTVZ3VVlXeFFaTXYwc2dRTUFRTUFVUEFFREFFcWlQQUVscVdDYldabFZNTWx3VE5aTThnYU1ySUVEQUVEQUZEd0JBd0JLb2pnSFpMMnNlMnBiUXBoa3ZxUm5ZQk1qSUVEQUZEd0JBd0JBeUIzaEZZVXBlOE9IOFpPeDNFQ0s3TXJrQkcwNERBYzUvNzNPekZMMzV4OXM5Ly9qTjc2cW1uTXVkNjJuSnhHbHBzdHpRRURBRkR3QkFvSUxDd3ZwTTRxa1VwaG92VDF4aHVDNmJoLy9PODV6MHZXMnl4eGJLbGxsb3FtekZqUnJid3dndG4vL00vLzVQOTRBYy95SjUrK3VuaE44RHVZQWdZQW9hQUlUQklCSWlEYWdzNlRqRmN1UExMQjNsbnF5dU93RXRmK3RKcytlV1h6OTd4am5ka2IzM3JXN1BYdmU1MTJUenp6Sk85L09Vdno3Nzg1UzluUC9yUmo0emh4cUd6bzEwUVdIenh4Yk1OTnRqQWp5VUV1c3N1dXl6NzcvLys3eTVYamVmUHIzclZxN0lQZk9BRDJhdGYvV3B2RWJyNTVwdDlmLy8rOTcrUFo0ZW11ZFZ2ZWN0YnNvMDIyc2hqK2FjLy9TbTc4TUlMczEvOG9qUXYvelMzZUNSdi93cTFxbTFudlJURHhlNU1NbWFqSVNId25PYzhKMXRtbVdXeVhYZmROVnRycmJXeWVlZWROM3ZaeS81LzJSWm1aTTZoTklrd2w4K1FCdithMTd6R1Q0NThJblE4Ly9uUDkzMWxndno5NzMrZlBmamdnOW45OTkrZi9lNTN2ek9UZXMwQmdQREcrQUxqTUk2YXluQVJVai80d1E5bWIzN3ptejFhMy8vKzk3TXJyN3d5TTRaYmIvREFjUGZhYXk5LzhXOS8rOXZzM252dk5ZYmJPNVR3VUFLUVc1Uml1QnhQL2RhNjJQNnBqOENXVzI2WkhYamdnZDUwUE5kY2JZRnN2dEpubm5rbWUrS0pKekkrbTBSTExMRkVkdW1sbDJab1hEQlpQbUhDZ1NFZ2FORG4vLzNmLy9YTUZyUDZHV2Vja2MyWk02ZEpNRXhKWDhEMWhTOThvZGR3dVdIVFl3RVEzTEFNTVg3KzhZOS9UQW5HVGIwSlkrWGYvdTNmZlBmKytNYy8rbmlTcHZaMWlQM0NVdHpHUjl1KzVHNU1sRTZ6Vkt0YzU2YnJYNWpLYTEvNzJteS8vZmJMUHY3eGo1YzI0NjkvL1d2Mm05Lzh4Z2RObFo0NFpqOHlJUzZ3d0FLdFZoTVl4dVRJSndRRHBvQVZXajlXQUlRVFRGcWYvL3puczUvOTdHZG1ZbStoVi80UG1BWmNPYlBKRExmWXQzeS95MUdhbkY4UjdBbkc1SDM3ODUvL1hOcnhQSjdGY1ZSNm9mMVlpa0NLNFpaZVpELzJqZ0FNNU4vLy9kK3pJNDQ0SXR0NDQ0MjdWdkNYdi93bGUreXh4eG8zU2FLNUJ1TC9uL3prSjlrZGQ5emhKd0F3ZXNVclh1R0ZrZ1VYWE5EN3N2SEp2ZWhGTDhyZSs5NzNacTkvL2V1end3NDdMTHY0NG91N1RoamhIdlpwQ0V3NkFsZzYzdmpHTjNweis4eVpNNzJyaHZnUUxHaEdVNHVBTWR3cHdudUZGVmJJUHZPWnoyUnJyTEdHTjZWMnUrMnZmLzFyLzJKME8yK2NmMy84OGNlelF3NDV4R3V2UWFLRzZlTExYbVNSUmJJM3ZlbE5QbkFEQVFXbWkzL3VzNS85ckpmUUw3amdBdlBQamZQRHQ3WlBHUUlJc2QvOTduZDlRQ2JXbzltelozczN6cFExd0c3VVFzQVliZ3VLNGYyRGRQbUpUM3pDTTF0OGF0MElFdzRCUTNmZmZYZTNVOGY2ZDVoc0tLRWpmTWZjZGR0dHQvbHl6VFhYWkgvNHd4K3lqMzcwby80VUltOTMyR0dIN0thYmJzcCsrY3RmaHN2c2M4SVJRRkF6aWlQd3Q3LzlMWnR2dnZtOHE0WXorSjYzTk1XdnNxUERRTUFZN2pCUXpkVko5T1MyMjI2YnJiLysrajZBSmZkVDhsK0NGQWdXZ3RFMG1hcE1ra1FybjNEQ0NSbFJreXV2ek9aVjJ2dHE5ZFV6VEdObm5YVldWMy91QzE3d0FpL1pFNnpGMGhGODR3Z3ltTEhMMWpmajd5TEtGd0VKSVFEekcwSlFrZWdEenhnVE9JUVF3UFBqbWp4eEhpWnhBbnNnenVIY2NCNmFCNysvNUNVdjhSbzhGbzdnVWtEYnArLzR0SW02L2ZuUGY1N2RlT09OcGUzUDM3dk8vN2cvRUJUcEc4bFhIbjc0NGV5V1cyN0pXQ0pTbFRCbGdzdXl5eTdySjN6NmpqRDEwRU1QWlN6YklmcTFGK0o2Nm1LdE9nRTlqejc2cVBmcDMzNzc3UjJDV3kvMVZqMlgyQVBHSVZIZitFRi85YXRmK1g1VXdRUUxEYytYOGNnekJNOXdIZjFoYVNEakUzekFoajcxRzJITnMyUE1nRnZlcDgzeEpaZGMwbzhmQWhlSkZXRzhwWWl4Rzk1VjNvYzExMXpUdnh0Y3kvdjU0eC8vdUpaNW12aU01WlpiTHB0NzdybDlXKzY4ODg3cyt1dXZ6M0NuVFJvdHJRNC9xY0tzWWFVbUJocVE3djN2ZjcvVEpLOTV0VHJwaFhPYTdCcUp1MTZ3RmhCNjBaM1dpWGJ0cDVpUjIyYWJiWndZWk92YTczem5PMDcrM2VTMW10aWNsbHU1YjMvNzIwNk16V21wa1pNQTQyVEdkcG9vblJLS3VBMDMzTkJwSW96V29RbmR5VmZzSG5ua0VWL09QLzk4SitiUmNlNzg4OC92dnZDRkw3VE8rK1FuUCtsa0V1ODRUd3pNU1N2MzU5MXp6ejFPZ1hOdDUxQ1BsckU0TVJGL3p2dmU5ejZuU2M3dHNzc3V2djIwWFV6ZmFaSjJXaXJsKy9YS1Y3NnlyWTdpdS9yT2Q3N1RQZkRBQXkzTUZCVmZlajdYSy9tS08vcm9veDF0Rk1QM21IRnYyblgxMVZlNzdiZmYzb0ZOOFY3NTd4SldQTGFubjM2NjA5cE4zMTdhSGRvdlJ1c2tVUHBuS21aUVdsZW9WMHpKUHpNeEJvOEJkZEV1NnFkZlltYnVxcXV1Y21Jc1RvektmZVVyWDNGVjZ3NzNTSDBHVENTa09kck9mU21NcWFxWWlMazRMYTN4T041NjY2MU82Kzc5T0pHTHhORW42cU5QRXNRYzc4Vnh4eDFYQ1pkVW16bSs5OTU3KytkSWZSSVFXdVBneVNlZjlQZGdiUE51S0M2aTQxNWJiNzExNjN3Sm1tNjk5ZFp6Y29zNXVYTDg4NlNkUEZNd3VPS0tLNXlFNEk0NlVtMlQwT1FZR3hLODJ2ck51UDdoRDMvbzFsNTc3Y3AxcGU0eElzZmhvWlZTSkJ2RHJjbGs4dzk2eG93WlRsRzFyWUZiNVI5cEUrNm9vNDVxeW9EcjZFY2RoZ3VtVExnMzNIQkRDMEltaW9VV1dxaWpmczZGNFIxKytPRis0dVVDSm1Gd1paTElDei84LzZVdmZjbEpjNG5XYy9EQkI3Zk9od0hGSmdKcFBFNGFaNnRkV3VmcXBFRjAxS2Mxb3A2QmNTSjF2ZWM5NzJrN1I1cElxMzlhMXVJT09PQUFkL3p4eHpzbVI0Z0prMzdrNmRwcnIzWFNEdHJxeVkrL1hoaXVOQmN2SE41MzMzMnRXNEFaazZwTWtHMzMxckl1SjlOKzhyNkt4UGZDQXhYQi9BSnpZbkttem53L0ZFVG9wTlVuNjZJL3NtWTRXU1ZhN1FyMVVsZGdKREErbUMvZkI4Vnd5ekNCT2ViNzBRMFRXVXM4czZidDBncWRYQ1R1M0hQUGRUeHJLUFo4di9HTmJ6Z0V4L3d6N2VWL3hZdzRhY3d0alB5TjlJZDJjMS91aVJENzFhOSt0ZU1lZVlZcnk0WWZqd2dLVUt5dDFDTXR2YU9lZkhzVkllMTREeEE4SU5yQTJFQ3dBOCtBQmI5dHRkVldUaGFTMHZyeWRZL28veDBNMTB6S2VsTERvczAzMzd5MUVML3FQVEIzbm5UU1NWVlBuNWp6OUVKNk0vRGIzdmJzanBHWTkvQkxZWnJMRTZhN2ozM3NZOW0rKys3ckQrT3JBbE95TE4xMTExMFpwbVV4SXA5R2t5VVNMTS9DOUVuME02YTFQRjErK2VYWlJ6N3lFYitVQWhNbTExSlBJSzdEOUlwZk9SQm1Na3lPWWk3aGtQL0VGSWxwRDhJVUtXYnAvdzkvTkFtMklxOXA4MDQ3N2VRVGc0aXBlUE1pYmFOZTBuOWlFc1RFdC9UU1MyZDc3cmxuSnNHZ2I1OGNVZUNNTzJuTjNqd3JyY2IzbFNoeXNNYU1qem1YZ0RZSkh0bkpKNStjeVhyanpkNmhEK0VUSCtFbGwxeml6Wm40MmttMlFmc3htNU5ON2QzdmZyZHZPL2p0dHR0dW1hd0htUmhtdUx6dEU3TzJ0TDBXeHJnRU1FbExtL1dtN2tVWFhUUmpUS3kwMGtvZUUzQVJRMmlybys2WElpYjBnY3h2dUh1SW5zZTBpaWs0ajRrWVJkUThDeWFZaTNtR0xJMWphU0QvRXpoSVVna0pOaDVuM0FjOEE0aHhTdllzTWQ1YVhjQkV5M09nZlRQbGdzRWNEUEhPL1BTblAvVjRZUmJHakZ0R3RFbmFzaitGZDBnQ28zOG53SjVDSGRUTkNneXlVOFZNd3B4RGdwLzk5OS9mdnpNU0pEMk8zL3ptTjMzZnFXZVRUVGJKVmx4eHhReDN6dWMrOXptZmFBT3NKNEZNdysxVHc4WHNWcFRLa2R6S0NNbjh3eC8rOExoTGRhWHRyNnZoWWo3KzRoZS8yQWFmSnU2T2V5bWkyWnVOT1JHcEczUFhPdXVzNHpCejZzVjFtUG5YV0dNTko3OVRTME5Cc3RaYTM0NjZGTjNwTkRINWU2Sk5IWHZzc1cwYWh5Wk9wN1hCYlczaVMvRVpVZy9tYVRRTE5GYjZRVnZ5QmEzNG9vc3VhcXNMVFZqQmRnNUxDVnE3R0w0NzlOQkR2YVllVGhSRDlPYlVmRjNoLzZvYUxobys5d29rLzZIVDVPZXhvaTQwRFVXTU96U3V2SVVBa3lWNGh2dUZUODdIeEx2cXFxdDJtSFhSMk5CeThxWnV6S3JoMnVLbi9QZWhXVjViMDNJV0o2YmRPaC9jSkRSNTAyZzRjUkFhYmd5VFdiTm1PWjQ1YmNUY2o0dWhpTW1SUng0WnhRU1hnUmhnYUtML3hNV2crQTdIYjlUTHUzSGFhYWUxTUVhVHhQVVI3bG5FcHR0M05IVEdqUVRUbG5XRkczL3RhMTl6WXZiK04vbU5vMjZWdkliTE5XaWl1RTRrM1BobkN1NVNLRnBtZk01QlU4WDBIR3NYNCtHODg4N2pORytCT1BIRUV4MldrUHk1bUpvVkpPazFYZDVKek02RGNndms3ek9GLzNkb3VMcDNsSXpoRmlaRW9kUTJPTHA5bDBUcEIxY3ZmNVJSeWZHU2RLdDduSCt2eTNEeFZ4YVoyMmFiYmRhR0ZSUFQ5NzczdlpacFNscWFaeHhGdkpqME45MTAwN1pKSDhhS3lhdDRMbVpkQ0diNVgvLzFYMjNtWjh6QW1IV1pISUkvaW5PLy92V3Z0OVdENzB0UjEvemtmVjdTQXRwKzU1NElGSmdZQTJIR2xmYmEwU2JPd3k4TlU0RXdyZE9YWXJ2NVhwWGhTdXNJdC9XVDVqNzc3Tk1TVVBMMVN2dnd2dGR3c2dLMzNCdmU4SWJvdmZQWEZmK1h4dVRPUFBQTVVJMW5Lc1Z6K0k3TEFEY0FCUDc0N2JtMmVDN0NMY3dBOHlrMENJYUx5VGNRakFSTVlwTi9FUk5wajA3TDF6cmFDRlBOdXg3d1YzN29ReC9xZU44eFBjdXkwaklEWThibG5TbjJ1WmZ2TUYzdUZ3ai9kamMvZkpIaEtrRFJhVU9WdG5hRTJBcGNCUkRDWk13ZlRGdUpaWkhtNjg5RDBQaVAvL2dQTDdRVSs2RlVwTjY4ekluMEhRWmZQR2VNdm5jdzNOUit1T3FUVVQ4SVNLdnE2WElGQzJUeU8vWWRtZGpUVGNmb1pNeVJsRHhKZzgxLzlWRzFtSDB4WDJGV3hKeEpHc2tpaVVGNk0xcmVYTVdhWDB5MFJlSzVRSmdxTlduNjljSGhITXk3bUpBeGQ0dFordnZ4Mjl2Zi9uYS9iamljUnhRcWF5RWhUTTB4RTU3bWw3WklVbW1BUHAwbHBzZzhhZkwzWmsxTXpSRG1RakdtL0NrOS9VKzdNT1VGWWprV2ZTNWl5KytZSVRFUGgzc1RnWXdwdHdvUmlRcSttQXd4RTJQT0Q4UnZFb0xDMTlibnV1dXUyOElOMHl0clNXUFJ0SmhxTVoyS3FiU3U3ZWNmVFArc0tnZ1VNTUVNV3FRaUpyZ2VNSjBXaWVkTENjUjFpa25vZU44eEwxOTMzWFd0NHhJaXZkazJYRmZuRXhNdDR6Y1E3eEhtL0tvRXZpU2JJU284VCtFZEM3anpESEd4eE9yRy9BNnVZRURXT0tLYjgzaUVlbmxmQTg2NFRuZ3ZtMFRtd3gzQzAyUmc0YXVxU3J4Z0pIU1FSRmYxa29rN2owbUN5U3dRTDN2UlR3cXp4YmNHd1RCZ2JFd1dNV0pKQ25ncmVNbFAva3dTK0FKaDBubkN0OGhrRDFOZ0FnamJKbklPdmt3WW5nS05Xb255VjFsbEZYOE9UQmIvSiszbWY1WjhRTlJYbkxqOEQvcVRueFR4RjRhSkovd2VQdmxOV3B6L2luREJlS3RMK001Z25CQytZL3h6bEJpQktaaUJCMzVkN3N0U2x4UXgwVXM3OHo1YmZKMzRMR2t2L2o3K0R3VHpaVGtVZnN3OGNVMGcvTjc0SkZQclJ4RlFwQTJIMC92NnBHOUJpT2tWRS9vY0U5eG9VUDc1NGtjdEc1c0loY1FqTUg3NmViNTlBZkd2aTJWTzltT1dOaFVKWVRNSWhiU1ZjYzd6RFVKWk9KOXhBTUZrWWNyYmJMT05aOHg1VEtpZjl4Y2hBNkwveEdrMGlZemhEdUZwb3ZtRVNheXNlb0lMQ0JoaEU0UFVKRmQyL1NUOUJzUExUKzVNc0RLbnRrSEFSQmswSjE1NEdHR0tZQjVvUzB4NjRab3d5ZWF2WWJJaHE1Vk1iSDRTWmpKbFFtRWlEcHFoVE5kK2JTek1CR2JFczJkYlBCZ3VEQnJoQzRiQ1pDTnpjRlN5ejkrVC8yUFNmemluK0Z0KzBncm5WUDBFTTlvTkVaQkVYMUtNbm5OZ2ZKd0h3VndRUXBnWWl4TXNXY0UrL2VsUCt5QWFOQjhtVTg0Sm1qUEg2QWR0UjlpSjlZRmduVUFJU0dDYklnU3dJaTZwYzdzZForMXFHQk85WWdLV1hNL3pEamgxdTEveDkzdy84djhYejV1cTc3MjBJYWJkZ3NtTUdUTjhjL2xkUG54ZnVyV2ZjMk9XajI3WGpmTHZ4bkNIOEhTUThwaUV5Z2d0UlFFU21md3AzcnhTZHE3OWx2bjh5cGh2QTVIOG9jZ1k4cE0yazBSS0d3cDE4RUxuSndnaWhXT0VtWXZvVTE1K21ENGJVSEF2bUFyM2dMSEQvUGtkclJzbVJsUXZVWnRJODVpaUlUU3dWRFJ1N0w2cFk4VitwczZyY3B6KzUrdExZUkRxQXRmOEJNeTErZXM1RDQyZVpDV1kxaUcwT2FLeUwxZlVONlpFdEhNbTNTMjIyTUlMTC82a3lKOGdDUEJUL3A2UlV3ZDZhQmlZOU5MQUlwNjlYRHNkNStiYkczdE9DS2hCZ09GM0JLY3k0U24wZ2ZkYmE0WEQxMFo4R3NNZHdtUEVMNWFTelBCM2tFV0djSGkybmFzckJRK2gyU05iSlNZbUpRcndqSTVHb3Myd1BDZVlza0xEZVVINURXS3lEc3Nyd3UvNVQ4eGYvSTZXRmlnMUNlQnJ3M2VLTm9mV3hhZUNoZnd6eGp4TTFpZmFncFVDNW91UEVxYURwb08xZzA4SVAyTlJTQWozbnE1UFRJSUJNOFlzV0lOTk9GWnNGNVlHSmxBSXJSVUxRTkJhdzduc3dSdVlMVllFUlZabkNpUnJuUWREUSt0UDNTUFVrOWVhY1NkZ3ZrOVJmdEpQblZQMU9KYW5JS3oxaWdsOUFwUGkyS3g2NzZrNEw4WVVoM2xmeGdmam51Y0hQaWdaQ0xIZG5obS9OODNOWmd4M0NDT05DU3RvVGd4dUJoc2FFT2tFdFV6RnAwS0Q2UnBWUTRCQW0xbXpaclZPQmp0eUxBYy9admlCeVIyc0ExTWdmVjJLWUxha2Jzejd4MGhkR0NPRUpBS3NsSm5LYTZzdzNPQ1RZbkpseTBDSVNSWWZNTUlCRWoxcmIvR1IwaDVJeTM3ODV5ajl3VVFjR0J2Q3h3eVovbWh2Q0lRcHRoWE1RZ0FZL1VVRHlXdkZXSGRZT3dveDlsbTNTckJUbmluRHhMQUFoWGVrZUkvd25mVzJnVEQzWTZySGp4c2puZ2xtM0VFUTV1dmdYKzBWRXhnMTczb2VrMEcwcWQ4Njhzd3QvMysvOVZhNUhpWUxKZ2llekkyOHR3aXhBZU1xZFRUbG5PcWhhazNwOFJUMEEvL2kyV2VmbldtdG1VK29zUHZ1dTJjNzc3eXozOERnMUZOUDlScnVGRFJqTEc3UlRkb21oekMrd09BVGg2RmlIVUNUTEY2TG1Sa0dDS0dGd2FneDc4WUlaa3hRVHBqMFlSekZnS2x3SFl3RkJnL0JxREVsRTJERnBNcXp6ak1CVEtjd01PNi8ybXFyK1dRWmFOdlVUM0RjcUJFTUY5d2dzRUE3MTVLTmFEUFI3b2xLRHBvbTJqMTVmL01Fd3c0Qll1Q0RUeGd0T2s4d1JoaGt5Z29VemlVaU9oREJNek5uem13TG5BdS84VW03UXNCYy9uaWQvMkc0ZFRGaHJBekNiVkNuM2FscllIRDVnQ2R3bjJxbUc5NHQ3a3ZzQTY2V3FXNURDcCtwUEc0YWJnRnRCZ0dUQVNZc3BIQW1EY3krK09hcW1uL0p4cUoxZ2Y1YUpIdXVDeWFxd3UzOFZ5Wm5HQXFURlJwRWtOUjVVVEJ6SXVrakljYVdSTVRxRzVkallGdGttcUh0NElGR2lXWWJscDRnS1o5enpqbmVQQm1MU0dWSmhmSVJlejhyR01JNGxQdlhaNjNKVHpqNFlQRWY1bjNDWlBNcE1vYlFGcDRoR2k1bVpaZ04xekpoOEh5WVNQTFJ0VEFnL1BQNGV0bFdNREFuSXFaVDBjbmhQdFB4U1I4dzk3N3JYZS95dDhjRXJ2WE52bDlCZU9FSDNnWGxkMjdiWHBLK1lrN1BVeDVuR0RpTWttZVIxMll3dHl2NVNFdllTWTBEM0FhOGQ3eVBDQzM0MFhtMzBKaURWczY5bFdERFA1TTh3K1g4dWhNNm1HZzl0OStWaXZvREp0dzdyM1h6M2hZeFlUemtCUVd1bjI1aS9nSC80Tm9nTXhxWXh0NmhZYlZWQ1R5ODN4N3JDTThmTjRQU2w3WUVtMkhkZDlUcU5ZYXJKNEpFamlhRlJzSWtEZU5qWUlRWGxoZVFTWlQxZUV3d3JGT01hVmpoNFRJWjVDZUVjRHovaVpTSkgwdVpXZng5ZVFtWW5Ka29NTHRBTUNPWURQZm5oZUZsUnRNaXNobk5ZZHdKb1lZSkMzTWhmUVFUbUNIK1VkSUlvbEVGaGdYVFkvMGVld3FqZ2NTSU9wVHB4NmZFZytIeFhKWDF5UXMrcDV4eWlqZVRJdENRcG81bENjRi9Dek1zUzZmSk15RFlCOU14NndsNWJvd05oS0hpbWxxWUw4ZUlacVlmZ2RoUkJlMW5GRWtaZ0x5YmcvV2pNRWRsM2ZLV0FtWEU4a0lDUzNpMjIyNDduNFl4bUpQQldwc2N0Sm1LNlp2eUdYdWN1UWFNU09ONHVZS2xXS2ZNdUVhN0lSMGxrMjRnR0JmanZrZ0lPTXAxN1o4NXZ6RWVlRTVZRjJnelFpei9LNEdFRjU2Q3RZTDdVR2Q0ajRyMVZ2a09zK2VaNVRIaE90YktNeGJBaVYzQTJIWXpqOG1uUHZXcHlvSjVsWFlNNGh6R0w4OGxSUG5qRGlHZ2ozbU1kdzUvS3VsUGgwbFlmckJNWWVuam5rVHhNd2FVVGFvbDNPR0c0WjNGRFlNVlNabmRKb1loTno3VGxGNFN2L3NGbVlSa1ZoTnZxMDVpZms2RDFDbG5yMCs3SjhZUnpacWlBZHpLa3FJSnhXZDNJVDBmV1d5a01WVy9ZZUZNVGZRKzZ3NEo4Q1hWZDcxM3ZoM1QvYjhteUVKdjBsK2wrZmpzTkNRN0o1ay9PRmRwUHhzS3lCclF5dGJESFdUU2RhUkJsRW02ZFVNeGNiOWhBSm1neEJ4SzYxWXdVVWVtSzFMMXljVGNjUjFaZGZMRXZhV2xkNXlYNzR2OHBtMlpwc1Nra2xtY2VPN1MvUHd0cEpWN2JQSjFoZi9aaVVuTW9kV1VndzQ2S05rR0NUMCtUWjhZYWV0OE1ieldEa2Zob0NadmoyMHh5MWU0SjUvc2NBUzJlU0lURnpoQVpCd2lJeE50aDNqL2VDL3lkWVQvcFluNXNaNXZsNzhvOTBkYXRWTkFtajh2UEY4eWpuRnRxS2ZPWnd3VGFZV08zYnp5YzBZVlRFaXZxQUNnVnF0bno1N3RVenJHMmtYS3pEdzJaSDJLbmRmTE1WS2VTZ2xvM1QvOFEzOTIzSEhIanZvbGtJWlQvQmhLN2VvbDV1amZLMDRHQnpIeGFLcEkyaXFHN3pPTWhiNjFiaEQ1UjRLckUzUHVhRmN2ZlI2QmN6c3lUWFdLbFdwbGt3bXRDa2xacWRxOHlUSUV0UFRTWjdRdWtoNVFNRFBocjUwelo0NzM1eEZzZ2drSHFSSUpIK2tYcVEySkRSTXAyWE80UDcvVkplckQ3RWQ5U1BvU0d2eGVwWG16WGQyNmgzMGQvUVlqcEZ3MGtGQTRqbWtSa3lUYUU1b2lHZzVKNnBHQ1EyQlNsZmFSeFlkbEoyaFNCQzZoTldQYXBFQm9tdFJOQUJzSlIvREI2cDB2clpySVZmeDZXRHJRYmlBMG9KaFpEbDh0ZmNRTVM3MWx5UzdDVGRITzZIOTRodnlmR2lPY3l4Z0RRejVUeEhsZ0dlcE1uY2R4Zkxtc05TYXBQbG9kUzVrWVorSDlRSnZFc2tCZ0dab3ZHbUNLbExZeG15RXJFZG9zcmdFc0NWZ3hlQ2RZSXNUN2dyV0dqU1BRY25nZW1EaDVsNHFFU1JrdEV2ekoza2E3Z2paTW04QWZjNytFQ2Y4N3BtcnV3emhDeSsySGlwaWd0UlBGallVRDZnVVR4amxqSVR3THJrMDlYNDZEQ2VmenlWam9sekJ6S3crMUQyampQUWphUDFneGpvckUyQWx0WlF5VnRTR1lyS2tqekh2Rit2aE9GTCsyci9TZmJNeEFmQVh6WTdnL21GQ3dEaEx6a01JblZ2ZTRIRXZOK21pNE42ZzhPN09NUzIrNnRKTkFHY3hBbURIeHdRMktlREh3ZHpFWkVVSEx3SklVNXdOc1NFM0dmWmxZZUZtSFFVeGkybUxMKytMd1k0NHk4WUx4c3NHMG1EZ3hJd1ZUT3BNcUx6bVRLUDVxek9Zd09GN2lPZ1REd0ZXQWVSb0d3QVJNMEJYUEIvOGppU2xpREROMUx5WUkvSVgwZ2NrQVJocUxOdWMzQkNMT1k2TENGY0c5TUl1bkNLYkUybDM4aFl3bi9MMzRvL1ArNFhBdEFodW1iZkFER3dRTVNwRmdjcmhKd0pjMjRRNmgzMldFUUlxUVFqOXBDOCtKZHVPN2hFbkMzR0NDM1lqb2I0TFd5THhGUGR5Zk9BUk1pNWpjZVJiOEJxTmxRb2VCdytCU1JMQWFTNDFramZCTU4yQUVyZ2c0akJmYXpiT0dXZEJlaERXZWQ3OFVNQ0hJRHJNc2VNSVlZQXIwcHdvbTRFaTZTQVFZMm82SmwwamRtTURFbk1HOXdBenNxWjh4Mnk4eEhoRmF3QkIvTjJNSElRZi9hbEhZd1IweVUwRnFqRjh3aEdFenp4UUpMRkFpZ3Y4YzNIbVc0Sk1pK29Wcmh3QTlCRExlVTRnNUV6d1FoaDlRTUNKdU80Nk5NU0VOcjZCeVcrakRSREJjSGpDQk4zdnR0WmZYU25sNWgwVU1ZZ1lvTDBwZ0pzTzZWNzVlSm1ZbDE4K09PZVlZei9oNXFjZUJtQnlEbG90V1VwZTVsdlVWVFJOaEJ3YkZjNEdwTThrYnBSR0FJY0pvd0k3bkFtWm9XNzFTd0o1M2tESGFMYmFoVy8zVVI3c1kzMHpPTVliVnJZNjZ2NE1KZ2dUdk5ReUY5M3dRREwxdWUrcGN4L3NHODZmd3JzSFFlTDdUUll5TG9PSFNqbkdadHlyaTFjRndVOWMxeG9lckIrb1VqZXEzYWRNa3ErZlpYTkxMNzdlQnc0ZXBGMnZjL1IvVy9sd01nRjVVdzhNd3NERXdYbU9ndzRmYitIVzRtQ3hJTTRmNUtraFNLU2xqM0k4anRXSXkwbjZYZmU4d011NVlXUHNOQVVQQUVCZzFCQnJOY0RFZGF4OUg3eHNMZ1JhajlnQUczUjdNcy9peVdJWVJnb1FHZlErcnp4QXdCQXdCUTZCM0JCckxjTkgyaUZ3aytHUFNpRUFIQWlRR0dSZzJhUmhhZncwQlE4QVFHRFFDaldXNFJDS3pXSC9TaUVoZm9nNUorRUFVcEpFaFlBZ1lBb2JBYUNEUXlIVzRMTVBaWVljZFdsbUtSZ1BxNGJlQ3BVbnN0M3JjY2NmNU1QK3l0WFBEYjQzZHdSQXdCQXdCUXlDUFFPTVlMb0ZSN0ZiQ0dpOUM0Q2VGWUxhelo4LzI2ZlpZSDZoWTdFbnB1dlhURURBRURJR3hRS0J4REpmMXRpUmlIK1phMjFGN3Nxd3AvZGEzdnVWOTFpRTd6S2kxMGRwakNCZ0Noc0NrSTlBb2hzdUNkTEs1aE9UeWsvSnd5VVN6Nzc3Nyt2UjNrOUpuNjZjaFlBZ1lBdU9HUUtOc3JxUmRJNVZmeUJNNmJnK2pUbnRKVGJqYmJyc1pzNjBEbmwxakNCZ0Noc0FVSXRBWWhzczZXellJU0cyZVBZV1lUdG10OE5PeXlYMHNqKzZVTmNKdVpBZ1lBb2FBSVZBSmdjWXczSkJnUENUQ3J0VDdNVCtKcFBpbm5YYmFtUGZDbW04SUdBS0d3R1FnMEJpR3l4WnNaRmlhRkVLN0pTbzV0Um43cE9CZy9UUUVEQUZEWUZ3UWFFelFGSm90SnVWSkliWTZHOVQyWTVPQ21mVnovQkFnRUpLbGZxd3BaN2VpWWV3bU5YNm9XSXZIRllGR01GeGVTTklZc2tIMHBCQ2JwN01IYUZPSndEZUM0RmplRlV2Z0ViYjF1dlhXVzZON3hqWVZseWIzaTYzdldHSEFmcTFMTDcxME51Kzg4L3A5VnRtU2o2VnZiTVhIRm4vc3gzdkhIWGRrUC8vNXozMzh3dTkrOTdzbXcySjlheEFDaldDNDdGTkpvZ3NtNFVrZzl1Sms0KzBtVHpSTXVtVE1ldHZiM2xiNlNEbUhLRzJqOFVTQWZZclpqSnhrTlp0c3Nva1hzbnA1ajJIQWJJN09YdEJ6NXN6SjdyLy8vcWlBTnA3b1dLc25CWUd4Mmc5WDVtVDN6VzkrczdrYjNSWjZKbk95MjJDRERScTdONmEwVzdmNzdyczdaYzhxOUx6ejY5MTMzKzFrMldnc0ZwcHdHdGszbVlxZGx2QzVMM3poQys3UlJ4L3RmTEExamp6MDBFTk9nbmNqOFdycU9HaDR2enIydzIyRWhzdVNJTXhQazBLWTFGaC8yMVRDTmNEeUxuWTg2a2F2ZnZXcnN6WFdXQ1A3N25lLzIrMVUrMzFFRU1CTmdEYTcwMDQ3K1VESHVlYWFheUF0SThzYW0zY1lHUUtqaWtBam9wVEptVHhKeTRISW05emtGSTc0NDVkWlpwbEtMZ0syWVp3NWMrWkU1YzBlMWNta1NydGd0aC84NEFlekF3ODhNRnR4eFJXelFURmI3bzFaK2ZISEg2L1NqSzduVEZJZTlxNWcyQWtEUTZBeERKZUpkMUxvNmFlZnpwNTU1cGxHZGhkcnhlS0xMNTZ4NDFNVnduKy83TExMWm9zdXVtaVYwKzJjYVVTQVFEaXNFUWNmZkhBMlk4YU1TaTFobkJNc3haaVhsVGw1elpOUFB1bWo5dnZSY09lZWUyNnZlWC8yczUvTmxsdHV1ZVM5N0FkRG9DNENqVEFwMC9sSmtrZ0pLdWtsc0tUdTRKaU82ekFSRXpCRnhHb1Y0cmt2dlBEQ2ZvSWtZTVpvZEJHWWYvNzUvUVliM1ZZVEVIbCswVVVYWlQvNzJjK3llKzY1eHpOY1ZpTGdObHBzc2NWOGtOWGIzLzUydnd5UUNHYUljeDk0NElGU3BoeEQ1bVV2ZTFtMnpqcnJaTzk0eHp1eVZWZGROVnR3d1FVemxpS1JuOXpJRUJnMEFvMWd1RENmU2NxZmpCbU9DYWlKdE1BQ0MvaUpyeWhRb0xsZ1JzZDFFQ2JaMEgrU25qQUJuM3Z1dVJrUjNFYWpod0RQYysrOTkvYkxmbUt0ZStxcHAveFNuK09QUHo3Ny92ZS8zM1dwRisvN0lvc3NrcjNuUGUvSjN2Lys5MmVYWFhaWlQwbGcwTEJwejhZYmI1d3g1dkwweEJOUFdLUnpIaEQ3ZjJBSU5JTGhEZ3lOTWFtSU5KWkk1azBqdEZYTXlTenhLdEtERHo2WW5YcnFxZGsyMjJ6VGtWRU1zekxyTnRGT1NBaGlOSG9JWUs3ZGV1dXRrdzBqSC9nZWUreFJXYk1rQVFZV2pTOTk2VXQrYTBvWWVpLysyeVdXV01KcnRVVm1tMnlnL1dBSURBQ0JSdmh3U1l5QWhEd3BoRVlIMDIwYXNTWVRIeDkrM0R6eGZHR2ttQm52dSsrKy9FK3Qvd20wUXVNeEdrMEUxbDEzM2VRZTFVVGRzd2xIWFRNdTE3TW12WmNzVlBpRVl3bFZSaE05YTFWVEVHZ0V3eVdZb3A5Z2lYRjdtUGc1a2N5TGpHbmMrbEZzTDh1QTFsNTc3ZUpoSHpDRGorN2hoeC9PZnZHTFgwUUR4dEJ1MFhMUmRvMUdEd0ZNL2ltNjk5NTd2Ums1OWJzZE53U2Fna0FqR0M2U2FwT1h5UlFIR3dGRkxKdHBtbG1aelNmUVZJdEVEdDFycnJuR0I4L2NmdnZ0VVY4ZGZ0M2xsMTgrcVVVVjY3VHZVNGNBNWw1Y0JTa2lTSW9vWXlORG9Pa0l0TnZ1eHJTMzVGbEYrNWtVWWdKYmJiWFZzdm5tbTY5UkNUQUlZSWtGZ3lrVFVYYjU1WmY3Q05RUWpZcEdXNlExMTF3ekl4SjJPbmRRNHRuZ3I2UWRCTGZCU0dnL0tRakxsclVVK3pLTTc2eUJYV2loaFh5N2NNR0FFMzdQWGt5eGRkb0ZEbVdKYVJDb3BwcXdpS1VDN0hoT1U1RllCc0VaTndoTDJsaldTSHQ0SGc4bzJ2cVJSeDRaK25QcGhqbGpoWWh5MnNYOENpWjF4ekR4R1NnSXdSMUdQU2hKNUlPZmp1ZmZyZS9EK3IwUkRKY0JRVkROSkZGSThvNkpkZGdUNWxUZ3lzc0l3NDBSekRaWU1FaGFUMUZhd0k2bFlHakhxNnl5U29ZV1hIZWRNbVp0SWw5WmZzSzRDaE1NRXdiK1kvekkrY21ZaVpKSmlaelA2NjIzbmsvbWdEYkgwcEpBdFAzT08rLzA2MFMvOTczditTVXNyQzN0eFlmSTVMeldXbXY1REZ4Y0Y5cEZ0QzRNL2NJTEwyemJ6QUltQjRNbFk1ZlNnR1lycmJTU043bm5mZjh3WFpiZDREc2xVeGVmQ0FqMGU5Q0VJSktpR1lvWTV2ZlFwOVI1ZFkvekxBaTJDOHlEL3BHL0dkZE1qTUR1SXgvNWlNZXM2S0tnblZoVGlLUW0wS3NYSXNJZUpvYmJoR2VKUlFaQnBJZ05ZNWV4OXVNZi85Zy8xMnV2dmRhN3pQQTc5MHEwZi92dHQvZDlEYytWK3lIWVVqOTVxQU54TG9MaVJodHRsRzI2NmFiK0hRc0M4T21ubjU3dHUrKytYaEFJNTVkOWNoMWpqZlhNTEx1YU9YTm05b1kzdk1Gbmp3djk1WG5qZStkOVp1Y3ozZzJsYXAxSWE4ZFk1VkxXQytKbXpacmx4SGowRENlSExybmtFcWNYcEJHNVkvV1NSeCtjbUl2NzBJYysxTmJISFhiWXdVa3lqcDcvbmU5OHg4MHp6enh0NTJ0aXFQeGRtclA3d1E5K0VLMzcwa3N2ZFpvMFduWEp3dUEwbWJucnI3L2VhVEtNWGxNOEtFM1h6WjQ5MjBrYmR4SXlXblYxYTZNMEE2Y283V0oxL3JzbWZsOWZxRVBCWjA1Q2c3djQ0b3VkbUgzMG11SkJDUUJPeTZxY1VpNDZNZXJLN1FyM0xQdlVCT3ZBTGtWaSttMjRsdFZWNXpkWkhKd1lXT3IydFk3dnVPT09sVEVLZWFPMTBZWWozM012eEhNQnUyMjMzZFpKU0hDSzI2aDhYN0NTUU9qa0k0L2U4cGhqam1uVlJSczMzM3h6ZCtPTk56b3gvSTd6enp6elRDZGhvWFYrNmpsSUFQUzV6WlZOelAzd2h6OTBFdUE2NmtvZGtCYnRUajc1WkNmaDBFbW82WHF2VkJ0RzZIaEhMbVcxTFVwanhYQjVvV1ZpZFpLV1VzK3lrY2Vsb1RocGhXTS9NSGwrLy9tZi94bDlSako3dXFXV1dxcXRqOXIzMkdscnR1ajVNc1U1WmFscU8xOGp2UEozYVVFT3BoMGphZHBPdm5OZmx3SzBmSnQ3bVZCQ25RaUd0Ris1aEIwYmIxUnBIMHhVUzJCQ0ZXMmY4b0U2Slc3dzljaEU2WTQrK21qM205LzhwdTJjcWw5a3puVFNaSncwNmtydHF0SjJ6dm55bDcrY2JBTGptTi9Cdm1wOXZaeUhBSUZRTWtqU0VxZEtiVlZ3bzl0MTExMGRtMnowUXdocTU1eHpqcE9tV09tK0FSOXBtdTY2NjY2TDNscVI0YjR1eGlCak1jV1l1ZmdiMy9pR1F4Z045Y1krcFNHNzFWZGYzWDM5NjEvdmF5NldOY2pKSXVHa0laZmVMOWFHRVR2V1RJWUx5RXlBcVlFVkhXME5PYWh0K3ZyUzZFWmhnRElweWF3VWZTSXk0WGIwRDZsZEp0Q29KSTVHakRaUXQxOW9RNm1kcHhTNDVXUWk4MHczZFU2MEU0bUQ3UHEwMTE1N1ZaTG0wVUNPT09JSUo3TmdSMjEzM1hXWDIzREREUjNNRnUyNVgwSnczWC8vL1FmS2ROR2N5d2pCNnRPZi92UlFMRFl3WE42VFFWSVZob3RHaXZDalpVc0R1L1hOTjkvczN2M3VkMWNlMzNLRnVDdXZ2REo2ZjhZS0RKbXgwMDBncU1KdzExOS9mU2NUdGVNZDdKZllRVXFKU1hxeUF0Vjk1NGQ0WFFmRGJVU1VzZ0R6ZnJYVUdrMStieW9SMmJ2bm5udU9kZmNJQU1PL0ZpUDh0L2c3ODhSM2ZFLzRJSXVFZndnZmJGM0NIMDRRWG96NERUOGN1OXhvMG91ZDB0TXhBbVkrL3ZHUForOTg1enU3WG9mL2pYNEhQMXorQW83aGY5dHV1KzJ5elRiYkxQOVRyZjlsa3ZkajZzTWYvbkN0NjJNWGhiMXFZNzl4ak9mUHZzWml1dDd2TjhqTWNmamZpOW5KVXUyb2VyemJrang4eEJLbU1yay9rcjdpcXZmS24wZnNCcm1lVS9FTytYUDVIMzkvYWp6ek8ydmZ3YjBzaXB6enVoRWJVUngxMUZFKzR4dnZZSkY0ZHdpUXdoK043MWh1bU5MZ1JuemJaQUtUbWJ0Unl4OGJFVFRGd3lVd2hXQVpTVllkUVFqRmg5KzA3L0p4K29DWDg4NDdieXk3Um5SeGJDcytJbnZsVStwZ3VIUVNoa3NLdnRqU0tBSTBZQm9rUk9pVm1LQlNBVmN3QlppdHpHWitvc3JYVFZ0SnppRlRycC9naU1Za2lDc1ZtQk91aGVsKzduT2Z5NjYrK21vZlFCS09Geitac0FMREphZ25Ud1J1TVRFUlNNYi9lU0lJU243RDdGZS8rcFdQQm1VaW02RWdwWlNBRTY0bDBucWZmZmJ4N2JycHBwdkM0ZHFmQkpwcDc5dE1wdU5rSFdCRk5pbzJveUNBNXR2Zi92WkFnaUhCanZ1REg4d0hBWVdnSHNaT2pMRXpoNEFiUVVyRjMyRW1NTyt5QUNiR25ueThHZThsREMxRnRJbEFOVm5tUFBNaE1BNUd6ZnZBMkVreGRibFlmRTVxK25YKytlZW5xbThkVDdXVlNHMFNrcEJzcGh1QlE0eVJjaDJCVm9jZmZuZzBReHkvUC9iWVk1NFo4ODZ5MDFuQUgrR1YrMis1NVphKzM1eWJKOFlEUWgrQm9kTFM4ejgxN3YreDh1RUtmVzlpZWU5NzMxdmJkOVd2Q1dTNnI3L2lpaXQ4c0VIQVlsdyt0U1RDU2VxTndpZXRLT21QMVFTUU5KVlJtZkxyVmphNzViSENkS3Q4dmxHekdNRWsrQnMxMGJYYWkva1ZYNWlpbzcwNVZJek1hYUp3WW14T2pNUC9WaVcyNEl0Zi9HTFg5dTY4ODg1T0UxYnIzdUdmMEM1TlpPR1EwMlR1empqakRLY0p6UWU3RUhSRnUvakVMQzV0eE9IdjdrYVk5SHNOMU1uam1mK2ZJRE1DdWJvUkpra3hSKzltMkcrLy9ad0VoSzdZNU85VC9CK3pLaTRuUlpJN1dZUjhUQUErUW9KMFlrU2dHWUY1WE1QNXhVSlFEMWdXNzhOMy9KaGJiYldWYjMrczduQU1YSWs3b1I3ODVRUitNdmJ3MWVNYTBQYUY0ZFRrSjhGOStTQytXSHM0UmpCY2pCVFo3azNBc2Q4WVU3Z3FDS0xDdDN2S0thYzRYRCt4ZTV4MDBrbE9na3lzR2lkaHpZbWhlOU93R0hiYjlYekhQYVJOSXh6dmVvd0lSdVRkR0hRZ1g2d2ZRempXWVZMV1BhSTBsZ3lYRjBQbWl0aHptNGhqK0trVXp1OEhzWjVxMitBZTFlOUVsOGNtZnBpYVRHZE9tbSt5SHpDZ0ZFbnlyOFVvbURDbGNVWjlwY1Y3TWRaZ1h0MndWWllsUjBSNVdZQVZHTWkwWEZxWHBQMUtBaVhqb0Z0ZHRGbm1TVDhaUzlNcGRxMzFYZXRDbmN6ZXJqaFpkdXR6NnZmWHYvNzEvcDRJTGxXSmdDR2laUEUxSXFEeGpGTDFWejJPZ0pTS0cwQllJWXE4YWwzNTg4QTB4Y2pwcjdROTc1dUVzZWF2aS8ydjVVUHVsbHR1U2NJRVV5U1FybHRVZmlvSU1DODRjaFA2alNEQU81a1BrRUs0eGRkYkhBTjh4MjhiaTd5bWJ0NFBtYXE3OXBPK0l3eEoyNDhLdXRSUERBQ0NVd3luRVQ3V2JJWkx3QXZhU1Y3U1Q0N1dodjVBaEIrTVNGdldqZnpnWk9KRU9vNU52Z1RSb0tXV3ZXUktRTyswYUQ3NkpIbEpxNzdzK1JlV3llV1FRdzVKU3V6aFpqSnp0U0tXODllbi9uL1RtOTZVMUNhb2s4bVR3QlFrL2xRZFRJUUVrNVFSMm5TSVdFN1Zrejh1MDZVWEJsSjFNbkhPa2ZhQnhwNi9ydTcvVE5KTXJnUzlsVEg2V0hzSVB0SW04KzRESC9oQVV0dXEyaTZpZmRIZ1lnU0RmOWU3M2xXcnYyaUNLZUxaTUxiS2hNaDgreG1MV2tQdEdHc3A0bjNIaWxGa2h2bDZ6anJyck5UbHJlTllUbGkyeEhqSVgxdjJQOUhOcWZtV1pWZ3NUU3Q3Zi9OMWM5NEJCeHlRRkVvSkdCekRxT1VPaHR1WW9DazlQTzhma0hSZnkzZkg5VTBnZGtGaGcyOThLZ1FqaWFtTmJMZklGaVd6bmM5OFZHd2tDK0RKc1l0UE5VVWtiU0F0WUl4WWRCL0x5eHc3dDNpczdKNmNpeDlRNndXVDl5N1d4M2N0QThvVStldjl6ckhmOGRmSlFwUGhuK3VITk9GbjBxWXJWMEdnSWUwU000aGVvNG5RKzN6eER3K0NOTU43dnp6QlViU1ZwQjBjcTBJeXYvcUFPTGJ3dys4dHBoajE0VmVwYXhqblNQdE9CcTNodDhSWHErVnZYYmNlREcyVHNPTVRRaWlhT0prTVFoYURhRXhCcUlOUE1lUDgxNDcvQ1Q3RUY0eVB2WmZBVTNiMVlvNlJZTkJXcDRUSFRPWnVuNDYxMjdzVUx1UThyVGRPN3ZaRmtoQXk2NDA3TllyaDh1S1MvWVdKZUpLSm9BMENFWGlCRGpyb0lMK2hleW9BWXpweElrQ0VVaVNlSTlsbnRDYTArRlBiZHlZa21jRGFqb1V2QkE4UkRGSU1NQXEvbDMxMm02Qmc4a3dPdlJLQkh6THZKUzhqK0lTSnBTN0pMSjFwdVZMUGw5OXd3dzBabVlSU3hFUkhwcXJpeEpvNnY4cHhuaTlSclVUeXdvaDZJY2EzRWl0azh1MzVhR29DejBhQmlCd21FQ2hHQkNqeGJIck5pRWRnSUZuRVVDUml4RE1oaUk4Z3ZicEVVQkpiWC9heXRhWDh6WDV2WXdUOEl0RkhWaGYwR3JUSWU4VTdIMlBTQ09ZODkyN3ZackV0by9hOVVRd1hjRW1oZDl0dHR5VWpUVWZ0QVF5elBhUWJaTm1KMXFVbUl4NkhlZit5dW9uMDVDV0tTYTFNTXZKZFZkcmZGSWFMUkYwa29sQ3BuekpvSXRxUzNMSjFpSW1OYU5rWUVkRktoRzRkSVlINldISlJ0MTB3WENKSVkwUjdtRmhqenlwMmZ0VmphTGRFSXlzeGhMZklNUEZYSlFSSXRMdGRkdG5GTHlXS1RmeFY2eHJFZVRBQ1VtaW1DQUhqZ2dzdVNQMWNlaHdGQW1FdEZXMk1aWVJVcEZnamVpVTBiNWJvRUMzZEN4SEZqaEFXVzI0RjR5Ym5lYStFVU1MOGpjWmRKS0xxU1EwNXloYTdZcHRqMzN0L1FyRmFSdWdZaWJEclNGY2oxSVdCTllWSmdPVlNEUDdVeXpxd20vVllFY3RURkowWTFacVFrQkdhcXBnYTc5Y201Q216Y3I4YVk2eExDQU5vaEN3RHFrT1k3TGcrUmdnSjhyMzdyUmRqdjVjZEF5dTBvTHJQbVRXU3FVbVhjUVN6eFFVd2FLSzlMUDA2OU5CRE02MHk4T1p0bmoyTW9Bb3hFV1BOd1pMRGxwWFRSYXhqTFJQdWxPYXc5aGFpTUNJRVVEYWJpRkVRMUdMTUwzWisvaGhMazlDZ1kwSnIvcnppLzVqM01Ta1hDV2FKK3dSTnRRNXhYZXpabzhsakRSdEZTMTB2L1d6TU90elFhU1llQmpmcjRKaHdKNTFZZzNuWlpaZFZZbDVUaVJYUEJnbTVTSmlKZVdGaEhsVTBQVjV3ekxRa0JDZ1Nrd0w3c0dwNVRPM0pybGduNjJ6UnpHS1RRdkhjMkhjRVFyUVZ6TjB4b3MwSUl3Z1N2UkFUSjM3dnV1MENSOXFscU5Qb2JUSG5EWk9od1hnUm5DakhIbnVzSHhzS212T0o5TUdrVExPQjBXeXh4UmJldDc3NzdydTNiUzRSN2N3UURzSjhNTE9taUhld0xqR25FYy9BdTR4QUZpTVlQZ0picjhSNll6VGNYZ2dCREVFSG4zV1JhQ3ZtYlJMRHdCdzV0d3B4SFV3Zm9TWEZWQm1EZzNSclZHblhvTTlwSE1NRklMYTRRbXJEMUtMMVc0UEdiR3pxWXdDemoyd3ZwcnFwNkJ3VEE2YlRtTzhOaGt0Q0FrV2llaE5adHhlV0Y1WEpocy9pdVpqWU1MVmhiaHhFOGdhd1Fkdm9aenN4bm9taVkvME9UN0hKQTk5ekxBbEl0K2RDdXlqZ1VJY0lCS05kZk1hWUc4K2tUcnZxdEFWOEZSbnR5OWUrOWpXZjFJTnNYRHpMTXFhbXRiWGViTXZPUjFOTmFQOHgzR2dId2dRbTVYNElmMmlaVmFYcy9tWDNoWkhqKysrRmVIL1JObU56Szg4SDRZY3lhQ0lRTXZiT0RQbyt3Nnl2a1F3WHdNaFNNMnZXck9pZ0dDYWdvMVEzMnRqWlo1ODlTazN5YmNFRWx0THdtTFMwM3JLdjlJejVEcE94UjVzZFpNcEJXNXNaNWV0RElLakwxS2dIaG92SkhPWVlZMkJNV0xIc1dmazJ4UDZuVGYyMEM4MFkveS9DYXN4WHl5UmJ4ZUlRYTFzL3g5QytDSVFrNnZWakgvdVlqMHd1TTUyeXJSN0Nkc3BQM2s5YnlxN0ZZcE5pQmtTQXAvempaWFhtZjRQWkJvR3FLRmh5SHNGYWRYeTR0SXN4M1F1aGdlTERuV3JpdWNmNlB0WHQ2T2QramZQaEJqQ1kxTml6Y3BJSjdiWlhjOUZVNElYSktjVnd1WCtkaVNQVmJzeXo3QWtiWTI2cGE4cU85L3ZDd3hUUjRQQ3R4d2pHUnFsRC9iWU5wc3VrSGlPZVNZcWh4TTRmNURHMGJ2THZzbnhKTzlHVVdoZ1FybUt1aWtHMkoxWVh6Q0ExYnZIN3h5SnZZL1dram1IeXgveWJJb1NoT3MrL2pwQkdQeEdhcDVycXRIV3EyOWp0Zm8xbHVIU2N2SzJwUUlOdXdJejc3N3pnSkRtdjY5TWJadjh4RDhJSXA0SmdFaXkxSWNKeFZJaUpJL1ZjK0cwNko1YVV0alBkN2VMWllmSldjZ1N2N2FhZUpTWjVKZjVJL1R5MDQyWCt5dFN6N3FVeDRGL0d0T3VPbVRwTW1uYlhGUXA3NlhQeFhIQXN3NkI0L2loK2I2eEpHYkF4cVo1d3dnbVpzcnVNSXZaRGJaUHlwL3JOSElaNms1cVZ3M0Nua2tnbVFZQUgwY0YxSjZaQnRoZXplY3Bzak1tNWJxUnh2MjJFYWNDd1lzUkVOd2pHRWF1N2wyT1laMG1hUVZCT3pNU05TVjVadmZ4eUZiVENxU0tlVzJwc3hkclphN3RnY0dYK2ErNC9WY3lJZm1KMWlCRmpoSWgzQ3N5OExrTXYxczA3UTZSMjZyN0Y4MGYxZTZNWkxxQ1QyWVZkTzBaSnd4bjJZTUFQZC9EQkI0L0VCRm5zNjR3Wk03SzExbHFyZUxqMW5iWXpjZlR5b2pJQkJHWVJDMXpCdjhVU0pKSlY5T3RMUzAycXJRNTArUWR6SENiMWxJa2I4MlBkTnZiVE52QW1DQ2JsbThNTVhtYlM3Tkx0Z2Y3TVdrMmlmbVByWGdPK1JORVMxVHRWaE04NHhmQjQzb3pMZnBnRkpsekdUT3E5UUJCSjNYL1FHRERPVWk0UnhnZ1p4TWgwWjlTSlFPTVpMaE00R1plVTVEdTZTTHNUa3ZFK3dzdUFuNHZvdzFFa3R1T0NPY2FJTGVRKzhZbFArR1Vkdlppc01JTXlHWkhrZzMwNVk1UFNDaXVzNEplSjFXVm1vYjFNNkpTNnhNU0x4cDNxSHhOV25UYlM1MWkvcTdhVDlyQWtneTNpWXNRRTIydm1vRmc5Z3pyR3NyRVl3NlYrM0FobDJ1Q2cycEN2aDdFTFE0MVpDQkJrc0xEMHMxcUFKVEd4cU9EUUJvU0xxYktNOEw2eDVSNXpUWEhNb2MyempJdDNmQlFzSWdHZlVmbU16M3lqMHJvQnRBUEpuS2hGdEZ4U29EV2RXSDdBc2dqNlBXckVwRjYyT2J5MkdNeVVhTDFXczJHQ01GWHQzaE5sWmdUVGtKbUlQWlA3SVpZbWxFWEpkcXViQ1htWlpaYUpub2FHUXN4QnI4czBxQXhHU2R1WUFPdG91bHdmUzJRUUdzb0VXNmRkNGZwQmY1WnAyK0E0MVpNOUNSc3c2OGFJWjRLWnV4K0d5L3BiR0ZtS1dJUGRqd2FkcWpkMm5INlNUWXJJNmFJUXdMdkJraUcwZXN6S1J1MEkxQmZWMitzWjZXOGtLaUE1UXRNRHFKaUV0T09NOTNYVW1YU0gvUkJaTDh2YTZCUWhHTlVsSmxtV2o2UzBNQmpLSUFRdUpwS3lKU0RkMnMvMU0yZk9qSjZHa0VSZ0VGYVpYZ2tObjRrdXBUbDNxNCtKTTJYcVI2TmhncDFLRTIyMzlxWk0zNHg3ZkxlWTV1c1NHbkt2Vmd5eVk2VWl2R2xIM1kwMHVCYXJDTmFIVk9JUitrckNrQlREcDQ1QkV1OGF3bGRxUENBY3NCelBxQk9CaVdDNFNMdm5uSE9PMzBWbHFpWGZUc2lIZDRRY3YvUXo1VjhaM3AycjFiek9PdXQ0TFN4Mk5tMyswWTkrRlB1cDhqR1NXNkNKcFFoemR0RUVsam8zZFJ4ZkdrSUQybVFkUXNOUHBVakVENGZRa0lvVUxyc2ZUSUpzVzNXMWJ5SjdaOGkvSGlOTTNHVC9La3U4RUx0dW1NZXdac1FJN0REdmtubXJqTkFHWVJ3eHdpeWFDbXFMbmM4eHREbWVYWW9Rc3VwbXZpTkJERXVkVW1PT1o4TWE2bFIvVW0zcTV6anZHVUpHakJDc2FXOHNuaUoyL2lRZG13aUd5d1BsaFNDQXFxazdDU0Z0c2h2SnFQYVBsNCt0dkZMcjk5Z3hCb2JURDJHeVE5SlBtZGJJT01WazBBL0JzR0hjc1N4WjNlcEZLOXR0dDkyU3AyR0J1ZXFxcTVLL2Qvc0JmRk5hVU5tMU1HbDg1ekR0R1BGY0xyLzg4dGhQMDNJTTAzZUs0YUxsTVFhNkNkYjRPMU9DRGY1SGZLYTlFTXhPZS9VbUwrRzViTFhWVnNuZlV6K2dhU1BnOFd4VDFNOW1HcWs2dXgySDRUSldZMW8xd3NwR0cyM2tzOGwxcTJmU2ZwOFloc3VEWldDZWVPS0pYYVhmY1JzRURIbzBXM1plU1UwaTA5MG5Ka2w4cUNrTmsxMS8raldETTRuQ0dGSlpodEJjK2pIdEJRenh3Ykk5WEsvRUhxNHBMWWMyazh1NEh6OHA1bW9ZWjY5RTR2K1VDUkRHeFhJTU1uWDFRMkNQU1QvRjFLdldqWmJIdG40cFRSNUxDUWxmdWhGbTU3SjNwY3oxa2FxYmR6QWxOR0t5MzN6enpYMk1RZXI2MlBFbGwxelM3NGlVOHQ4U0hNbThWbWJPanRYYjd6SGVOY1lGMm5XUmVNY0pYcHlsVEg5RWl4dDFSMkJwblVKYUV4S3pOcTRvWk4xSkM5TDgzZ3pTY2hlbnBTOGorNXowQXJvOTl0akRTU3FPQWk3Tnptbloxa0RhcjN5N1RwTlE5RDRjdlBycXE1MGlXSlAzRWtOd1dsTFZkWHhJbzNFNzdMQ0QwMFNhckl0M1I5cVNXMmloaGR4Sko1M2tORWtsMnlWenBKUHZxN1F1VFdCTzhRakpPc0lQaHgxMm1GTjZ4dEs2cERrNUpSOXhFZ0tjbUUrNHRPTlRsaE1uODJCcFhWWG1DR1g3OHBqS2t1RjIybWtucHlBMko2M1B5ZWZzR0I5bGRmQzdHSzJUWmNGSktIRmlsQjN0REFla1pUcjZWbFlmdjRtQk9TMHRTdFlsdjZoVG9GUFhlb3IzNFJtbDhLVGQybGpGU1R0M0VrQzYxczM5dFRGODZGckhKL2RSamdHblFMelN1cFRtdHVQYWNFQUJscVhYRnZ1WC84NTlsWWdrMlYvdW9XeC9Uc3pYU1VEcStUN1VMeUhTajVIOGZjZm9mM2hvNTVaS09saWtSak5jSnR6enpqdlBNV21PTzhtTTZyVHZiYytEV1E5OHlxNUJHUGpXdDc3bHBDMUY0ZWFsbExsMUlPMWhjcWErRk1IY3l4aElWWVpML2RLbUhNeHQ1WlZYZHBMa0hkY0dYR1ZDZC9LSnV2ZTk3MzIrUFV6Z0tXSWlWZzdnMXJXaGp1Sm5WWWFyNEN0Mzhza25PNlhQOUV3TnBoL3FvbDN5SVR2dEN1Um16NTd0RktDVmFwWS9mc3d4eDdTdURYWFUrZFNTcmRaOXBNMDdCSXpUVGp2TjkxdFdCOCtBRVpaZ3dreXlDQXd5Mnp0Rm5UdHQ3TzZPUFBKSXA2ME5TOTlaK3FLRUdKWGF5emo1eWxlK1Vzb3NZTWhnU0xzUVRtZ1RncUdXZFNYdmdRQ200TDlXWDR2L3lCcmxHVDE5VXFCYlZOamdmZEV1VjA3NzV4WXZiMzFIWWJqa2trc3FDUVhEWXJpTUExbDduTGIvTEgwdTBvU2Q5aTMyZ2diUEYyR2pLR1R4N3NqZDVKKy9Bc1RjZXV1dDUvYmVlMjh2L0NvWU1JbDNuYkU0aGRkME1OekdMd3NTdUIxRU5PZ25QL2xKYjViQ0h6ZXVoRG1KL0xMc0p6cktSSVFsL2xPOVZORm00Z3RLbVlHakY1UWMxSXlVWVo3ZVpKTk5vbWV4TEljQW9kVGVyOUdMRWdmeFZlMjU1NTdlcDB2QURENWtnblZvQTZZMGNqaUxHWHQvcnlhWVJDMlpUMVhJMnVsQkVlYldiYmZkTmx0bGxWVzhLWmhFRVVSdjQyZkU3TXdTS1hacklxb1pmMldLQ0VKakRYdS9oQjh5LzU2eFJoWnNLSmptaVlCbUpRRitRZDVOWENSY1F6L3dmYktHVlZhQzBzaGhyaUdHZ2FWbFZZaG54RFBEekl1NU8wWml0ajZKQTZaVFROVmdoV2tZY3lwYkI4YUk4ejcvK2MvN2R0Ty9JbEVIMGVEMDUrS0xMODVrY2ZGcjVqRnhnd3V4QVR3M3hpaExpV0pFMjltKzhmampqL2YrNnRnNVUzV013Q215K2RGbnNJa1IvVGppaUNQOHZ0ekVtRHlnSlZSa0FRUkhDRXg0bDhDRU9BYzJ6OERGSVlIVjc3TEUvRENxZVFWaS9hMXpyTkVhcmdEeFpnbzBFL2svTkg3SGp6Ukp1YTIzM3Jxck9ZbStUbWRCa2tWN1M1bVQ5ZUk1UlhCMlNMejl0Qm5UTEZwZWpOQ3lOZEY1N1NKMmoyNGFMdlhHVElab3FXaXhhTkFVTGRHSzNiN2pHTm9CV2x5c0xjVmpaUm91V3FQOGVCMmFCbFljam92aE9yQkdLNjlDWXRKT2ZpcUt0d0FBQ3RWSlJFRlVrMzZsZGhYYldmeXVRRFVuQmxIbHRyWE80WmxpR2tVekttcE94YmJrdjZPNThoNzFTcmdzOHZVVS8wZURreURodENhK3RHcTBYVEVmSjUrelUreUJ1L2JhYTcwN0pEVjJRMldNcisyMjI2NnltWGFZR2k1OTE1STdwM1Nib1hsZFAra2Yxb2p3cmpBMmVYZGlyZ0pGWHp2bFVDakZ1NGovQ0gzdjBIRFZ0aWcxbnVHcTF3N3ptcVJOTjJmT25LNkRwT29KdlB4YVJ1RW5HRXdwa3VpY0FpbTYrZ1NyMXM5NVd1VHVwTUg0Z1U0L1JybGdLc2E4bVRMZjQ5T1NORHZRUHVERGs2YVRoQlJtQXBPUDRkYU40V3IzSmFmVWRVNVI3OG42cS82Z2FGcTMyV2FiUmRzUmExc1p3MlZ5VjBDZ0gydFY3NTg2RDcvdHBwdHVXcmxkc2JibWoyRk9oT2tQZ3hBMHRQYmN5WUxTWnRMUDN6LzFQK01FbDBDdmhCdW5HMlBIdEx6bGxsczZudkVnQ1NhbENPRFNPSVJpZjRmTmNMa2ZQbkg4eVRGaHRKLys4M3hseFJ0WFAyNEh3NTJvS0dVTmpEWmkrUWdSZmdybzhXWklNY3UyMzZ0K3dUUWlmMHBHdEtkOE05Nk1TQmcvWmlFaU00bllJMkgvWG52dGxiR3BRTGMxZ21YM3hUeUlPVnd2MGNqa3RpMXJyN1FJYnhwTG1WUXg3ZFpKOUZCMlQweW41RTFPRVpIQ3JCT3NRNWorNVB2TVRqLzk5RHFYdDY1aDZjbysrK3pqTjB4dkhlempIeEpleU9lWHllZmFSeTJaTjFYdXUrKyszdHpaVjBXNWkzay9NUGtPbWpCTFlxb2tNaHRUcFRTa25tN0JPSkZ2T0NOTlpDK0VDVHJsSGduMThJNnpGN1dFallHNEw2Z1hFN2hpQW56bVBHbUo0VllqOFlrN0FQZkQ3cnZ2UHRDbGliZ1ZjRW5oQ21reVRZU0dxd2ZZa3VJSllDRGlEbTAwWnRySVMybVlncFFFd0duM0dTY20yN09HUmdER3JydnU2c1JzdkdtbG0xVEkvWWhPSmNobFVORzgrYjRQNjM4c0NOdHZ2NzAzNzRKcHZxRHhZbWF1R3VUU2F4dmxvL1JXaGZ3OXcvL2NtNEFVZ29lSzlYYlRjT1hYZFBLeCtldkVtTHlabHVkSG5XWEU3MGpybURDUFBmWllIMUJWdkhlMzcyVWFMbHFwY2d2N2RtR0NrMi9ObTdYcGN6ZWkvVnFPNURWRmdtQzZ0YVBPNzBUY2Z2V3JYL1hqR1BPaG1IQlh6SXJ0NWozQWVxVEVGazZUdXcvWXFkT1c0alc0SUJnUGFPRlY4T0k1ZG9zTXp0K0RJRTJDdnNBWVYwT1ZlOUIzeGd6OVJVdEd5K3NXZVo2L1ovNy9FQ0FheG4vNHBINmlvUFBuRHVKLytkemQwVWNmN1MxeDlMZmJ1MUY4emdTRThTekFpemx5eHgxM1RMcUFCdEhlSWRiUm9lR21JeWJVaWtraXN1akl2SlNoUWJKQW5YV2pMSDRueUVZRHdpK2sxeUR3Mmhocnp6U0l2UmFRU2lWWWhoMlNPUUVQcEpza2dFSVJvMTZLWTFjYlVoQ2lyUkEwZ21aQUVBWkJHK3pBUVNZbTJqSXVoQ1pBZjFnWG1aZkkwWGJSRUI1ODhNSG9PcjVCOUk5RUlGcUs0NThqV21tZ2NHOHk4eERrUVZhaVhnajh3elBRcE9LZnlSWmJiT0UxWmdLbENQNlFvTkZLM280VmhiNHpUZ2lRVWJSMlJqRFNvRW1UV3F2S004ODgwMk5PUUpKTTV6NFloWVFqUVRQalhOb0ZMbVNSWXR2Q004NDR3MXQ3OHZXMEtoekFQN3d6bWpoOTRwRTExMXpUcjBjbENRbnJTd2tXb2pBbUNLQUoxaEFzVHJ3RDRNZDdRTnBMRXFSZ1RlbzNKM2ErUzR5VldWb3pTcUFabGloU0U3TGVGKzBLRW9QeUdqcHRrYkRnQTNsNjBkaHAvMzc3N2VmVHJoTE1Gd0xwU01kSnY3a1BmUVo3NmhWRDkvMGx1SWkrTXRmMGs5Q0dvRXJldytJN3lIMng4QTJhQ0lKVGhMSHZMMVkrbmpmQllMU0IvdktNZzRVZ1lFdS9TVTFMb2ErMFdlNGJiMzNnMlRlRlVxR1RhTGczcUx5a0tSM3RwUis4Q0VRb0VsMUg1QnlEQXJNbkE0bVhIdE1PekhkUXhNRG5KY2Qwd3Nic3ZPd01TQ1pEb3ZOZ1dIbW1NYWo3RHJzZWhBWVlFSDBCdzhDb3VDKy9jV3lRT0JiN0E0TkJZQ3E2Q3BqY3VEOFRHNHduVDdTVi9WYVpJQkY4aWdTemxIVWlVNEJMNnlmT0k1cVdTR3crRWRTWVZLaWJad2h6SjRJWkFhTWZoZ1pUd0lUS0dDa1NkWC8wb3gvMTVzYndHMzFFQ0dCM0lzWVg3UUlUeGhLNGsyU0R5YTJPT1RiY28rNG5tTkUyelB0TXhrSFlSRmpoTjhZR2t5K0NNTWtrWUQ0d3hqelRxSHZ2MUhYZ0JiYmh2UWN2eGdyM3BDMllUY01jd05pcFN3Z1pqQlhjTFl3WEJELzZEVVBIRkMwL3JSOHZDUCtNbjM0cE1QWGllOEFZNVo3OTlLVksyNWpQRUs1bUtPcVlLR1RtQk1aaEVQd1lpL1NiOFVqaGZlbEZvS25TaG1rNmgwR3lnc3B0M2U0L2NTWmxBZEpoV3RITDVnT3JOREM3QmtuRXJyZGpuWmlPT2laaXVLV0pMeVI1KzNXMzA5RVBNZHhrNGd0TTFjR2tQQjF0czN2Mk45YVphd3pEL2pBY1Fmek1wS3lIVXBuUXlJb2FVT1dMN1VSRHdCQXdCQ29pa0xmK1ZMekVUaHREQkNZNlNua01uNWMxMlJBd0JBd0JRMkJNRVVneFhIeTc0eE9kTTZiZ1c3TU5BVVBBRURBRUpnZUJGTU5sUWVyZ0Y4NU5EcTdXVTBQQUVEQUVESUhKUmdBZTJzWkhVd3lYVmRXanRiSjZzaCtjOWQ0UU1BUU1BVU5ndkJBZ2FPci8xeVRxUzRyaHdwV2ZHSysrV1dzTkFVUEFFREFFRElHUlFRQWVXa25ESlVmYW95UFRiR3VJSVdBSUdBS0dnQ0V3WGdnOG91YTI1UnN0MDNBZkhLKytXV3NOQVVQQUVEQUVESUdSUWVCaHRlVFpQUWovMWFRVXc4WHVmS3VLUlNyL0N5ajdNQVFNQVVQQUVEQUVLaUlBNzd4WnBSTEQ1YVRyVlg2dlltUUlUQlFDcFBpanhJalVqNVRwb0h3TzJ1TDkrUzNWNXVLNTl0MFFNQVNHanNBZmRZZWZxclF4M05UbUJXUkN4NlRNQmV1cUdCa0NFNE1BZVYzdnUrOCszOTk4QmlEeTZtb2YzR25MODBwT1gzSW1rMSszMkM3YWJGblJKbWFJV2tkSEg0RWIxVVRpb05xc3hDbUdTM2QrcThKV0VtdXBUSTlJcnhzYkdRSlRpUUFKMWRsWGxzMEdvRHhqUTRNa21mN2RkOTg5bFUxcTNldktLNi8wbTJpUTNEKy9DUUtDQUVubzJWVER5QkF3QktZZEFRS2w0SjBkVzVHbGRndWl4ZnkydHNxSktvdXJHQmtDaG9BaFlBZ1lBb1pBT1FKSTZ6dXJYS3JTcHVIR0hWWFBWc2FKYkN0MFJmR2laMysydjRhQUlXQUlHQUtHZ0NHUVF3QytDYy9FcE56R2JEbW5qT0h5T3pib2kxVHU1NHVSSVdBSUdBS0dnQ0ZnQ0NRUmdGZkNNd21hNnFCdURCY09mYjdLQlNya1Z6WXlCQXdCUThBUU1BUU1nVTRFL3F4RDhFcDRab2QyeStsVmdxR0lXR1lCN3pJcUMxYThScWNaR1FLR2dDRmdDQmdDRTRQQXRlcnBRU29FSEVlcENzUGxRaXBnVGU3cUtxOVVNVElFREFGRHdCQXdCQXlCWnhINHBUNE9WN215REpDcURKYzY3bEhCcDd1aFN0bHlJdjFzWkFnWUFvYUFJV0FJVEFRQzdLeTNpOHJaM1hyYkM4T2xMcGp1QzFSV1Vlbm0vOVVwUm9hQUlXQUlHQUtHUUdNUllNM3RVU3FucUxSdFZCRHJjYThNbDhDcG42amcxMTFlQmVaclpBZ1lBb2FBSVdBSVRCb0NhTFl3MjVOVi9sQ2w4NzB5WE9wa1k0UHJWQjVUV1VMbFZTcEdob0FoWUFnWUFvYkFKQ0RBSHJmNGJBOVRPVTRGWGxpSjZqQmNLdWFHTjZrOHBQSmFGWmp1aTFTTURBRkR3QkF3QkF5QnBpTHdkM1hzR3BVRFZNNVM0WHRscXN0d3VRSHJqTzVRUWR0OWpzcThLa1F3ODcrUklXQUlHQUtHZ0NIUUZBVGdkL2Vybks1eWhNclZLaHpyaWZwaHVPRkdMQmNpRlBvQmxiK3F2RlRsNVNxRHFGdlZHQmtDaG9BaFlBZ1lBdE9DQU5iY2UxVklabkdDQ3NGUnYxYXBSWVBVUm9sYW5sdmxyU29ycTZ5ajhtYVZWNmdZR1FLR2dDRmdDQmdDNDRMQW45UlEzS1pYcUpEUTRuYVZSMVFJR0s1TmcyUzRvUkV3WHJUYytWVVdWbGxCWlNtVlJWWHc5NzVFNWNVcUwxVHBXU1hYTlVhR2dDRmdDQmdDaHNBZ0VFQ0RKZG9ZNnl6V1dzekc3TDk1bFFxYUxFejJMeW9ENFZYRFlMaHFXNHVvbjJBcW1PdGNLcGlaV1VvRTB6V0dLeENNREFGRHdCQXdCS1lGQWZnVERQZkpmMzJ5anBidnJNU2hESVRKcWg0alE4QVFNQVFNQVVQQUVEQUVEQUZEd0JBd0JBd0JRNkJoQ1B3ZmUwOXZaTmE5clpNQUFBQUFTVVZPUks1Q1lJST0iCiAgLz4KPC9kZWZzPgo8L3N2Zz4=%0A%20%20%20%20%20%20%20%20"
          alt="App Image"
        />
      </section> -->

      <footer style="margin-top: 50px">
        <p>Copyright &copy; 2023</p>
        <p style="font-weight: bold"><span>PortfolioOne</span></p>
      </footer>
    </div>
  </body>
</html>

        '''
        message.html = html_content
        mail.send(message)
        
        return jsonify({'Message': 'Password reset email sent successfully', 'status': 200})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/addLeaseData/upload', methods=['POST'])
@token_required
def upload():
    try:
        data = request.get_json()
        auth_header = request.headers.get('Authorization')
      # Get the token by removing 'Bearer ' from the header
        token = auth_header.split(' ')[1]
        
        # Assuming `token` holds the JWT token you received or retrieved
        decoded_token = jwt.decode(token, "PortfolioOne", algorithms=['HS256'])

        # Access the 'user_id' from the decoded token
        user_id = decoded_token.get('user_id')

        # Ensure data is a list of dictionaries
        if not isinstance(data, list):
            return jsonify({'error': 'Data must be an array of lease records'}), 400

        # Create a database connection
        connection = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['db']
        )

        if connection is None:
            result = {
                'status': 500,
                'Message': 'Failed to connect to the database'
            }
            return jsonify(result)

        cursor = connection.cursor(dictionary=True)

        success_count = 0
        error_count = 0

        for lease_record in data:
            try:
               # Generate a UUID for lease_id
                lease_record['lease_id'] = str(uuid.uuid4())
                lease_record['user_id'] = user_id
                # Ensure that required fields are present in each lease record
                required_fields = ['lease_id']  # Add or modify as needed
                for field in required_fields:
                    if field not in lease_record:
                        error_count += 1

                insert_fields = ', '.join(lease_record.keys())
                insert_values = ', '.join(['%s' for _ in lease_record.values()])
                query = f"INSERT INTO lease_data ({insert_fields}) VALUES ({insert_values})"
                insert_data = tuple(lease_record.values())
                cursor.execute(query, insert_data)
                connection.commit()

                success_count += 1
            except Exception as e:
                error_count += 1
                print(e)

        cursor.close()
        connection.close()

        result = {
            'success_count': success_count,
            'error_count': error_count,
            'Message': 'Lease data insertion completed',
            'status': 200
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/feedback', methods=['POST'])
@token_required
def addFeedback():
    try:
        data = request.get_json()
                # Validate the 'category' field
        allowed_categories = ['Feature requests', 'Bug reports', 'Questions', 'Reviews', 'Others']
        if 'category' not in data or data['category'] not in allowed_categories:
            return jsonify({'error': 'Invalid or missing category'})

        # # Generate a UUID for feedback
        # generated_uuid = str(uuid.uuid4())

        # # Update the data dictionary with the generated UUID
        # data['id'] = generated_uuid

        data['user_id'] = g.user['user_id']
        
        # return jsonify({'msg': g.user.user_id})

        # Create a database connection
        connection = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['db']
        )

        if connection is None:
            result = {
                'status': 500,
                'Message': 'Failed to connect to the database'
            }
            return jsonify(result)

        cursor = connection.cursor(dictionary=True)

        # Insert data into the database dynamically
        try:
            insert_fields = ', '.join(data.keys())
            insert_values = ', '.join(['%s' for _ in data.values()])
            query = f"INSERT INTO feedbacks ({insert_fields}) VALUES ({insert_values})"
            insert_data = tuple(data.values())
            cursor.execute(query, insert_data)
            connection.commit()

            result = {
                'status': 200,
                'Message': 'Feedback data inserted successfully'
            }
        except Exception as e:
            result = {
                'status': 500,
                'Message': str(e)
            }
        finally:
            cursor.close()
            connection.close()

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500



import requests
import base64
import json

# Your PayPal sandbox credentials
PAYPAL_CLIENT_ID = "ATzX2fzuRpxCD_N3oJgY_JD82V6vVvmKnIeVuK63EKBdNbVz1wJD-6hubdvOljeI-kI-VvuVr0hsKeN-"
PAYPAL_CLIENT_SECRET = "ELaiJVAy7n4T84kmKI6IStopS_GOzd82JjKD1-t54sup0BTjBczv7Y8QwuWkiQunsc7MggOeR3eVTkLj"
PLAN_ID = "P-27310851BE4578012MWNZWRQ"


base_url = "https://api-m.sandbox.paypal.com" #
mode = "sandbox" #live

# Parse post params sent in body in JSON format
app.use_json = True

def generate_access_token():
    """Generates an OAuth 2.0 access token."""
    auth_string = f"{PAYPAL_CLIENT_ID}:{PAYPAL_CLIENT_SECRET}"
    encoded_auth = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")
    headers = {"Authorization": f"Basic {encoded_auth}"}
    response = requests.post(f"{base_url}/v1/oauth2/token", headers=headers, data="grant_type=client_credentials")
    response.raise_for_status()
    return response.json()["access_token"]
  
def create_subscription(user_action="SUBSCRIBE_NOW"):
    """Creates a subscription for the customer."""
    url = f"{base_url}/v1/billing/subscriptions"
    access_token = generate_access_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Prefer": "return=representation",
    }
    data = {"plan_id": PLAN_ID, "application_context": {"user_action": user_action}}
    response = requests.post(url, headers=headers, json=data)
    return response.json(), response.status_code
  
def handle_response(response):
    try:
        json_response = response.json()
        return {"jsonResponse": json_response, "httpStatusCode": response.status_code}
    except Exception as error:
        error_message = response.text
        raise Exception(error_message)

@app.route("/api/paypal/create-subscription", methods=["POST"])
def create_subscription_endpoint():
    """Endpoint for creating a subscription."""

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        # user_id = g.user['user_id']
        user_id = 99
        
        json_response, http_status_code = create_subscription()
        print(json_response['id'])
        subscription_id =json_response['id']
        if subscription_id:
          delete_query = "DELETE FROM subscriptions WHERE user_id = %s"
          cursor.execute(delete_query, (user_id,))
          insert_query = "INSERT INTO subscriptions (user_id, subscription_id) VALUES (%s, %s)"
          cursor.execute(insert_query, (user_id, subscription_id))
          connection.commit()
        return jsonify(json_response), http_status_code
    except Exception as e:
        print("Failed to create order:", e)
        return jsonify({"error": "Failed to create order."}), 500
    finally:
      cursor.close()
      connection.close()
    

@app.route("/api/webhook/paypal", methods=["POST"])
def paypal_webhook():
    webhook_event = request.get_json()
    handle_webhook_event(webhook_event)
    return jsonify({"status": "Webhook received and processed"})


def handle_webhook_event(event):
    try:
        event_type = event["event_type"]
        resource = event["resource"]

        connection = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['db']
        )
        cursor = connection.cursor(dictionary=True)

        if event_type == "PAYMENT.SALE.COMPLETED":
            subscription_id = resource["billing_agreement_id"]

            # Check if the subscription already exists
            subscription_query = "SELECT * FROM subscriptions WHERE subscription_id = %s"
            cursor.execute(subscription_query, (subscription_id,))
            existing_subscription = cursor.fetchone()

            if existing_subscription:
                # If the subscription exists, update the end_date if start_date is the same
                if existing_subscription["start_date"]:
                    update_query = "UPDATE subscriptions SET end_date = NOW() + INTERVAL 30 DAY WHERE subscription_id = %s"
                    cursor.execute(update_query, (subscription_id,))
                else:
                  update_query = "UPDATE subscriptions SET start_date = NOW(), end_date = NOW() + INTERVAL 30 DAY WHERE subscription_id = %s"
                  cursor.execute(update_query, (subscription_id,))               


        else:
            print("Ignoring non-subscription event:", event_type)

    except Exception as e:
        print("Error handling webhook event:", str(e))
    finally:
        cursor.close()
        connection.close()
     
     

# API to update role permissions
@app.route('/api/updateRolePermissions', methods=['POST'])
@token_required
def updateRolePermissions():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        data = request.get_json()
        role_id = data['roleId']
        org_id = data['orgId']
        permission_ids = data['permissionID']

        # Delete existing role permissions
        checkPermission = "SELECT * FROM role_permissions WHERE role_id = %s AND org_id = %s"
        cursor.execute(checkPermission, (role_id, org_id))
          # Fetch the result after executing the query
        checkPermissionExist = cursor.fetchall()
        if checkPermissionExist :
            # Delete existing role permissions
            delete_query = "DELETE FROM role_permissions WHERE role_id = %s AND org_id = %s"
            cursor.execute(delete_query, (role_id, org_id))

        # Insert new role permissions
        insert_query = "INSERT INTO role_permissions (role_id, org_id, permission_id) VALUES (%s, %s, %s)"
        for permission_id in permission_ids:
            cursor.execute(insert_query, (role_id, org_id, permission_id))

        connection.commit()

        result = {
            'status': 200,
            'Message': 'Role permissions updated successfully'
        }
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()





# API to get permissions
@app.route('/api/getPermissions', methods=['GET'])
@token_required
def getPermissions():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM permissions")
        permissions = cursor.fetchall()

        result = {
            'status': 200,
            'data': permissions,
            'Message': 'Permissions retrieved successfully'
        }
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

        
# API to get roles
@app.route('/api/getRoles', methods=['GET'])
@token_required
def getRoles():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM user_roles")
        roles = cursor.fetchall()

        result = {
            'status': 200,
            'data': roles,
            'Message': 'Roles retrieved successfully'
        }
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()


# Function to fetch permissions based on org_id
@app.route('/api/getPermissionsByOrgId/<int:org_id>', methods=['GET'])
@token_required
def get_permissions_by_org_id(org_id):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # SQL query to fetch permissions based on org_id
        query = "SELECT role_id, GROUP_CONCAT(permission_id) AS permission_ids FROM role_permissions WHERE org_id = %s GROUP BY role_id"
        cursor.execute(query, (org_id,))
        permissions = cursor.fetchall()

        formatted_permissions = []
        for permission in permissions:
            formatted_permission = {
                'org_id': org_id,
                'role_id': permission['role_id'],
                'permission_ids': [int(id) for id in permission['permission_ids'].split(',')]
            }
            formatted_permissions.append(formatted_permission)

        return {'data': formatted_permissions, 'status': 200}

    except Error as e:
        return jsonify({'error': str(e)}), 500

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()



@app.route('/api/updateUserHeadcount/<int:user_id>', methods=['PUT'])
@token_required
def update_user_headcount(user_id):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        data = request.get_json()
        user_id = g.user['user_id']
        headcount_values = data
        
        if g.user['user_id'] != user_id:
          return jsonify({'msg': 'User is not authorized'})

        # Update headcount values for the specified user
        update_query = "UPDATE user_headcount SET headcount1 = %s, headcount2 = %s, headcount3 = %s, headcount4 = %s WHERE user_id = %s"
        cursor.execute(update_query, (headcount_values['headcount1'], headcount_values['headcount2'], headcount_values['headcount3'], headcount_values['headcount4'], user_id))

        connection.commit()

        result = {
            'status': 200,
            'Message': 'User headcount updated successfully'
        }
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/getUserHeadcount/<int:user_id>', methods=['GET'])
@token_required
def get_user_headcount(user_id):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        if g.user['user_id'] != user_id:
          return jsonify({'msg': 'User is not authorized'})

        # Retrieve headcount values for the specified user
        select_query = "SELECT * FROM user_headcount WHERE user_id = %s"
        cursor.execute(select_query, (user_id,))
        user_headcount = cursor.fetchone()


        if user_headcount:
            result = {
                'status': 200,
                'data': user_headcount,
                'Message': 'User headcount retrieved successfully'
            }
        else:
            result = {
                'status': 404,
                'data': {},
                'Message': 'User headcount not found'
            }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')