from flask import request, json, jsonify, Flask,g
import pandas as pd
from sqlalchemy import create_engine,text
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import mysql.connector
from flask_mail import Mail, Message
from twilio.rest import Client
import random
import datetime
import jwt
from functools import wraps
from Crypto.Cipher import AES
import base64




# from logger import logging

# logger = logging.getLogger()

app = Flask(__name__)
CORS(app)

db_config = {
    'host': 'api.portfolioone.io',
    'port': 3306,
    'user': 'portfolio',
    'password': 'PortfolioOne!@#',
    'db': 'dfx'
}


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

# @app.route('/rough', methods=['POST'])
# def rough():
#     try:
#         data = request.get_json()
#         number = data.get('number')
#         print(type(number))
#         return jsonify({'message': 'Rough'}), 200
#     except mysql.connector.Error as e:
#         return str(e)


@app.route('/getAllLeaseData', methods=['GET'])
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

        query = "SELECT * FROM lease_data"
        cursor.execute(query)

        data_list = cursor.fetchall()

        cursor.close()
        connection.close()

        result = {
            'status': 200,
            'data': data_list,
            'Message': 'Request Submitted Successfully',
            'count': len(data_list)
        }

        return jsonify(result)

    except mysql.connector.Error as e:
        return str(e)

@app.route('/getAllLeaseDataByUser/<string:id>', methods=['GET'])
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
        cursor = connection.cursor(dictionary=True)
        # SQL query to fetch data based on the provided ID
        query = f"SELECT * FROM lease_data WHERE user_id= '{id}'"
        # Use pandas to read data into a DataFrame
        cursor.execute(query)
        # Convert the DataFrame to a list of dictionaries
        data_list = cursor.fetchall()

        cursor.close()
        connection.close()

        result={
            'status':200,
            'data':data_list,
            'Message':'Request Submitted Successfully',
            'count':len(data_list)
        }

        return jsonify(result)

    except Exception as e:
        return str(e)

@app.route('/validateUser', methods=['POST'])
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
        data= request.get_json()
        username=data['email']
        password=data['password']
        # SQL query to fetch data based on the provided ID
        query = f"SELECT email,fullname,mobile,organisation,user_id FROM user_details WHERE email= '{username}' AND password='{password}'"
        # Use pandas to read data into a DataFrame
        cursor.execute(query)
        # Convert the DataFrame to a list of dictionaries
        data_list = cursor.fetchall()

        cursor.close()
        connection.close()
        # Generate a JWT token upon successful user validation
        payload = {
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)  # Token expiration time
        }
        token = jwt.encode(payload, "PortfolioOne", algorithm='HS256') #[1]->secret key 
        if data_list==[]:
            result={
            'status':404,
            'data':[],
            'Message':'User not found'
            }
        else:
            result={
            'status':200,
            'data':data_list,
            'Message':'User found',
            'token':token
            }
        return result


    except Exception as e:
        # logger.error(e)
        return str(e)


@app.route('/RegisterUser', methods=['POST'])
def RegisterUser():
    try:
        data = request.get_json()
        name = data['fullname']
        email = data['email']
        mobile = data['mobile']
        password = data['password']
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
        query = "SELECT * FROM user_details WHERE email=%s OR mobile=%s"
        cursor.execute(query, (email, mobile))
        existing_user = cursor.fetchone()

        if existing_user:
            result = {
                'status': 500,
                'Message': 'User already exists'
            }
        else:
            insert_query = "INSERT INTO user_details (fullname, email, mobile, password, organisation) VALUES (%s, %s, %s, %s, %s)"
            insert_data = (name, email, mobile, password, organisation)
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
        connection.close()

    return jsonify(result)







@app.route('/addLeaseData', methods=['POST'])
@token_required
def addNewLeaseData():
    try:
        data = request.get_json()

        # Ensure that required fields are present in the JSON data
        required_fields = ['lease_id']  # You can adjust the list of required fields
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

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





# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465  # Use the appropriate port (587 for TLS)
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True   
app.config['MAIL_USERNAME'] = 'reddysainath47@gmail.com'
app.config['MAIL_PASSWORD'] = 'jxyhiqscawrnbntw'  # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = 'reddysainath47@gmail.com'


mail = Mail(app)


# @app.route('/send-otp', methods=['POST'])
# def send_otp():
#     try:
#         data = request.get_json()
#         mobile_number = data.get('mobile_number')
#         email = data['email']

#         # Check if both mobile_number and email are provided
#         if not mobile_number or not email:
#             response = {
#                 'status': 400,
#                 'message': 'Both mobile_number and email are required.'
#             }
#             return jsonify(response)

#         # Create a database connection
#         connection = mysql.connector.connect(
#             host=db_config['host'],
#             port=db_config['port'],
#             user=db_config['user'],
#             password=db_config['password'],
#             database=db_config['db']
#         )

#         if connection is None:
#             response = {
#                 'status': 500,
#                 'message': 'Failed to connect to the database'
#             }
#             return jsonify(response)

#         cursor = connection.cursor()

#         # Query the database to check if a user with the provided email and mobile number exists
#         query = "SELECT * FROM user_details WHERE email=%s OR mobile=%s"
#         cursor.execute(query, (email, mobile_number))
#         existing_user = cursor.fetchone()

#         if existing_user:
#             response = {
#                 'status': 400,
#                 'message': 'User already registered. Please log in.'
#             }
#             return jsonify(response)

#         # Generate a random 4-digit OTP
#         otp = ''.join(random.choice('0123456789') for i in range(4))

#         # Create an email message
#         msg = Message('Your OTP Code', recipients=[email])
#         msg.body = f'Your OTP code is: {otp}'

#         # Send the email
#         mail.send(msg)


#         # Send the OTP to the mobile number (Twilio SMS)
#         # message = f'Your OTP is: {otp}'
#         # account_sid = 'ACd385449272c77d3c5442bc12caa32c5e'
#         # auth_token = 'cee34d164876e14591b7931c6bc650f0'
#         # client = Client(account_sid, auth_token)

#         # client.messages.create(
#         #     to=f'+91{mobile_number}',
#         #     from_='+12512208257',
#         #     body=message
#         # )

#         response = {
#             'status': 200,
#             'message': 'OTP sent successfully',
#             'otp': otp
#         }

#         return jsonify(response)

#     except Exception as e:
#         return str(e)



def create_otp_entry(connection, user_id, otp):
    # Create an entry in the otp_data table
    try:
        cursor = connection.cursor()
        insert_query = "INSERT INTO otp_data (user_id, otp) VALUES (%s, %s)"
        cursor.execute(insert_query, (user_id, otp))
        connection.commit()
        cursor.close()
    except Exception as e:
        raise e
    



# Encryption
def encrypt_data(data, key):
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC)
    padding_length = AES.block_size - (len(data) % AES.block_size)
    if isinstance(data, int):
        data = str(data)  # Convert to string if it's an integer
    padded_data = data.encode('utf-8') + bytes([padding_length] * padding_length)  # Convert to bytes
    ciphertext = cipher.encrypt(padded_data)
    return base64.b64encode(ciphertext).decode('utf-8')

# Your secret key (must match the key used in Swift)
key = 'secret key 12345'

# Data to encrypt
data_to_encrypt = '1234'

# Encrypt the data
encrypted_data = encrypt_data(data_to_encrypt, key)

print(encrypted_data, "encrypted_data")



