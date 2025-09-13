# Backend app initialization and configuration
from flask import Flask
from .table_models import db
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from flask_caching import Cache
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask extensions
mail = Mail()  # For sending emails
jwt = JWTManager()  # For JWT authentication
cache = Cache()  # For caching (uses Redis)

# Read secrets and credentials from environment
APP_SECRET_KEY = os.getenv('APP_SECRET_KEY')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

# Factory function to create and configure the Flask app
def create_app():
    app = Flask(__name__)

    # Enable CORS for all routes and origins
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, allow_headers=["Authorization", "Content-Type"], expose_headers=["Authorization"])
    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/parking.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = APP_SECRET_KEY
    app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY

    # Mail server configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = MAIL_USERNAME
    app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
    app.config['MAIL_DEFAULT_SENDER'] = MAIL_DEFAULT_SENDER

    # Redis cache configuration
    app.config['CACHE_TYPE'] = 'RedisCache'
    app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/2'

    # Initialize extensions with app
    cache.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    jwt.init_app(app)

    # Create all database tables
    with app.app_context():
        db.create_all()

    return app
