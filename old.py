from flask import request, json, jsonify, Flask, g
import pandas as pd
from flask_cors import CORS
from sqlalchemy.exc import SQLAlchemyError
import jwt
from functools import wraps
import datetime
from flask_mail import Mail, Message
from twilio.rest import Client
import random
import mysql.connector  # Import the mysql.connector library
from sqlalchemy.sql import text


app = Flask(__name__)
CORS(app)


account_sid = 'ACd385449272c77d3c5442bc12caa32c5e'
auth_token = 'cee34d164876e14591b7931c6bc650f0'
client = Client(account_sid, auth_token)

db_config = {
    'host': 'api.portfolioone.io',
    'port': 3306,
    'user': 'portfolio',
    'password': 'PortfolioOne!@#',
    'db': 'dfx'
}

# Create a MySQL connection
conn = mysql.connector.connect(
    host=db_config['host'],
    user=db_config['user'],
    password=db_config['password'],
    database=db_config['db'],
    port=db_config['port']
)




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




@app.errorhandler(Exception)
def handle__error(e):
    # logger.error(e)
    return e



@app.route('/getAllLeaseData',methods=['GET'])
@token_required
def  getAllLeaseData():
    try:
        # SQL query to fetch data 
        query = "SELECT * FROM lease_data"

        # Use pandas to read data into a DataFrame
        df = pd.read_sql(query, conn)
        data_list = df.to_dict(orient='records')
        
        result={
            'status':200,
            'data':data_list,
            'Message':'Request Submitted Successfully',
            'count':len(data_list)
        }
        
        # logger.info('getAllLeaseData api call is successful')
        return jsonify(result)

    except Exception as e:
        return str(e)
  

@app.route('/getAllLeaseDataByUser/<string:id>', methods=['GET'])
@token_required
def getAllLeaseData_by_id(id):
    try:
        # SQL query to fetch data based on the provided ID
        query = f"SELECT * FROM lease_data WHERE user_id= '{id}'"
        # Use pandas to read data into a DataFrame
        df = pd.read_sql(query, conn)
        # Convert the DataFrame to a list of dictionaries
        data_list = df.to_dict(orient='records')
        
        result={
            'status':200,
            'data':data_list,
            'Message':'Request Submitted Successfully',
            'count':len(data_list)
        }
        
        return jsonify(result)

    except Exception as e:
        return str(e)