@app.route('/forgot-password-send-otp', methods=['POST'])
def forgotPasswordSendOTP():
    try:
        data = request.get_json()
        mobile_number = data.get('mobile_number')
        email = data['email']

        if not mobile_number or not email:
            response = {
                'status': 400,
                'message': 'Both mobile_number and email are required.'
            }
            return jsonify(response)

        # Create a database connection
        connection = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['db']
        )

        if connection is None:
            response = {
                'status': 500,
                'message': 'Failed to connect to the database'
            }
            return jsonify(response)

        cursor = connection.cursor()

        # Query the database to check if a user with the provided email and mobile number exists
        query = "SELECT * FROM user_details WHERE email=%s OR mobile=%s"
        cursor.execute(query, (email, mobile_number))
        existing_user = cursor.fetchone()

        if not existing_user:
            response = {
                'status': 400,
                'message': 'User not registered, please sign up.'
            }
            return jsonify(response)

        # Generate a random 4-digit OTP
        otp = ''.join(random.choice('0123456789') for i in range(4))

        # Create an email message
        msg = Message('Your OTP Code', recipients=[email])
        msg.body = f'Your OTP code is: {otp}'

        # Send the email
        mail.send(msg)

        # Save the OTP and user ID in the database
        user_id_query = "SELECT user_id FROM user_details WHERE email = %s"
        cursor.execute(user_id_query, (email,))
        user_id = cursor.fetchone()

        if user_id:
            user_id = user_id[0]
            # Create an entry in the otp_data table
            create_otp_entry(connection, user_id, otp)

            response = {
                'status': 200,
                'message': 'OTP sent successfully'
            }
        else:
            response = {
                'status': 400,
                'message': 'User not found'
            }

        cursor.close()
        connection.close()

        return jsonify(response)
    except Exception as e:
        return str(e)








@app.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        email = data['email']
        otp = data['otp']
        new_password = data['new_password']

        if not email or not otp or not new_password:
            response = {
                'status': 400,
                'message': 'Email, OTP, and new password are required.'
            }
            return jsonify(response)

        # Create a database connection
        connection = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['db']
        )

        if connection is None:
            response = {
                'status': 500,
                'message': 'Failed to connect to the database'
            }
            return jsonify(response)

        cursor = connection.cursor()

        # Verify if the OTP matches the latest one stored in the database
        # You can retrieve the latest OTP based on the user's email
        query = "SELECT otp FROM otp_data WHERE user_id = (SELECT user_id FROM user_details WHERE email = %s) " \
                "ORDER BY created_at DESC LIMIT 1"

        cursor.execute(query, (email,))
        result = cursor.fetchone()
        print(result, "result")

        if result and result[0] == otp:
            # Update the password in the user_details table
            update_query = "UPDATE user_details SET password = %s WHERE email = %s"
            cursor.execute(update_query, (new_password, email))
            connection.commit()

            # Clean up the used OTP
            delete_query = "DELETE FROM otp_data WHERE user_id = (SELECT user_id FROM user_details WHERE email = %s)"
            cursor.execute(delete_query, (email,))
            connection.commit()

            response = {
                'status': 200,
                'message': 'Password reset successfully'
            }
        else:
            response = {
                'status': 400,
                'message': 'OTP verification failed'
            }

        return jsonify(response)

    except Exception as e:
        return str(e)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')




# from Crypto.Cipher import AES
# import base64

# # Encryption
# def encrypt_data(data, key):
#     cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC)
#     padding_length = AES.block_size - (len(data) % AES.block_size)
#     if isinstance(data, int):
#         data = str(data)  # Convert to string if it's an integer
#     padded_data = data.encode('utf-8') + bytes([padding_length] * padding_length)  # Convert to bytes
#     ciphertext = cipher.encrypt(padded_data)
#     return base64.b64encode(ciphertext).decode('utf-8')

# # Your secret key (must match the key used in Swift)
# key = 'secretkey1234567'

# # Data to encrypt
# data_to_encrypt = 'Sainath'

# # Encrypt the data
# encrypted_data = encrypt_data(data_to_encrypt, key)

# print("Encrypted data:", encrypted_data)

# # Decryption
# def decrypt_data(encrypted_data, key):
#     cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC)
#     ciphertext = base64.b64decode(encrypted_data)
#     decrypted_data = cipher.decrypt(ciphertext)
    
#     # Remove padding
#     padding_length = decrypted_data[-1]
#     decrypted_data = decrypted_data[:-padding_length]
    
#     return decrypted_data.decode('utf-8')

# # Decrypt the data
# decrypted_data = decrypt_data(encrypted_data, key)

# print("Decrypted data:", decrypted_data)



