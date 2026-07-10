from tools import check_availability, book_appointment


def test_check_availability_returns_open_slots():
    slots = check_availability("2026-07-15")
    assert "10:00" in slots and "14:00" in slots


def test_booking_removes_slot():
    book_appointment("2026-07-15", "10:00", "Fatou", "+15551234567")
    assert "10:00" not in check_availability("2026-07-15")
