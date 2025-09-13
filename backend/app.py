# Flask and app imports
from flask import Flask, request, jsonify
from . import flask_app as app
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Database and model imports
from backend.models.table_models import db, ParkingLot, ParkingSpot, Reservation, User
from backend.models.create_admin import create_admin
from backend.models.auth_routes import register_user, login_user

# JWT and other libraries
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
from tasks.reminder_tasks import export_user_parking_history
from sqlalchemy import or_
import math
from backend.models import cache
import time

# Initialize admin user on app startup
create_admin(app)

create_admin(app)


#----------------------------------------------- DB Helper Functions ------------------------------------------------------
# These functions handle business logic and database operations for parking lots, spots, users, and reservations.

## Admin Creates Parking Lot
# Creates a new parking lot and its associated parking spots.
def CreateParkingLot(data):
    try:
        lot = ParkingLot(
            prime_location = data['prime_location'],
            price = data['price'],
            address =data['address'],
            pincode = data['pincode'],
            total_spots = data['total_spots'],
            available_spots = data['total_spots']
        )

        db.session.add(lot)
        db.session.commit()

        for _ in range(data['total_spots']):
            db.session.add(ParkingSpot(lot_id=lot.id, status='A'))

        db.session.commit()

        return {'msg': 'Parking lot created with spots'}, 201
    
    except Exception as e:
        db.session.rollback()
        return {'msg': 'Error occured while creating Parking Lot'}, 400

## Get Records of All Lots
# Returns all parking lots with their spot statistics.
def GetAllLots():
    try:
        lots = ParkingLot.query.all()
        result = []

        for lot in lots:
            total_spots = lot.total_spots
            available_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').count()
            occupied_spots = total_spots - available_spots

            result.append({
                'id': lot.id,
                'prime_location': lot.prime_location,
                'price': lot.price,
                'address': lot.address,
                'pincode': lot.pincode,
                'total_spots': total_spots,
                'available_spots': available_spots,
                'occupied_spots': occupied_spots
            })

        return result, 200

    except Exception as e:
        return {'msg': 'Error occured while getting all Parking Lots'}, 400

## Admin Edits Parking Lot
# Updates details of a parking lot.
def EditParkingLot(lot_id):
    try:
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return jsonify({'msg': 'Lot not found'}), 404

        data = request.get_json()

        # Editable fields
        lot.prime_location = data.get('prime_location', lot.prime_location)
        lot.price = data.get('price', lot.price)
        lot.address = data.get('address', lot.address)
        lot.pincode = data.get('pincode', lot.pincode)
        lot.total_spots = data.get('total_spots', lot.total_spots)

        db.session.commit()

        return {'msg': 'Lot updated successfully'}, 200

    except Exception as e:
        db.session.rollback()
        return {'msg': 'Error occurred while editing Parking Lot'}, 400


## Admin Deletes Parking Lot
# Deletes a parking lot if no reservations or occupied spots exist.
def DeleteParkingLot(lot_id):
    try:
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return {'msg': 'Lot not found'}, 404

        # Get all spot IDs under this lot
        spot_ids = [spot.id for spot in ParkingSpot.query.filter_by(lot_id=lot.id).all()]

        # Check if any reservation exists for these spots
        existing_reservations = Reservation.query.filter(Reservation.spot_id.in_(spot_ids)).first()
        if existing_reservations:
            return {'msg': 'Cannot delete lot. Reservation records exist for its spots.'}, 400

        # Optionally also check if any spots are currently occupied
        if ParkingSpot.query.filter_by(lot_id=lot.id, status='O').first():
            return {'msg': 'Cannot delete lot. Some spots are currently occupied.'}, 400

        # Safe to delete
        ParkingSpot.query.filter_by(lot_id=lot.id).delete()
        db.session.delete(lot)
        db.session.commit()

        return {'msg': 'Lot and its spots deleted successfully'}, 200
    
    except Exception as e:
        db.session.rollback()
        return {'msg': 'Error occured while editing Parking Lot'}, 400

## Admin Gets All Registered Users
# Returns all registered users (excluding admins).
def GetRegisteredUsers():
    try:
        users = User.query.all()
        result = []
        for user in users:
            if user.role == 'user':
                result.append({
                    'id': user.id,
                    'full_name': user.full_name,
                    'email': user.email,
                    'address': user.address,
                    'pincode': user.pincode
                })
            
            else:
                continue

        return result, 200
    
    except Exception as e:
        return {'msg': 'Error fetching registered users'}, 400
    
