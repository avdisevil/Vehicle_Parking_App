# Celery tasks for reminders, monthly reports, and CSV export
from datetime import datetime, timezone, timedelta, date
from backend.models.table_models import db, User, Reservation, ParkingLot, ParkingSpot
from sqlalchemy import func
from flask_mail import Message
from backend.models import mail
from celery_app import celery_app
import io
import csv

# Get Flask app context from Celery for DB access
flask_app = celery_app.flask_app

def user_not_visited_mail(user):
    """
    Send a reminder email to a user who has not booked a parking slot today.
    """
    msg = Message(
        subject="Parking Slot Reminder",
        recipients=[user.email],
        body=f"""
Hello {user.full_name},

You haven’t booked any parking slot today. 
Please make a reservation to avoid inconvenience.

– Parking App Team
""".strip()
    )
    try:
        mail.send(msg)
        print(f"Reminder email sent to {user.email}")
    except Exception as e:
        print(f"Failed to send email to {user.email}: {e}")

def new_lot_created_mail(user):
    """
    Send a notification email to all users when a new parking lot is created.
    """
    msg = Message(
        subject="New Parking Lot Created",
        recipients=[user.email],
        body=f"""
Hello {user.full_name},

New parking lot has been created. 

– Parking App Team
""".strip()
    )
    try:
        mail.send(msg)
        print(f"Reminder email sent to {user.email}")
    except Exception as e:
        print(f"Failed to send email to {user.email}: {e}")

@celery_app.task
# Daily scheduled task: Remind users who haven't booked and notify about new lots
def send_daily_reminder():
    with flask_app.app_context():
        today_utc = datetime.now(timezone.utc).date()
        # today_utc = date(2025, 8, 1) # Test run
        print(f"Running reminder check for {today_utc}")

    # --- 1. Find users who DID NOT book today ---
        booked_user_ids = db.session.query(Reservation.user_id)\
            .filter(func.date(Reservation.parking_time) == today_utc)\
            .distinct().all()

        booked_user_ids = [uid for (uid,) in booked_user_ids]

        users_without_booking = User.query.filter(~User.id.in_(booked_user_ids)).all()

        if users_without_booking:
            print("Users without a reservation today:")
            for user in users_without_booking:
                if user.role == 'user':
                    print(f"{user.full_name} ({user.email}) did NOT book a slot today.")
                    user_not_visited_mail(user)
        else:
            print("All users have booked today.")

    # --- 2. Notify users about new parking lots created today ---
        new_lots = ParkingLot.query.filter(
            func.date(ParkingLot.created_at) == today_utc
        ).all()

        if new_lots:
            print("New parking lots added today:")

            all_users = User.query.filter(User.role != 'admin').all()
            
            for lot in new_lots:
                print(f"Lot: {lot.prime_location} (ID: {lot.id})")

                for user in all_users:
                    new_lot_created_mail(user)
        else:
            print("No new parking lots created today.")

@celery_app.task
# Monthly scheduled task: Send users a summary report of their parking activity
def send_monthly_user_report():
    with flask_app.app_context():
        today = datetime.now(timezone.utc).date()
        today = date(2025, 8, 1) # Test Run
        first_day_of_month = today.replace(day=1)
        last_month = first_day_of_month - timedelta(days=1)
        first_day_last_month = last_month.replace(day=1)
        last_day_last_month = last_month

        print(f"Generating reports for: {first_day_last_month} to {last_day_last_month}")

        users = User.query.filter(User.role != 'admin').all()

        for user in users:
            reservations = (
                db.session.query(Reservation)
                .join(ParkingSpot, ParkingSpot.id == Reservation.spot_id)
                .join(ParkingLot, ParkingLot.id == ParkingSpot.lot_id)
                .filter(
                    Reservation.user_id == user.id,
                    func.date(Reservation.parking_time) >= first_day_last_month,
                    func.date(Reservation.parking_time) <= last_day_last_month
                )
                .all()
            )

            if not reservations:
                continue

            total_bookings = len(reservations)
            total_cost = sum(r.cost for r in reservations if r.cost)

            # Count most used lot by name
            lot_counter = {}
            for r in reservations:
                lot = (
                    db.session.query(ParkingLot)
                    .join(ParkingSpot, ParkingSpot.lot_id == ParkingLot.id)
                    .filter(ParkingSpot.id == r.spot_id)
                    .first()
                )
                if lot:
                    lot_name = lot.prime_location
                    lot_counter[lot_name] = lot_counter.get(lot_name, 0) + 1

            most_used_lot = max(lot_counter, key=lot_counter.get)

            print("\nHello This Is send_monthly_user_report function\n")

            # --- Create HTML Report for user ---
            html_body = f"""
            <h2>Monthly Parking Activity Report</h2>
            <p>Hello <b>{user.full_name}</b>, here is your report for <b>{first_day_last_month.strftime('%B %Y')}</b>.</p>
            <ul>
                <li>Total Reservations: <b>{total_bookings}</b></li>
                <li>Most Used Parking Lot: <b>{most_used_lot}</b></li>
                <li>Total Spent: ₹<b>{total_cost}</b></li>
            </ul>
            <p>Thanks for using our Parking System!</p>
            """

            try:
                print("\nInside that try function btw\n")
                msg = Message(
                    subject="Monthly Parking Report",
                    recipients=[user.email],
                    html=html_body
                )
                mail.send(msg)
                print(f"Monthly report sent to {user.email}")
            except Exception as e:
                print(f"Failed to send report to {user.email}: {e}")

@celery_app.task
# On-demand task: Export a user's parking history as a CSV and email it
def export_user_parking_history(user_id):
    try:
        with flask_app.app_context():
            print("USER ID: ", user_id)
            user = User.query.get(int(user_id))

            if not user:
                print(f"No user found with id {user_id}")
                return

            reservations = (
                Reservation.query
                .filter_by(user_id=user.id)
                .order_by(Reservation.parking_time.desc())
                .all()
            )

            if not reservations:
                print(f"No reservations for {user.email}")
                return

            # Prepare CSV file for user's parking history
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow([
                'Slot ID', 'Spot ID', 'Parking Time', 'Checkout Time',
                'Duration (mins)', 'Cost (Rs)', 'Lot Name'
            ])

            for r in reservations:
                spot = ParkingSpot.query.get(r.spot_id)
                lot = ParkingLot.query.get(spot.lot_id)

                parking_time = r.parking_time.strftime('%Y-%m-%d %H:%M')
                leaving_time = r.leaving_time.strftime('%Y-%m-%d %H:%M') if r.leaving_time else '-'
                duration = (r.leaving_time - r.parking_time).total_seconds() // 60 if r.leaving_time else '-'

                writer.writerow([
                    r.id,
                    spot.id,
                    parking_time,
                    leaving_time,
                    duration,
                    r.cost,
                    lot.prime_location
                ])

            try:
                msg = Message(
                    subject="Your Parking History Report (CSV)",
                    recipients=[user.email],
                    body=f"Hi {user.full_name},\n\nPlease find your parking history report."
                )
                msg.attach("parking_history.csv", "text/csv", output.getvalue())
                mail.send(msg)
                print(f"CSV report sent to {user.email}")
            except Exception as e:
                print(f"Failed to send CSV to {user.email}: {e}")

    except Exception as e:
        print("Error: ", e)