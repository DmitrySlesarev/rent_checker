import os
import time
from datetime import date

from flask import Flask, render_template
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

        return render_template("index.html", room_cards=room_cards, today=today)

    return app