## Admin Deletes a Parking Spot
# Deletes a parking spot if not occupied and has no reservation history.
def DeleteSpot(spot_id):
    try:
        spot = ParkingSpot.query.get(spot_id)
        if not spot:
            return {'msg': 'Parking spot not found'}, 404

        if spot.status != 'A':
            return {'msg': 'Cannot delete an occupied spot'}, 400
        
        existing_reservation = Reservation.query.filter_by(spot_id=spot_id).first()
        if existing_reservation:
            return {'msg': 'Cannot delete spot with reservation history'}, 400
        
        lot = ParkingLot.query.get(spot.lot_id)
        if not lot:
            return {'msg': 'Associated parking lot not found'}, 404

        lot.total_spots -= 1
        lot.available_spots -= 1

        db.session.delete(spot)
        db.session.commit()

        return {'msg': 'Parking spot deleted successfully'}, 200

    except Exception as e:
        db.session.rollback()
        return {'msg': 'Error fetching registered users'}, 500

## Admin gets a Spot Data
# Returns data for a specific spot in a lot, including reservation info if occupied.
def GetSpotData(spot_no, lot_id):
    try:
        spots = ParkingSpot.query.filter_by(lot_id=lot_id).order_by(ParkingSpot.id).all()

        if spot_no < 1 or spot_no > len(spots):
            return {'msg': 'Invalid spot number for the given lot'}, 400

        spot = spots[spot_no - 1]

        response = {
            'spot_id': spot.id,
            'lot_id': spot.lot_id,
            'status': spot.status,
            'reservation': None
        }

        if spot.status == 'O':
            recent_reservation = Reservation.query.filter_by(spot_id=spot.id)\
                .order_by(Reservation.parking_time.desc()).first()

            if recent_reservation:
                response['reservation'] = {
                    'reservation_id': recent_reservation.id,
                    'user_id': recent_reservation.user_id,
                    'parking_time': recent_reservation.parking_time.isoformat(),
                    'vehicle_no': recent_reservation.vehicle_no
                }

        return response, 200

    except Exception as e:
        print("Error in GetSpotData:", e)
        return {'msg': 'Server error while fetching spot data'}, 500

    
## User Searches for Users
# Allows admin to search for users by name.
def SearchUsers():
    try:
        search_query = request.args.get('search_query')

        if not search_query:
            return {'msg': 'Search query is required'}, 400

        users = User.query.filter(User.full_name.ilike(f'%{search_query}%')).all()

        result = []

        for user in users:
            if user.role != 'admin':
                result.append({
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'address': user.address,
                    'pincode': user.pincode
                })

        return result, 200
    
    except Exception as e:
        print("Error: ", e)
        return {'msg': 'Error searching for lots'}, 455

## User Reserves a Parking Spot
# Allows a user to reserve an available parking spot in a lot.
def ReserveSpot(user_id):
    try:
        data = request.get_json()
        lot_id = data['lot_id']
        vehicle_no = data['vehicle_no']

        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return {'msg': 'Lot not found'}, 404

        # Find available spot
        spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
        if not spot:
            return {'msg': 'No available spots in this lot'}, 400

        # Mark spot as occupied
        spot.status = 'O'

        reservation = Reservation(
            user_id = user_id,
            spot_id = spot.id,
            parking_time = datetime.now(timezone.utc),
            vehicle_no = vehicle_no
        )

        lot.available_spots -= 1
        db.session.add(reservation)
        db.session.commit()

        return {'msg': 'Spot reserved', 'reservation_id': reservation.id}, 201

    except Exception as e:
        db.session.rollback()
        return {'msg': 'Reservation failed'}, 500

## User Releases a Parking Spot
# Allows a user to release a reserved parking spot and calculates cost.
def ReleaseSpot(reservation_id, user_id):
    try:
        reservation = Reservation.query.filter_by(id=reservation_id, user_id=user_id).first()
        if not reservation:
            return {'msg': 'Reservation not found'}, 404

        if reservation.leaving_time:
            return {'msg': 'Reservation already released'}, 400

        leaving_time = datetime.now(timezone.utc)

        spot = ParkingSpot.query.get(reservation.spot_id)
        spot.status = 'A'

        lot = ParkingLot.query.get(spot.lot_id)
        lot.available_spots += 1

        reservation.leaving_time = leaving_time.replace(tzinfo = None)

        # cost calc
        hours = (reservation.leaving_time - reservation.parking_time).total_seconds() / 3600
        hours = math.ceil(hours)  # ceiling to next integer
        reservation.cost = hours * lot.price

        db.session.commit()

        return {'msg':'Spot released', 'cost': reservation.cost},200

    except Exception as e:
        print("Error: ", e)
        db.session.rollback()
        return {'msg': 'Release failed'}, 500

