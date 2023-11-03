# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv 
import os

# Import and register your blueprints
from app.routes.user_bp import user_bp
from app.routes.lease_bp import lease_bp

load_dotenv()



# Initialize Flask app
app = Flask(__name__)
app.debug = True

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:sai123@127.0.0.1:3306/rough'

# Access environment variables
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)


app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(lease_bp, url_prefix='/lease')