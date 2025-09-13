# SQLAlchemy models for users, parking lots, spots, and reservations
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# User model: stores user/admin info and authentication
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(200), unique = True, nullable = False)
    password_hash = db.Column(db.String(200), nullable = False)
    full_name = db.Column(db.String(100), nullable = False)
    address = db.Column(db.String(500), nullable = False)
    pincode = db.Column(db.String(10), nullable = False)
    role = db.Column(db.String(20), default = "user")

    # Hash and store password securely
    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Check password against stored hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# ParkingLot model: stores lot details and pricing
class ParkingLot(db.Model):
    __tablename__ = 'parking_lot'

    id = db.Column(db.Integer, primary_key = True)
    prime_location = db.Column(db.String(100), nullable = False)
    price = db.Column(db.Integer, nullable = False)
    address = db.Column(db.String(500), nullable = False)
    pincode = db.Column(db.String(10), nullable = False)
    available_spots = db.Column(db.Integer, nullable = False)
    total_spots = db.Column(db.Integer, nullable = False)
    created_at = db.Column(db.DateTime, default = datetime.now(timezone.utc))

# ParkingSpot model: stores individual spot status and lot association
class ParkingSpot(db.Model):
    __tablename__ = 'parking_spot'

    id = db.Column(db.Integer, primary_key = True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable = False)
    status = db.Column(db.String(1), default = "A")  # 'A' for available, 'O' for occupied

# Reservation model: stores booking info for each spot/user
class Reservation(db.Model):
    __tablename__ = 'reservation'

    id = db.Column(db.Integer, primary_key = True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    parking_time = db.Column(db.DateTime, nullable = False)
    leaving_time = db.Column(db.DateTime, nullable = True)
    cost = db.Column(db.Integer, nullable = True)
    vehicle_no = db.Column(db.String(10), nullable = False)