## Particular User's Reservation Details
# Returns all reservations for a specific user.
def GetUserReservations(user_id):
    try:
        reservations = Reservation.query.filter_by(user_id=user_id).all()
        result = []

        for res in reservations:
            spot = ParkingSpot.query.get(res.spot_id)
            lot = ParkingLot.query.get(spot.lot_id)

            result.append({
                'reservation_id': res.id,
                'parking_time': res.parking_time,
                'leaving_time': res.leaving_time if res.leaving_time else None,
                'prime_location': lot.prime_location,
                'spot_id': spot.id,
                'cost': res.cost,
                'price': lot.price,
                'vehicle_no': res.vehicle_no
            })

        return result, 200

    except Exception as e:
        return {'msg': 'Error fetching reservations'}, 400

## User Searches for Lots
# Allows users to search for parking lots by location, address, or pincode.
def SearchLots():
    try:
        search_query = request.args.get('search_query')

        if not search_query:
            return {'msg': 'Search query is required'}, 400

        lots = ParkingLot.query.filter(
                    or_(
                        ParkingLot.prime_location.ilike(f'%{search_query}%'),
                        ParkingLot.address.ilike(f'%{search_query}%'),
                        ParkingLot.pincode.ilike(f'%{search_query}%')
                    )
                ).all()

        result = []

        for lot in lots:
            result.append({
                'id': lot.id,
                'address': lot.address,
                'price': lot.price,
                'available_spots': lot.available_spots,
            })

        return result, 200
    
    except Exception as e:
        print("Error: ", e)
        return {'msg': 'Error searching for lots'}, 455
    
## User Summary
# Returns summary statistics for a user's reservations.
def GetUserSummary(user_id):
    try:
        reservations = Reservation.query.filter_by(user_id=user_id).all()
        active = 0
        checked_out = 0
        total_spent = 0
        for res in reservations:
            if res.leaving_time:
                checked_out += 1
                total_spent += res.cost
            else:
                active += 1

        result = {
            'active_reservations': active,
            'checked_out_reservations': checked_out,
            'total_spent': total_spent
        }

        return result, 200

    except Exception as e:
        return {'msg': 'Error fetching user summary'}, 400

## Admin Summary
# Returns overall statistics for admin dashboard (revenue, occupancy, etc.).
def GetAdminSummary():
    try:
        reservations = Reservation.query.all()
        print("HELLO")
        lots = ParkingLot.query.all()

        total_revenue = 0
        occupied = 0
        available = 0
        lot_shares = []
        for res in reservations:
            if res.leaving_time:
                total_revenue += res.cost
            else:
                pass
        
        for lot in lots:
            lot_occupied = lot.total_spots - lot.available_spots
            available += lot.available_spots
            occupied += lot_occupied
            lot_shares.append({
                'lot_name': lot.prime_location,
                'reserved_spots': lot_occupied
            })

        result = {
            'occupied': occupied,
            'available': available,
            'total_revenue': total_revenue,
            'lot_shares': lot_shares
        }
        
        return result, 200

    except Exception as e:
        print("Exception: ", e)
        return {'msg': 'Error fetching admin summary'}, 400


#----------------------------------------------- Route Functions ------------------------------------------------------
# These functions define the API endpoints for user and admin actions.

@app.route('/register', methods = ["POST"])
# Registers a new user.
def Register():
    data = request.get_json()
    response, status = register_user(data)
    
    return jsonify(response), status

@app.route('/login', methods = ["POST"])
# Authenticates a user and returns a JWT token.
def Login():
    data = request.get_json()
    response, status = login_user(data)

    return jsonify(response), status


@app.route('/admin/parking_lot', methods=['POST'])
@jwt_required()
# Admin endpoint to create a new parking lot.
def Create_Parking_Lot():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user or user.role != 'admin':
        return jsonify({'msg': 'Admins only'}), 403

    data = request.get_json()

    result, status = CreateParkingLot(data)

    cache.delete('/admin/parking_lots')

    return jsonify(result), status

@app.route('/admin/parking_lots', methods=['GET'])
@cache.cached(timeout = 60, key_prefix = '/admin/parking_lots')
@jwt_required()
# Admin endpoint to get all parking lots.
def Get_All_Lots():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user or user.role != 'admin':
        return jsonify({'msg': 'Admins only'}), 403

    result, status = GetAllLots()

    return jsonify(result), status

@app.route('/admin/parking_lot/<int:lot_id>', methods=['PUT'])
@jwt_required()
# Admin endpoint to edit a parking lot.
def Edit_Parking_Lot(lot_id):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user or user.role != 'admin':
        return jsonify({'msg': 'Admins only'}), 403

    result, status = EditParkingLot(lot_id)

    cache.delete('/admin/parking_lots')

    return jsonify(result), status

@app.route('/admin/registered_users', methods = ["GET"])
@cache.cached(timeout = 120, key_prefix = '/admin/registered_users')
@jwt_required()
# Admin endpoint to get all registered users.
def Get_Registered_Users():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user or user.role != 'admin':
        return jsonify({'msg': 'Admins only'}), 403

    result, status = GetRegisteredUsers()

    return jsonify(result), status

