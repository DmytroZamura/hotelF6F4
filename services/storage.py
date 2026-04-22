"""Сервіс збереження та завантаження даних готелю у JSON."""

import json
import re
import shutil
from pathlib import Path
from typing import Any

from models.hotel import Hotel
from utils.data_utils import obj_to_dict, dict_to_class, save_data, read_data

# Підтримувані формати фото
ALLOWED_PHOTO_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".webp"}


class HotelStorage:
    """Сервіс для збереження/завантаження готелів у файлову систему.

    Кожен готель зберігається в окремій директорії ``data/{slug}/``.
    Реєстр усіх готелів — у ``data/registry.json``.

    Атрибути:
        base_dir: Кореневий каталог для всіх даних готелів.
    """

    def __init__(self, base_dir: str = "data") -> None:
        self.base_dir: Path = Path(base_dir)

    # ========== slug ==========

    @staticmethod
    def _slugify(name: str) -> str:
        """Перетворює назву готелю на slug (lowercase, пробіли → _).

        Args:
            name: Назва готелю.

        Returns:
            slug-рядок, наприклад ``"grand_hotel"``.
        """
        slug = name.strip().lower()
        # Замінюємо пробіли та спецсимволи на підкреслення
        slug = re.sub(r"[^\w]+", "_", slug)
        # Прибираємо зайві підкреслення на початку/кінці
        return slug.strip("_")

    def _get_hotel_dir(self, hotel: Hotel) -> Path:
        """Повертає шлях до директорії готелю.

        Args:
            hotel: Об'єкт готелю.

        Returns:
            ``Path`` до ``data/{slug}/``.
        """
        return self.base_dir / self._slugify(hotel.name)

    # ========== registry.json ==========

    def _registry_path(self) -> Path:
        """Шлях до файлу реєстру."""
        return self.base_dir / "registry.json"

    def _read_registry(self) -> list[str]:
        """Зчитує список slug-ів із registry.json.

        Якщо файл не існує — повертає порожній список.
        """
        path = self._registry_path()
        if not path.exists():
            return []
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("hotels", [])

    def _write_registry(self, slugs: list[str]) -> None:
        """Записує список slug-ів у registry.json."""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        with open(self._registry_path(), "w", encoding="utf-8") as f:
            json.dump({"hotels": slugs}, f, ensure_ascii=False, indent=2)

    # ========== save ==========

    def save(self, hotel: Hotel) -> None:
        """Зберігає готель у файлову систему.

        Створює директорію ``data/{slug}/`` та записує:
        - ``hotel.json`` — повні дані готелю (номери, бронювання).

        Оновлює ``registry.json``.

        Args:
            hotel: Готель для збереження.
        """
        slug = self._slugify(hotel.name)
        hotel_dir = self.base_dir / slug
        hotel_dir.mkdir(parents=True, exist_ok=True)

        # Зберігаємо дані готелю
        save_data(str(hotel_dir / "hotel.json"), hotel)

        # Оновлюємо реєстр
        registry = self._read_registry()
        if slug not in registry:
            registry.append(slug)
            self._write_registry(registry)

        # Створюємо структуру медіа-директорій
        self._ensure_media_dirs(slug, hotel)

    # ========== load ==========

    def load(self, hotel_slug: str) -> Hotel:
        """Завантажує готель за slug-ом.

        Args:
            hotel_slug: Slug готелю (наприклад, ``"grand_hotel"``).

        Returns:
            Відновлений об'єкт ``Hotel``.

        Raises:
            FileNotFoundError: Якщо директорію або файл готелю не знайдено.
            json.JSONDecodeError: Якщо файл містить невалідний JSON.
        """
        hotel_dir = self.base_dir / hotel_slug
        hotel_file = hotel_dir / "hotel.json"

        if not hotel_file.exists():
            raise FileNotFoundError(
                f"Готель '{hotel_slug}' не знайдено — "
                f"файл {hotel_file} відсутній"
            )

        try:
            hotel = read_data(str(hotel_file))
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Пошкоджений файл готелю '{hotel_slug}': {e.msg}",
                e.doc,
                e.pos,
            )

        # Зв'язуємо бронювання з номерами готелю —
        # після десеріалізації room у booking є окремою копією,
        # потрібно замінити на той самий об'єкт із hotel.rooms
        rooms_by_number = {r.number: r for r in hotel.rooms}
        for booking in hotel.bookings:
            if booking.room.number in rooms_by_number:
                booking.room = rooms_by_number[booking.room.number]

        # Заповнюємо фото готелю та номерів з медіа-директорій
        hotel.photos = [
            str(p) for p in self.get_hotel_photos(hotel_slug)
        ]
        for room in hotel.rooms:
            room.photos = [
                str(p) for p in self.get_room_photos(hotel_slug, room.number)
            ]

        return hotel

    def load_all(self) -> list[Hotel]:
        """Завантажує всі готелі з реєстру.

        Returns:
            Список об'єктів ``Hotel``.
        """
        slugs = self._read_registry()
        return [self.load(slug) for slug in slugs]

    def list_hotels(self) -> list[str]:
        """Повертає список slug-ів зареєстрованих готелів.

        Returns:
            Список рядків — slug-ів.
        """
        return self._read_registry()

    # ========== delete ==========

    def delete(self, hotel_slug: str) -> None:
        """Видаляє готель: його директорію та запис у реєстрі.

        Args:
            hotel_slug: Slug готелю для видалення.

        Raises:
            FileNotFoundError: Якщо готель не знайдено в реєстрі.
        """
        registry = self._read_registry()
        if hotel_slug not in registry:
            raise FileNotFoundError(
                f"Готель '{hotel_slug}' не знайдено в реєстрі"
            )

        # Видаляємо директорію
        hotel_dir = self.base_dir / hotel_slug
        if hotel_dir.exists():
            shutil.rmtree(hotel_dir)

        # Оновлюємо реєстр
        registry.remove(hotel_slug)
        self._write_registry(registry)

    # ========== медіафайли ==========

    def _ensure_media_dirs(self, hotel_slug: str, hotel: Hotel) -> None:
        """Створює структуру медіа-директорій для готелю.

        Args:
            hotel_slug: Slug готелю.
            hotel: Об'єкт готелю (для отримання номерів кімнат).
        """
        media_dir = self.base_dir / hotel_slug / "media"
        (media_dir / "hotel").mkdir(parents=True, exist_ok=True)
        for room in hotel.rooms:
            (media_dir / "rooms" / str(room.number)).mkdir(
                parents=True, exist_ok=True
            )

    @staticmethod
    def _validate_photo_extension(photo_path: str) -> None:
        """Перевіряє, що формат фото підтримується.

        Raises:
            ValueError: Якщо розширення файлу не підтримується.
        """
        ext = Path(photo_path).suffix.lower()
        if ext not in ALLOWED_PHOTO_EXTENSIONS:
            raise ValueError(
                f"Непідтримуваний формат фото '{ext}'. "
                f"Дозволені: {', '.join(sorted(ALLOWED_PHOTO_EXTENSIONS))}"
            )

    def add_hotel_photo(self, hotel_slug: str, photo_path: str) -> Path:
        """Копіює фото у директорію медіа готелю.

        Args:
            hotel_slug: Slug готелю.
            photo_path: Шлях до файлу фото.

        Returns:
            Шлях до скопійованого файлу.
        """
        self._validate_photo_extension(photo_path)
        dest_dir = self.base_dir / hotel_slug / "media" / "hotel"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / Path(photo_path).name
        shutil.copy2(photo_path, dest)
        return dest

    def add_room_photo(
        self, hotel_slug: str, room_number: int, photo_path: str
    ) -> Path:
        """Копіює фото у директорію номера.

        Args:
            hotel_slug: Slug готелю.
            room_number: Номер кімнати.
            photo_path: Шлях до файлу фото.

        Returns:
            Шлях до скопійованого файлу.
        """
        self._validate_photo_extension(photo_path)
        dest_dir = (
            self.base_dir / hotel_slug / "media" / "rooms" / str(room_number)
        )
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / Path(photo_path).name
        shutil.copy2(photo_path, dest)
        return dest

    def get_hotel_photos(self, hotel_slug: str) -> list[Path]:
        """Повертає список фото готелю.

        Args:
            hotel_slug: Slug готелю.

        Returns:
            Список шляхів до фото.
        """
        photo_dir = self.base_dir / hotel_slug / "media" / "hotel"
        if not photo_dir.exists():
            return []
        return sorted(
            p for p in photo_dir.iterdir()
            if p.is_file() and p.suffix.lower() in ALLOWED_PHOTO_EXTENSIONS
        )

    def get_room_photos(self, hotel_slug: str, room_number: int) -> list[Path]:
        """Повертає список фото конкретного номера.

        Args:
            hotel_slug: Slug готелю.
            room_number: Номер кімнати.

        Returns:
            Список шляхів до фото.
        """
        photo_dir = (
            self.base_dir / hotel_slug / "media" / "rooms" / str(room_number)
        )
        if not photo_dir.exists():
            return []
        return sorted(
            p for p in photo_dir.iterdir()
            if p.is_file() and p.suffix.lower() in ALLOWED_PHOTO_EXTENSIONS
        )

    def delete_photo(self, photo_path: str) -> None:
        """Видаляє фото за шляхом.

        Args:
            photo_path: Шлях до фото для видалення.

        Raises:
            FileNotFoundError: Якщо файл не знайдено.
        """
        path = Path(photo_path)
        if not path.exists():
            raise FileNotFoundError(f"Фото не знайдено: {photo_path}")
        path.unlink()


