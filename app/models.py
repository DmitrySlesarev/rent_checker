from datetime import date

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Room(db.Model):
    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(16), unique=True, nullable=False)
    floor = db.Column(db.Integer, nullable=False, default=1)
    position = db.Column(db.Integer, nullable=False, default=1)

    payments = db.relationship("Payment", back_populates="room", cascade="all,delete-orphan")

    def compute_status(self, payments, today: date) -> str:
        current_month_start = date(today.year, today.month, 1)
        overdue = any(p.paid_at is None and p.due_date < today for p in payments)
        if overdue:
            return "overdue"

        current_month = next((p for p in payments if p.month_start == current_month_start), None)
        if current_month and current_month.paid_at is not None:
            return "paid"

        return "current_unpaid"


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=False, index=True)
    month_start = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    paid_at = db.Column(db.Date, nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)

    room = db.relationship("Room", back_populates="payments")
