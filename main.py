"""Демонстрація роботи з готелями: створення, бронювання, збереження."""

from datetime import date

from constants.amenity import WIFI, TV, MINI_BAR
from models.booking import Booking
from models.contact import Contact
from models.guest import Guest
from models.hotel import Hotel
from models.room import StandardRoom, DeluxeRoom, Suite
from services import report
from services.report import HotelReportGenerator
from services.storage import HotelStorage
from utils.data_utils import obj_to_dict, dict_to_class


def create_demo_hotels() -> tuple[Hotel, Hotel]:
    """Створює два демонстраційні готелі з гостями та бронюваннями.

    Returns:
        Кортеж із двох готелів.
    """
    # ── Гості ──
    guest1 = Guest(
        contact=Contact(
            name="Іван Петров",
            email="ivan.petrov@gmail.com",
            phone="+380631234567",
            passport="АА111222",
        ),
        birthday=date(1990, 5, 20),
    )
    guest2 = Guest(
        contact=Contact(
            name="Марія Подопригора",
            email="m.podoprygora@gmail.com",
            phone="+380631234568",
            passport="АА111242",
        ),
        birthday=date(1992, 8, 15),
    )
    guest3 = Guest(
        contact=Contact(
            name="Олексій Шевченко",
            email="o.shevchenko@ukr.net",
            phone="+380501112233",
            passport="ВВ334455",
        ),
        birthday=date(1985, 3, 10),
    )
    guest4 = Guest(
        contact=Contact(
            name="Анна Коваленко",
            email="anna.kovalenko@gmail.com",
            phone="+380671239876",
            passport="СС556677",
        ),
        birthday=date(1998, 12, 1),
    )

    # ── Готель 1: «Карпатський Затишок» ──
    hotel1 = Hotel(name="Карпатський Затишок")
    hotel1.add_room(StandardRoom(number=101))
    hotel1.add_room(StandardRoom(number=102))
    hotel1.add_room(DeluxeRoom(number=201))
    hotel1.add_room(Suite(number=301))

    # Бронювання для готелю 1
    booking1 = hotel1.book(guest1, hotel1.rooms[0], nights=3, check_in_date=date(2026, 5, 1))
    booking2 = hotel1.book(guest2, hotel1.rooms[2], nights=5, check_in_date=date(2026, 5, 3))

    # ── Готель 2: «Одеса Палас» ──
    hotel2 = Hotel(name="Одеса Палас")
    hotel2.add_room(StandardRoom(number=101, price_per_night=1000.0))
    hotel2.add_room(DeluxeRoom(number=201, price_per_night=2000.0))
    hotel2.add_room(DeluxeRoom(number=202, price_per_night=2000.0))
    hotel2.add_room(Suite(number=301, price_per_night=4500.0))

    # Бронювання для готелю 2
    booking3 = hotel2.book(guest3, hotel2.rooms[0], nights=2, check_in_date=date(2026, 5, 10))
    booking4 = hotel2.book(guest4, hotel2.rooms[3], nights=7, check_in_date=date(2026, 6, 1))

    return hotel1, hotel2


def main() -> None:
    """Головна функція: створює готелі, виводить інформацію, зберігає у storage."""

    storage = HotelStorage()
    hotels = storage.load_all()
    reports = HotelReportGenerator()
    reports.generate_all(hotels, storage)













if __name__ == "__main__":
    main()