@app.route('/addLeaseData', methods=['POST'])
@token_required
def addNewLeaseData():
    try:
        data = request.get_json()

        # Ensure that required fields are present in the JSON data
        required_fields = ['additional_facilities_cost', 'address', 'annualized_base_rent', 'lease_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        # Extract data from the JSON request
        additional_facilities_cost = data['additional_facilities_cost']
        address = data['address']
        annualized_base_rent = data['annualized_base_rent']
        lease_id = data['lease_id']

        # Insert data into the database
        query = text("INSERT INTO lease_data (additional_facilities_cost, address, annualized_base_rent, lease_id) "
                     "VALUES (:additional_facilities_cost, :address, :annualized_base_rent, :lease_id)")
        params = {
            'additional_facilities_cost': additional_facilities_cost,
            'address': address,
            'annualized_base_rent': annualized_base_rent,
            'lease_id': lease_id
        }

        with conn.connect() as connection:
            connection.execute(query, params)
            connection.commit()

        result = {
            'status': 200,
            'Message': 'Lease data inserted successfully'
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/RegisterUser', methods=['POST'])
def RegisterUser():
    try:
        data = request.get_json()
        name = data['fullname']
        email = data['email']
        mobile = data['mobile']
        password = data['password']
        organisation = data['organisation']
        # SQL query to fetch data based on the provided ID
        query = f"SELECT * FROM user_details WHERE email= '{email}' OR mobile='{mobile}'"
        # Use pandas to read data into a DataFrame
        df = pd.read_sql(query, conn)
        # Convert the DataFrame to a list of dictionaries
        data_list = df.to_dict(orient='records')
        if data_list!=[]:
            result={
                'status': 500,
                'Message': 'User already exist'
            }
        else:
            # SQL query to insert data into the user_details table
            query = text(f"INSERT INTO user_details(`fullname`, `email`, `mobile`, `password`, `organisation`) VALUES (:fullname, :email, :mobile, :password, :organisation)")
            params = {
                'fullname': name,
                'email': email,
                'mobile': mobile,
                'password': password,
                'organisation': organisation
            }
            with conn.connect() as connection:
                connection.execute(query, params)
                connection.commit()

            result = {
                'status': 200,
                'Message': 'User data inserted successfully'
            }
    except SQLAlchemyError as e:
        result = {
            'status': 500,
            'Message': str(e)
        }

    return jsonify(result)

@app.route('/validateUser', methods=['POST'])
def validateUser():
    try:
        data= request.get_json() 
        username=data['email']
        password=data['password']
        # SQL query to fetch data based on the provided ID
        query = f"SELECT * FROM user_details WHERE email= '{username}' AND password='{password}'"
        # Use pandas to read data into a DataFrame
        df = pd.read_sql(query, conn)
        # Convert the DataFrame to a list of dictionaries
        data_list = df.to_dict(orient='records')
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



# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465  # Use the appropriate port (587 for TLS)
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True   
app.config['MAIL_USERNAME'] = 'reddysainath47@gmail.com'
app.config['MAIL_PASSWORD'] = 'jxyhiqscawrnbntw'  # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = 'reddysainath47@gmail.com'


mail = Mail(app)




@app.route('/send-otp', methods=['POST'])
def send_otp():
    try:

        data = request.get_json()
        mobile_number = data.get('mobile_number')
        email = data['email']
                # print(email)
        # return jsonify({email})

                # Check if both mobile_number and email are provided
        if not mobile_number or not email:
            response = {
                'status': 400,
                'message': 'Both mobile_number and email are required.'
            }
            return jsonify(response)

        # Query the database to check if a user with the provided email and mobile number exists
        query = f"SELECT * FROM user_details WHERE email= '{email}' OR mobile='{mobile_number}'"
        df = pd.read_sql(query, conn)
        data_list = df.to_dict(orient='records')

        if  data_list:
            response = {
                'status': 400,
                'message': 'User already registered. Please log in.'
            }
            return jsonify(response)

  
        # Generate a random 4-digit OTP
        otp = ''.join(random.choice('0123456789') for i in range(4))

        # Create an email message
        msg = Message('Your OTP Code', recipients=[email])
        msg.body = f'Your OTP code is: {otp}'

        # Send the email
        mail.send(msg)

        response = {
            'status': 200,
            'message': 'OTP sent successfully',
            'otp': otp
        }

        # return jsonify(response)




        # Compose the message
        message = f'Your OTP is: {otp}'

        # # Send the message using Twilio
        # client.messages.create(
        #     to=mobile_number,
        #     from_='+12512208257',
        #     body=message
        # )


        # return jsonify(mobile_number)

        message = client.messages.create(
        from_='+12512208257',
        body=message,
        to= f'+91{mobile_number}'
        )

        print(message.sid)

        response = {
            'status': 200,
            'message': 'OTP sent successfully',
            'otp': otp
        }
        return jsonify(response)

    except Exception as e:
        return str(e)

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
                # Query the database to check if a user with the provided email and mobile number exists
        query = f"SELECT * FROM user_details WHERE email= '{email}' OR mobile='{mobile_number}'"
        df = pd.read_sql(query, conn)
        data_list = df.to_dict(orient='records')
        # print(data_list)
        if not data_list:
            response = {
                'status': 400,
                'message': 'User not registred, please signup.'
            }
            return jsonify(response)

        # Generate a random 4-digit OTP
        otp = ''.join(random.choice('0123456789') for i in range(4))

        # Create an email message
        msg = Message('Your OTP Code', recipients=[email])
        msg.body = f'Your OTP code is: {otp}'

        # Send the email
        mail.send(msg)

        
        # Compose the message
        message = f'Your OTP is: {otp}'

        # # Send the message using Twilio
        # client.messages.create(
        #     to=mobile_number,
        #     from_='+12512208257',
        #     body=message
        # )

   

        # return jsonify(mobile_number)

        message = client.messages.create(
        from_='+12512208257',
        body=message,
        to= f'+91{mobile_number}'
        )

        # print(message.sid)

        # response = {
        #     'status': 200,
        #     'message': 'OTP sent successfully',
        #     # 'otp': otp
        # }
        # return jsonify(response)

        # Save the OTP and user ID in the database
        # In this example, we'll assume you have a user_id that corresponds to the user's email in your database
        # Replace 'your_query' with the correct query to retrieve user_id based on email
        user_id_query = text("SELECT user_id FROM user_details WHERE email = :email")
        user_id_params = {'email': email}

        with conn.connect() as connection:
            user_id = connection.execute(user_id_query, user_id_params).fetchone()
            if user_id:
                user_id = user_id[0]
                # Now insert the OTP into the otp_data table
                insert_query = text("INSERT INTO otp_data (user_id, otp) VALUES (:user_id, :otp)")
                insert_params = {
                    'user_id': user_id,
                    'otp': otp
                }
                connection.execute(insert_query, insert_params)
                connection.commit()
                response = {
                    'status': 200,
                    'message': 'OTP sent successfully'
                }
            else:
                response = {
                    'status': 400,
                    'message': 'User not found'
                }

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

        # Verify if the OTP matches the latest one stored in the database
        # You can retrieve the latest OTP based on the user's email
        query = text("SELECT otp FROM otp_data WHERE user_id = (SELECT user_id FROM user_details WHERE email = :email) "
                    "ORDER BY created_at DESC LIMIT 1")


        params = {'email': email}

        with conn.connect() as connection:
            result = connection.execute(query, params).fetchone()

        print(result)
        if result and result[0] == otp:
            # Update the password in the user_details table
            update_query = text("UPDATE user_details SET password = :new_password WHERE email = :email")
            update_params = {
                'email': email,
                'new_password': new_password
            }

            with conn.connect() as connection:
                connection.execute(update_query, update_params)
                connection.commit()

            # Clean up the used OTP
            delete_query = text("DELETE FROM otp_data WHERE user_id = (SELECT user_id FROM user_details WHERE email = :email)")
            delete_params = {'email': email}
            with conn.connect() as connection:
                connection.execute(delete_query, delete_params)
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