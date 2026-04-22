"""Тести для генератора HTML-звітів."""

import os
import shutil
import unittest
from datetime import date
from pathlib import Path

from models.contact import Contact
from models.enums import RoomStatus
from models.guest import Guest
from models.hotel import Hotel
from models.room import StandardRoom, DeluxeRoom
from services.report import HotelReportGenerator
from services.storage import HotelStorage


class TestHotelReportGenerator(unittest.TestCase):
    """Тести для HotelReportGenerator."""

    def setUp(self) -> None:
        """Створюємо тестові дані перед кожним тестом."""
        self.test_data_dir = "test_report_data"
        self.test_reports_dir = "test_reports"
        self.storage = HotelStorage(base_dir=self.test_data_dir)

        # Створюємо готель із номерами
        self.hotel = Hotel(name="Тестовий Готель")
        self.hotel.add_room(StandardRoom(101))
        self.hotel.add_room(DeluxeRoom(201))

        # Зберігаємо, щоб створити директорії медіа
        self.storage.save(self.hotel)
        self.slug = self.storage._slugify(self.hotel.name)

        self.generator = HotelReportGenerator(
            template_dir="templates",
            output_dir=self.test_reports_dir,
        )

    def tearDown(self) -> None:
        """Прибираємо тестові файли."""
        for d in (self.test_data_dir, self.test_reports_dir):
            if os.path.exists(d):
                shutil.rmtree(d)

    def test_generate_creates_html_file(self) -> None:
        """Перевіряємо, що генерується HTML-файл."""
        result = self.generator.generate(self.hotel, self.slug, self.storage)
        self.assertTrue(result.exists(), "HTML-файл має існувати")
        self.assertTrue(result.name.endswith(".html"))

    def test_generate_html_contains_hotel_name(self) -> None:
        """HTML має містити назву готелю."""
        result = self.generator.generate(self.hotel, self.slug, self.storage)
        content = result.read_text(encoding="utf-8")
        self.assertIn("Тестовий Готель", content)

    def test_generate_html_contains_room_numbers(self) -> None:
        """HTML має містити номери кімнат."""
        result = self.generator.generate(self.hotel, self.slug, self.storage)
        content = result.read_text(encoding="utf-8")
        self.assertIn("101", content)
        self.assertIn("201", content)

    def test_generate_copies_css(self) -> None:
        """CSS-файл має бути скопійований у директорію звітів."""
        self.generator.generate(self.hotel, self.slug, self.storage)
        css_path = Path(self.test_reports_dir) / "style.css"
        self.assertTrue(css_path.exists(), "style.css має існувати у reports/")

    def test_generate_all(self) -> None:
        """generate_all має повернути список шляхів."""
        paths = self.generator.generate_all([self.hotel], self.storage)
        self.assertEqual(len(paths), 1)
        self.assertTrue(paths[0].exists())

    def test_generate_shows_status(self) -> None:
        """HTML має відображати статуси номерів."""
        result = self.generator.generate(self.hotel, self.slug, self.storage)
        content = result.read_text(encoding="utf-8")
        self.assertIn("Вільний", content)


class TestMediaIntegration(unittest.TestCase):
    """Тести інтеграції медіа у моделі."""

    def test_room_has_photos_attribute(self) -> None:
        """Room має мати атрибут photos."""
        room = StandardRoom(101)
        self.assertIsInstance(room.photos, list)
        self.assertEqual(len(room.photos), 0)

    def test_hotel_has_photos_attribute(self) -> None:
        """Hotel має мати атрибут photos."""
        hotel = Hotel(name="Тест")
        self.assertIsInstance(hotel.photos, list)
        self.assertEqual(len(hotel.photos), 0)

    def test_load_populates_photos(self) -> None:
        """Після load() фото мають заповнюватися зі списку медіа."""
        test_dir = "test_media_integration"
        try:
            storage = HotelStorage(base_dir=test_dir)
            hotel = Hotel(name="Медіа Тест")
            hotel.add_room(StandardRoom(101))
            storage.save(hotel)

            slug = storage._slugify(hotel.name)

            # Створюємо фейкове фото
            photo_dir = Path(test_dir) / slug / "media" / "hotel"
            fake_photo = photo_dir / "test.jpg"
            fake_photo.write_bytes(b"\xff\xd8fake")

            room_photo_dir = Path(test_dir) / slug / "media" / "rooms" / "101"
            fake_room_photo = room_photo_dir / "room.jpg"
            fake_room_photo.write_bytes(b"\xff\xd8fake")

            loaded = storage.load(slug)
            self.assertTrue(len(loaded.photos) > 0, "Фото готелю мають завантажитися")
            self.assertTrue(len(loaded.rooms[0].photos) > 0, "Фото номера мають завантажитися")
        finally:
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)


if __name__ == "__main__":
    unittest.main()
