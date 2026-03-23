import os
import time
from datetime import date

from flask import Flask, redirect, render_template, request, url_for
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from .models import Payment, Room, db
from .seed import seed_demo_data


def _wait_for_database(max_attempts: int = 20, delay_seconds: float = 1.0) -> None:
    for attempt in range(1, max_attempts + 1):
        try:
            db.session.execute(text("SELECT 1"))
            return
        except OperationalError:
            if attempt == max_attempts:
                raise
            time.sleep(delay_seconds)


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "postgresql+psycopg2://rent_user:rent_pass@localhost:5432/rent_checker"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        _wait_for_database()
        db.create_all()
        seed_demo_data()

    @app.route("/")
    def index():
        today = date.today()
        rooms = Room.query.order_by(Room.floor.asc(), Room.position.asc()).all()
        room_cards = []

        for room in rooms:
            payments = (
                Payment.query.filter_by(room_id=room.id)
                .order_by(Payment.month_start.desc())
                .all()
            )
            room_cards.append(
                {
                    "room": room,
                    "status": room.compute_status(payments, today),
                    "payments": payments,
                }
            )

        return render_template("index.html", room_cards=room_cards, today=today, rooms=rooms)

    @app.post("/payments/confirm")
    def confirm_payment():
        room_id = request.form.get("room_id", type=int)
        amount = request.form.get("amount", type=float)

        if room_id is None or amount is None:
            return redirect(url_for("index"))

        today = date.today()
        current_month_start = date(today.year, today.month, 1)
        due_date = date(today.year, today.month, 7)

        payment = Payment.query.filter_by(room_id=room_id, month_start=current_month_start).first()
        if payment is None:
            payment = Payment(
                room_id=room_id,
                month_start=current_month_start,
                due_date=due_date,
                amount=amount,
                paid_at=today,
            )
            db.session.add(payment)
        else:
            payment.amount = amount
            payment.paid_at = today

        db.session.commit()
        return redirect(url_for("index"))

    return app
