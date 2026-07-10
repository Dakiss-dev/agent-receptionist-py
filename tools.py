"""Booking tools backed by a JSON file store.

The store path comes from the CALENDAR_STORE env var (tests point it at a
throwaway copy) and defaults to calendar_store.json next to this file.
"""

import json
import os
from pathlib import Path


def _store_path() -> Path:
    return Path(os.environ.get("CALENDAR_STORE", Path(__file__).parent / "calendar_store.json"))


def _load() -> dict:
    with open(_store_path()) as f:
        return json.load(f)


def _save(data: dict) -> None:
    with open(_store_path(), "w") as f:
        json.dump(data, f, indent=2)


def check_availability(date: str) -> list[str]:
    """Return open time slots for a date (empty list if none)."""
    return _load()["slots"].get(date, [])


def book_appointment(date: str, time: str, name: str, phone: str) -> dict:
    """Book a slot. Raises ValueError if the slot is not available."""
    data = _load()
    open_slots = data["slots"].get(date, [])
    if time not in open_slots:
        raise ValueError(f"{time} on {date} is not available. Open slots: {open_slots or 'none'}")
    open_slots.remove(time)
    booking = {"date": date, "time": time, "name": name, "phone": phone}
    data["bookings"].append(booking)
    _save(data)
    return {"confirmed": True, **booking}
