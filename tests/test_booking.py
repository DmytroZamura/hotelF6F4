"""Тести для класу Booking."""

import unittest
from datetime import date, timedelta

from models.booking import Booking
from models.contact import Contact
from models.guest import Guest
from models.room import StandardRoom, DeluxeRoom, Suite
from models.enums import RoomStatus


class TestBooking(unittest.TestCase):
    """Тести бронювання номера готелю."""

    def setUp(self) -> None:
        """Підготовка тестових даних перед кожним тестом."""
        self.contact = Contact(
            name="Іван Петренко",
            email="ivan@example.com",
            phone="+380501234567",
            passport="АА123456",
        )
        self.guest = Guest(contact=self.contact, birthday=date(1990, 5, 15))
        # Дата заїзду — завтра (гарантовано не в минулому)
        self.tomorrow = date.today() + timedelta(days=1)

    # ---------- створення бронювання ----------

    def test_create_booking_standard(self) -> None:
        """Створення бронювання стандартного номера."""
        room = StandardRoom(number=101)
        booking = Booking(
            guest=self.guest, room=room,
            check_in_date=self.tomorrow, nights=3,
        )
        self.assertEqual(booking.guest, self.guest)
        self.assertEqual(booking.room, room)
        self.assertEqual(booking.nights, 3)
        self.assertEqual(room.status, RoomStatus.RESERVED)

    def test_create_booking_deluxe(self) -> None:
        """Створення бронювання делюкс-номера."""
        room = DeluxeRoom(number=201)
        booking = Booking(
            guest=self.guest, room=room,
            check_in_date=self.tomorrow, nights=2,
        )
        self.assertEqual(room.status, RoomStatus.RESERVED)
        self.assertEqual(booking.nights, 2)

    def test_create_booking_suite(self) -> None:
        """Створення бронювання люкс-номера."""
        room = Suite(number=301)
        booking = Booking(
            guest=self.guest, room=room,
            check_in_date=self.tomorrow, nights=5,
        )
        self.assertEqual(room.status, RoomStatus.RESERVED)
        self.assertEqual(booking.nights, 5)

    # ---------- вартість ----------

    def test_total_cost(self) -> None:
        """Загальна вартість = ціна за ніч × кількість ночей."""
        room = StandardRoom(number=101)  # 800 грн/ніч
        booking = Booking(
            guest=self.guest, room=room,
            check_in_date=self.tomorrow, nights=3,
        )
        self.assertEqual(booking.total_cost(), 800.0 * 3)

    def test_total_cost_deluxe(self) -> None:
        """Вартість делюкс-номера за 2 ночі."""
        room = DeluxeRoom(number=201)  # 1500 грн/ніч
        booking = Booking(
            guest=self.guest, room=room,
            check_in_date=self.tomorrow, nights=2,
        )
        self.assertEqual(booking.total_cost(), 1500.0 * 2)

    # ---------- дата виїзду ----------

    def test_check_out_date(self) -> None:
        """Дата виїзду = дата заїзду + кількість ночей."""
        room = StandardRoom(number=101)
        booking = Booking(
            guest=self.guest, room=room,
            check_in_date=self.tomorrow, nights=4,
        )
        expected = self.tomorrow + timedelta(days=4)
        self.assertEqual(booking.check_out_date, expected)

    # ---------- валідація ----------

    def test_past_date_raises(self) -> None:
        """Дата заїзду в минулому — помилка."""
        room = StandardRoom(number=101)
        yesterday = date.today() - timedelta(days=1)
        with self.assertRaises(ValueError):
            Booking(
                guest=self.guest, room=room,
                check_in_date=yesterday, nights=2,
            )

    def test_zero_nights_raises(self) -> None:
        """Нуль ночей — помилка."""
        room = StandardRoom(number=101)
        with self.assertRaises(ValueError):
            Booking(
                guest=self.guest, room=room,
                check_in_date=self.tomorrow, nights=0,
            )

    def test_negative_nights_raises(self) -> None:
        """Від'ємна кількість ночей — помилка."""
        room = StandardRoom(number=101)
        with self.assertRaises(ValueError):
            Booking(
                guest=self.guest, room=room,
                check_in_date=self.tomorrow, nights=-1,
            )

    def test_occupied_room_raises(self) -> None:
        """Бронювання зайнятого номера — помилка."""
        room = StandardRoom(number=101, status=RoomStatus.OCCUPIED)
        with self.assertRaises(ValueError):
            Booking(
                guest=self.guest, room=room,
                check_in_date=self.tomorrow, nights=2,
            )

    def test_reserved_room_raises(self) -> None:
        """Бронювання вже зарезервованого номера — помилка."""
        room = StandardRoom(number=101, status=RoomStatus.RESERVED)
        with self.assertRaises(ValueError):
            Booking(
                guest=self.guest, room=room,
                check_in_date=self.tomorrow, nights=2,
            )

    def test_invalid_guest_type_raises(self) -> None:
        """Невалідний тип гостя — помилка."""
        room = StandardRoom(number=101)
        with self.assertRaises(TypeError):
            Booking(
                guest="не гість", room=room,
                check_in_date=self.tomorrow, nights=2,
            )

    def test_invalid_date_type_raises(self) -> None:
        """Невалідний тип дати — помилка."""
        room = StandardRoom(number=101)
        with self.assertRaises(TypeError):
            Booking(
                guest=self.guest, room=room,
                check_in_date="2026-04-25", nights=2,
            )

    # ---------- repr / str ----------

    def test_repr(self) -> None:
        """Перевірка repr бронювання."""
        room = StandardRoom(number=101)
        booking = Booking(
            guest=self.guest, room=room,
            check_in_date=self.tomorrow, nights=3,
        )
        r = repr(booking)
        self.assertIn("Booking", r)
        self.assertIn("101", r)
        self.assertIn("Іван Петренко", r)

    def test_str(self) -> None:
        """Перевірка str бронювання."""
        room = StandardRoom(number=101)
        booking = Booking(
            guest=self.guest, room=room,
            check_in_date=self.tomorrow, nights=3,
        )
        s = str(booking)
        self.assertIn("Бронювання", s)
        self.assertIn("101", s)
        self.assertIn("грн", s)

    # ---------- сьогоднішня дата ----------

    def test_today_date_allowed(self) -> None:
        """Дата заїзду сьогодні — допустимо."""
        room = StandardRoom(number=101)
        booking = Booking(
            guest=self.guest, room=room,
            check_in_date=date.today(), nights=1,
        )
        self.assertEqual(booking.check_in_date, date.today())


if __name__ == "__main__":
    unittest.main()
