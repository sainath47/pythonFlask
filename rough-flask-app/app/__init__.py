from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv 
import os

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Register the blueprints for each route group
from app.routes import user_routes

app.register_blueprint(user_routes.user_routes, url_prefix="/users")


# from app import routes  # Import the routes after initializing db
