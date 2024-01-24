from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv 
import os

load_dotenv()


DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Register the blueprints for each route group
from app.routes import user_routes
from app.routes import country_routes
from app.routes import lease_routes
from app.routes import password_routes

app.register_blueprint(user_routes.user_routes, url_prefix="/api/users")
app.register_blueprint(country_routes.country_routes, url_prefix="/api/countries")
app.register_blueprint(lease_routes.lease_routes, url_prefix="/api/lease")
app.register_blueprint(password_routes.password_routes, url_prefix="/api/password")


# from app import routes  # Import the routes after initializing db