@app.route('/admin/parking_lot/<int:lot_id>', methods = ['DELETE'])
@jwt_required()
# Admin endpoint to delete a parking lot.
def Delete_Parking_Lot(lot_id):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user or user.role != 'admin':
        return jsonify({'msg': 'Admins only'}), 403

    result, status = DeleteParkingLot(lot_id)

    cache.delete('/admin/parking_lots')

    return jsonify(result), status

@app.route('/lots', methods = ["GET"])
@jwt_required()
# User endpoint to get all parking lots.
def Get_Lots_For_User():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user or user.role != 'user':
        return jsonify({'msg': 'Users only'}), 403

    result, status = GetAllLots()

    return jsonify(result), status
    
@app.route('/reserve', methods=['POST'])
@jwt_required()
# User endpoint to reserve a parking spot.
def Reserve_Spot():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user or user.role != 'user':
        return jsonify({'msg': 'Users only'}), 403
    

    response, status = ReserveSpot(user.id)

    cache.delete('/my_reservations')
    cache.delete('/user/summary')

    return jsonify(response), status


@app.route('/release/<int:reservation_id>', methods=['POST'])
@jwt_required()
# User endpoint to release a reserved parking spot.
def Release_Spot(reservation_id):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user or user.role != 'user':
        return jsonify({'msg': 'Users only'}), 403

    response, status = ReleaseSpot(reservation_id, user.id)

    cache.delete('/my_reservations')
    cache.delete('/user/summary')

    return jsonify(response), status


@app.route('/my_reservations', methods=['GET'])
@cache.cached(timeout = 120, key_prefix = '/my_reservations')
@jwt_required()
# User endpoint to get all reservations for the logged-in user.
def Get_My_Reservations():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user or user.role != 'user':
        return jsonify({'msg': 'Users only'}), 403

    result, status = GetUserReservations(user.id)

    return jsonify(result), status

@app.route('/search_lots', methods = ['GET'])
@jwt_required()
# User endpoint to search for parking lots.
def Search_Lots():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user or user.role != 'user':
        return jsonify({'msg': 'Users only'}), 403

    result, status = SearchLots()

    return jsonify(result), status

@app.route('/user/summary', methods = ['GET'])
@cache.cached(timeout = 120, key_prefix = '/user/summary')
@jwt_required()
# User endpoint to get summary statistics for the logged-in user.
def Get_User_Summary():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user or user.role != 'user':
        return jsonify({'msg': 'Users only'}), 403
    
    result, status = GetUserSummary(user.id)

    return jsonify(result), status

@app.route('/admin/summary', methods = ['GET'])
@cache.cached(timeout = 120, key_prefix = '/admin/summary')
@jwt_required()
# Admin endpoint to get overall summary statistics.
def Get_Admin_Summary():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user or user.role != 'admin':
        return jsonify({'msg': 'Admins only'}), 403

    result, status = GetAdminSummary()

    return jsonify(result), status

@app.route('/admin/search', methods = ['GET'])
@jwt_required()
# Admin endpoint to search for users.
def Search_Users():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user or user.role != 'admin':
        return jsonify({'msg': 'Admins only'}), 403

    result, status = SearchUsers()

    return jsonify(result), status

@app.route('/admin/delete_spot/<int:spot_id>', methods = ['DELETE'])
@jwt_required()
# Admin endpoint to delete a parking spot.
def Delete_Spot(spot_id):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user or user.role != 'admin':
        return jsonify({'msg': 'Admins only'}), 403
    
    result, status = DeleteSpot(spot_id)

    cache.delete('/admin/parking_lots')

    return jsonify(result), status

@app.route('/admin/spot/<int:spot_no>/<int:lot_id>', methods = ["GET"])
@jwt_required()
# Admin endpoint to get data for a specific parking spot.
def Get_Spot_Data(spot_no, lot_id):
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user or user.role != 'admin':
        return jsonify({'msg': 'Admins only'}), 403
    
    result, status = GetSpotData(spot_no, lot_id)

    return jsonify(result), status

@app.route('/export_parking_csv', methods = ['POST'])
@jwt_required()
# User endpoint to export parking history as CSV (async task).
def trigger_csv_export():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user or user.role != 'user':
        return jsonify({'msg': 'Users only'}), 403

    export_user_parking_history.delay(user_id)

    return jsonify({"msg": "Your parking history is being processed. You'll receive an email once ready."}), 202

@app.after_request
# Adds CORS headers to every response.
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Authorization,Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

# Entry point for running the Flask app.
if __name__ == "__main__":
    app.run(debug=True)