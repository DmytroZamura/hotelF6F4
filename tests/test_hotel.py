"""Тести для класу Hotel."""

import unittest
from datetime import date

from models.contact import Contact
from models.enums import RoomStatus
from models.guest import Guest
from models.hotel import Hotel
from models.room import StandardRoom, DeluxeRoom, Suite


class TestHotelCreation(unittest.TestCase):
    """Тести створення готелю."""

    def test_create_hotel(self) -> None:
        """Готель створюється з коректною назвою."""
        hotel = Hotel("Grand Hotel")
        self.assertEqual(hotel.name, "Grand Hotel")
        self.assertEqual(hotel.rooms, [])
        self.assertEqual(hotel.bookings, [])

    def test_empty_name_raises(self) -> None:
        """Порожня назва — виняток."""
        with self.assertRaises(ValueError):
            Hotel("")

    def test_non_string_name_raises(self) -> None:
        """Назва не рядок — виняток."""
        with self.assertRaises(TypeError):
            Hotel(123)


class TestHotelRooms(unittest.TestCase):
    """Тести додавання та пошуку номерів."""

    def setUp(self) -> None:
        self.hotel = Hotel("Test Hotel")
        self.std = StandardRoom(101)
        self.dlx = DeluxeRoom(201)
        self.suite = Suite(301)

    def test_add_room(self) -> None:
        """Номер успішно додається."""
        self.hotel.add_room(self.std)
        self.assertEqual(len(self.hotel), 1)

    def test_add_duplicate_raises(self) -> None:
        """Дублікат номера — виняток."""
        self.hotel.add_room(self.std)
        dup = StandardRoom(101)
        with self.assertRaises(ValueError):
            self.hotel.add_room(dup)

    def test_add_non_room_raises(self) -> None:
        """Додавання не-Room — виняток."""
        with self.assertRaises(TypeError):
            self.hotel.add_room("not a room")

    def test_find_available_all(self) -> None:
        """Пошук вільних номерів без фільтра."""
        self.hotel.add_room(self.std)
        self.hotel.add_room(self.dlx)
        self.assertEqual(len(self.hotel.find_available()), 2)

    def test_find_available_by_type(self) -> None:
        """Фільтр за типом номера."""
        self.hotel.add_room(self.std)
        self.hotel.add_room(self.dlx)
        self.hotel.add_room(self.suite)
        result = self.hotel.find_available(DeluxeRoom)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], DeluxeRoom)

    def test_find_available_excludes_occupied(self) -> None:
        """Зайняті номери не потрапляють у результат."""
        self.hotel.add_room(self.std)
        self.std.status = RoomStatus.OCCUPIED
        self.assertEqual(len(self.hotel.find_available()), 0)


class TestHotelBooking(unittest.TestCase):
    """Тести бронювання, заселення, виселення."""

    def setUp(self) -> None:
        self.hotel = Hotel("Test Hotel")
        self.room = StandardRoom(101)
        self.hotel.add_room(self.room)
        contact = Contact(
            name="Іван Петренко",
            email="ivan@example.com",
            phone="+380501234567",
            passport="АА123456",
        )
        self.guest = Guest(contact=contact, birthday=date(1990, 5, 15))

    def test_book_creates_booking(self) -> None:
        """Бронювання створюється і додається до списку."""
        booking = self.hotel.book(self.guest, self.room, nights=3)
        self.assertEqual(len(self.hotel.bookings), 1)
        self.assertEqual(self.room.status, RoomStatus.RESERVED)
        self.assertEqual(booking.nights, 3)

    def test_book_room_not_in_hotel_raises(self) -> None:
        """Бронювання номера, що не належить готелю — виняток."""
        other_room = StandardRoom(999)
        with self.assertRaises(ValueError):
            self.hotel.book(self.guest, other_room, nights=2)

    def test_book_occupied_room_raises(self) -> None:
        """Бронювання зайнятого номера — виняток."""
        self.room.status = RoomStatus.OCCUPIED
        with self.assertRaises(ValueError):
            self.hotel.book(self.guest, self.room, nights=1)

    def test_check_in_and_out(self) -> None:
        """Повний цикл: бронювання → заселення → виселення."""
        booking = self.hotel.book(self.guest, self.room, nights=2)
        self.assertEqual(self.room.status, RoomStatus.RESERVED)

        self.hotel.check_in_guest(booking)
        self.assertEqual(self.room.status, RoomStatus.OCCUPIED)

        self.hotel.check_out_guest(booking)
        self.assertEqual(self.room.status, RoomStatus.FREE)

    def test_total_revenue(self) -> None:
        """Дохід рахується правильно."""
        room2 = DeluxeRoom(201)
        self.hotel.add_room(room2)

        self.hotel.book(self.guest, self.room, nights=2)  # 800 * 2

        contact2 = Contact("Марія", "m@ex.com", "+380509999999", "ВВ999999")
        guest2 = Guest(contact=contact2, birthday=date(1985, 1, 1))
        self.hotel.book(guest2, room2, nights=3)  # 1500 * 3

        expected = 800 * 2 + 1500 * 3
        self.assertEqual(self.hotel.total_revenue(), expected)


class TestHotelMagicMethods(unittest.TestCase):
    """Тести магічних методів."""

    def test_len(self) -> None:
        """__len__ повертає кількість номерів."""
        hotel = Hotel("H")
        self.assertEqual(len(hotel), 0)
        hotel.add_room(StandardRoom(1))
        self.assertEqual(len(hotel), 1)

    def test_str(self) -> None:
        """__str__ містить назву та кількість."""
        hotel = Hotel("Grand")
        hotel.add_room(StandardRoom(1))
        result = str(hotel)
        self.assertIn("Grand", result)
        self.assertIn("1 номерів", result)
        self.assertIn("1 вільних", result)

    def test_repr(self) -> None:
        """__repr__ містить назву."""
        hotel = Hotel("Grand")
        self.assertIn("Grand", repr(hotel))


if __name__ == "__main__":
    unittest.main()
