from datetime import date, timedelta
from decimal import Decimal

from .models import Payment, Room, db


def _add_month(month_start: date, delta: int) -> date:
    new_month = month_start.month + delta
    year = month_start.year + (new_month - 1) // 12
    month = ((new_month - 1) % 12) + 1
    return date(year, month, 1)


def seed_demo_data():
    if Room.query.count() > 0:
        return

    rooms = []
    for floor in range(1, 5):
        for pos in range(1, 7):
            room_number = f"{floor}{pos:02d}"
            rooms.append(Room(number=room_number, floor=floor, position=pos))

    db.session.add_all(rooms)
    db.session.flush()

    today = date.today()
    current_month_start = date(today.year, today.month, 1)
    previous_month_start = _add_month(current_month_start, -1)
    previous_two_months_start = _add_month(current_month_start, -2)

    for idx, room in enumerate(rooms):
        base_amount = Decimal("1000.00") + Decimal(idx * 15)

        # Always include history so dropdown is useful.
        db.session.add(
            Payment(
                room_id=room.id,
                month_start=previous_two_months_start,
                due_date=previous_two_months_start + timedelta(days=7),
                paid_at=previous_two_months_start + timedelta(days=3),
                amount=base_amount,
            )
        )

        db.session.add(
            Payment(
                room_id=room.id,
                month_start=previous_month_start,
                due_date=previous_month_start + timedelta(days=7),
                paid_at=previous_month_start + timedelta(days=5),
                amount=base_amount,
            )
        )

        # Force first 3 rooms to represent each state.
        if idx == 0:
            db.session.add(
                Payment(
                    room_id=room.id,
                    month_start=current_month_start,
                    due_date=current_month_start + timedelta(days=7),
                    paid_at=today,
                    amount=base_amount,
                )
            )
        elif idx == 1:
            db.session.add(
                Payment(
                    room_id=room.id,
                    month_start=current_month_start,
                    due_date=today + timedelta(days=3),
                    paid_at=None,
                    amount=base_amount,
                )
            )
        elif idx == 2:
            db.session.add(
                Payment(
                    room_id=room.id,
                    month_start=current_month_start,
                    due_date=today - timedelta(days=5),
                    paid_at=None,
                    amount=base_amount,
                )
            )
        else:
            db.session.add(
                Payment(
                    room_id=room.id,
                    month_start=current_month_start,
                    due_date=current_month_start + timedelta(days=7),
                    paid_at=(today if idx % 3 == 0 else None),
                    amount=base_amount,
                )
            )

    db.session.commit()
