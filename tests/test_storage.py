"""Тести для HotelStorage — збереження та завантаження даних готелю."""

import json
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

from models.amenity import Amenity
from models.booking import Booking
from models.contact import Contact
from models.enums import RoomStatus
from models.guest import Guest
from models.hotel import Hotel
from models.room import StandardRoom, DeluxeRoom, Suite
from services.storage import HotelStorage


class TestHotelStorage(unittest.TestCase):
    """Тести сервісу HotelStorage."""

    def setUp(self) -> None:
        """Створює тимчасову директорію та тестові дані."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = HotelStorage(base_dir=self.temp_dir)

        # Тестовий готель
        self.hotel = Hotel(name="Grand Hotel")
        self.room1 = StandardRoom(number=101)
        self.room2 = DeluxeRoom(number=201)
        self.room3 = Suite(number=301)
        self.hotel.add_room(self.room1)
        self.hotel.add_room(self.room2)
        self.hotel.add_room(self.room3)

        # Тестовий гість
        self.contact = Contact(
            name="Іван Петренко",
            email="ivan@test.com",
            phone="+380501234567",
            passport="АА123456",
        )
        self.guest = Guest(contact=self.contact, birthday=date(1990, 5, 15))

    def tearDown(self) -> None:
        """Видаляє тимчасову директорію."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # ---------- slugify ----------

    def test_slugify(self) -> None:
        """Перевіряє перетворення назви на slug."""
        self.assertEqual(HotelStorage._slugify("Grand Hotel"), "grand_hotel")
        self.assertEqual(HotelStorage._slugify("Sea Resort"), "sea_resort")
        self.assertEqual(HotelStorage._slugify("  Test  "), "test")

    # ---------- save / load ----------

    def test_save_creates_files(self) -> None:
        """save() створює директорію та hotel.json."""
        self.storage.save(self.hotel)

        hotel_dir = Path(self.temp_dir) / "grand_hotel"
        self.assertTrue(hotel_dir.exists())
        self.assertTrue((hotel_dir / "hotel.json").exists())

    def test_save_updates_registry(self) -> None:
        """save() додає slug у registry.json."""
        self.storage.save(self.hotel)

        registry_path = Path(self.temp_dir) / "registry.json"
        self.assertTrue(registry_path.exists())
        with open(registry_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("grand_hotel", data["hotels"])

    def test_save_no_duplicate_in_registry(self) -> None:
        """Повторний save() не дублює slug у реєстрі."""
        self.storage.save(self.hotel)
        self.storage.save(self.hotel)

        slugs = self.storage.list_hotels()
        self.assertEqual(slugs.count("grand_hotel"), 1)

    def test_load_restores_hotel(self) -> None:
        """load() відновлює готель з правильною назвою та номерами."""
        self.storage.save(self.hotel)
        loaded = self.storage.load("grand_hotel")

        self.assertEqual(loaded.name, "Grand Hotel")
        self.assertEqual(len(loaded.rooms), 3)

    def test_load_restores_room_types(self) -> None:
        """load() відновлює правильні типи номерів."""
        self.storage.save(self.hotel)
        loaded = self.storage.load("grand_hotel")

        types = [type(r).__name__ for r in loaded.rooms]
        self.assertIn("StandardRoom", types)
        self.assertIn("DeluxeRoom", types)
        self.assertIn("Suite", types)

    def test_load_restores_room_prices(self) -> None:
        """load() відновлює ціни номерів."""
        self.storage.save(self.hotel)
        loaded = self.storage.load("grand_hotel")

        prices = {r.number: r.price_per_night for r in loaded.rooms}
        self.assertEqual(prices[101], 800.0)
        self.assertEqual(prices[201], 1500.0)
        self.assertEqual(prices[301], 3000.0)

    def test_round_trip_with_booking(self) -> None:
        """Round-trip: save → load зберігає бронювання."""
        booking = self.hotel.book(
            guest=self.guest,
            room=self.room1,
            nights=3,
            check_in_date=date(2026, 5, 1),
        )
        self.storage.save(self.hotel)
        loaded = self.storage.load("grand_hotel")

        self.assertEqual(len(loaded.bookings), 1)
        b = loaded.bookings[0]
        self.assertEqual(b.nights, 3)
        self.assertEqual(b.guest.contact.passport, "АА123456")

    def test_booking_room_reference(self) -> None:
        """Після load() бронювання посилається на номер з hotel.rooms."""
        self.hotel.book(
            guest=self.guest,
            room=self.room1,
            nights=2,
            check_in_date=date(2026, 6, 1),
        )
        self.storage.save(self.hotel)
        loaded = self.storage.load("grand_hotel")

        # room у booking має бути тим самим об'єктом, що й у hotel.rooms
        loaded_room_101 = next(r for r in loaded.rooms if r.number == 101)
        self.assertIs(loaded.bookings[0].room, loaded_room_101)

    def test_load_nonexistent_raises(self) -> None:
        """load() кидає FileNotFoundError для неіснуючого готелю."""
        with self.assertRaises(FileNotFoundError):
            self.storage.load("неіснуючий_готель")

    # ---------- load_all / list_hotels ----------

    def test_list_hotels(self) -> None:
        """list_hotels() повертає slug-и всіх збережених готелів."""
        self.storage.save(self.hotel)

        hotel2 = Hotel(name="Sea Resort")
        hotel2.add_room(StandardRoom(number=100))
        self.storage.save(hotel2)

        slugs = self.storage.list_hotels()
        self.assertEqual(len(slugs), 2)
        self.assertIn("grand_hotel", slugs)
        self.assertIn("sea_resort", slugs)

    def test_load_all(self) -> None:
        """load_all() завантажує всі готелі."""
        self.storage.save(self.hotel)
        hotel2 = Hotel(name="Sea Resort")
        hotel2.add_room(StandardRoom(number=100))
        self.storage.save(hotel2)

        hotels = self.storage.load_all()
        self.assertEqual(len(hotels), 2)
        names = {h.name for h in hotels}
        self.assertEqual(names, {"Grand Hotel", "Sea Resort"})

    # ---------- delete ----------

    def test_delete_removes_dir_and_registry(self) -> None:
        """delete() видаляє директорію і slug з реєстру."""
        self.storage.save(self.hotel)
        self.storage.delete("grand_hotel")

        self.assertFalse((Path(self.temp_dir) / "grand_hotel").exists())
        self.assertNotIn("grand_hotel", self.storage.list_hotels())

    def test_delete_nonexistent_raises(self) -> None:
        """delete() кидає FileNotFoundError для відсутнього готелю."""
        with self.assertRaises(FileNotFoundError):
            self.storage.delete("неіснуючий")

    # ---------- медіафайли ----------

    def test_ensure_media_dirs(self) -> None:
        """save() створює медіа-директорії для готелю та номерів."""
        self.storage.save(self.hotel)

        media_dir = Path(self.temp_dir) / "grand_hotel" / "media"
        self.assertTrue((media_dir / "hotel").exists())
        self.assertTrue((media_dir / "rooms" / "101").exists())
        self.assertTrue((media_dir / "rooms" / "201").exists())
        self.assertTrue((media_dir / "rooms" / "301").exists())

    def test_add_and_get_hotel_photo(self) -> None:
        """Додавання та отримання фото готелю."""
        self.storage.save(self.hotel)

        # Створюємо тимчасове фото
        tmp_photo = Path(self.temp_dir) / "facade.jpg"
        tmp_photo.write_text("fake image")

        result = self.storage.add_hotel_photo("grand_hotel", str(tmp_photo))
        self.assertTrue(result.exists())

        photos = self.storage.get_hotel_photos("grand_hotel")
        self.assertEqual(len(photos), 1)
        self.assertEqual(photos[0].name, "facade.jpg")

    def test_add_and_get_room_photo(self) -> None:
        """Додавання та отримання фото номера."""
        self.storage.save(self.hotel)

        tmp_photo = Path(self.temp_dir) / "room_main.png"
        tmp_photo.write_text("fake image")

        result = self.storage.add_room_photo("grand_hotel", 101, str(tmp_photo))
        self.assertTrue(result.exists())

        photos = self.storage.get_room_photos("grand_hotel", 101)
        self.assertEqual(len(photos), 1)

    def test_invalid_photo_extension(self) -> None:
        """Непідтримуваний формат фото кидає ValueError."""
        tmp_photo = Path(self.temp_dir) / "file.gif"
        tmp_photo.write_text("fake")

        with self.assertRaises(ValueError):
            self.storage.add_hotel_photo("grand_hotel", str(tmp_photo))

    def test_delete_photo(self) -> None:
        """delete_photo() видаляє файл."""
        self.storage.save(self.hotel)
        tmp_photo = Path(self.temp_dir) / "test.jpg"
        tmp_photo.write_text("fake")

        dest = self.storage.add_hotel_photo("grand_hotel", str(tmp_photo))
        self.storage.delete_photo(str(dest))
        self.assertFalse(dest.exists())

    def test_delete_photo_nonexistent(self) -> None:
        """delete_photo() кидає FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            self.storage.delete_photo("/неіснуючий/шлях.jpg")

    def test_get_photos_empty(self) -> None:
        """get_hotel_photos() повертає порожній список, якщо немає фото."""
        self.storage.save(self.hotel)
        self.assertEqual(self.storage.get_hotel_photos("grand_hotel"), [])
        self.assertEqual(self.storage.get_room_photos("grand_hotel", 101), [])


if __name__ == "__main__":
    unittest.main()
