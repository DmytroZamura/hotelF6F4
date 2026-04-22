"""Сервіс генерації HTML-звітів про готель."""

import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from models.enums import RoomStatus
from models.hotel import Hotel
from models.room import Room
from services.storage import HotelStorage


# Маппінг класів номерів на українські назви
_ROOM_TYPE_LABELS: dict[str, str] = {
    "StandardRoom": "Стандарт",
    "DeluxeRoom": "Делюкс",
    "Suite": "Люкс",
}


class HotelReportGenerator:
    """Генератор HTML-звітів для готелів.

    Атрибути:
        template_dir: Каталог із Jinja2-шаблонами.
        output_dir: Каталог для збереження згенерованих звітів.
    """

    def __init__(
        self,
        template_dir: str = "templates",
        output_dir: str = "reports",
    ) -> None:
        self.template_dir: Path = Path(template_dir)
        self.output_dir: Path = Path(output_dir)
        self._env: Environment = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True,
        )

    # ---------- допоміжні ----------

    @staticmethod
    def _room_type_label(room: Room) -> str:
        """Повертає українську назву типу номера."""
        return _ROOM_TYPE_LABELS.get(type(room).__name__, type(room).__name__)

    @staticmethod
    def _find_guest_for_room(hotel: Hotel, room: Room) -> str | None:
        """Знаходить ім'я гостя, який зараз проживає у номері."""
        if room.status != RoomStatus.OCCUPIED:
            return None
        for booking in hotel.bookings:
            if booking.room.number == room.number:
                return booking.guest.contact.name
        return None

    # ---------- генерація ----------

    def generate(
        self,
        hotel: Hotel,
        hotel_slug: str,
        storage: HotelStorage,
    ) -> Path:
        """Генерує HTML-звіт для одного готелю.

        Args:
            hotel: Об'єкт готелю.
            hotel_slug: Slug готелю (для шляхів до медіа).
            storage: Сервіс збереження (для отримання фото).

        Returns:
            Шлях до згенерованого HTML-файлу.
        """
        # Підготовка статистики
        total = len(hotel.rooms)
        free = sum(1 for r in hotel.rooms if r.status == RoomStatus.FREE)
        occupied = sum(1 for r in hotel.rooms if r.status == RoomStatus.OCCUPIED)
        reserved = sum(1 for r in hotel.rooms if r.status == RoomStatus.RESERVED)
        revenue = hotel.total_revenue()

        # Відносні шляхи до фото (щоб працювало у браузері)
        hotel_photos_rel = [
            str(Path("..") / p.relative_to(Path.cwd()))
            if p.is_absolute() else str(Path("..") / p)
            for p in storage.get_hotel_photos(hotel_slug)
        ]
        hotel.photos = hotel_photos_rel

        # Дані для кожного номера
        rooms_data: list[dict] = []
        for room in hotel.rooms:
            room_photos_rel = [
                str(Path("..") / p.relative_to(Path.cwd()))
                if p.is_absolute() else str(Path("..") / p)
                for p in storage.get_room_photos(hotel_slug, room.number)
            ]
            room.photos = room_photos_rel
            rooms_data.append({
                "room": room,
                "type": self._room_type_label(room),
                "current_guest": self._find_guest_for_room(hotel, room),
            })

        # Рендеримо шаблон
        template = self._env.get_template("hotel.html")
        html = template.render(
            hotel=hotel,
            total=total,
            free=free,
            occupied=occupied,
            reserved=reserved,
            revenue=revenue,
            rooms_data=rooms_data,
        )

        # Зберігаємо результат
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_file = self.output_dir / f"{hotel_slug}.html"
        output_file.write_text(html, encoding="utf-8")

        # Копіюємо CSS
        css_src = self.template_dir / "style.css"
        if css_src.exists():
            shutil.copy2(css_src, self.output_dir / "style.css")

        return output_file

    def generate_all(
        self,
        hotels: list[Hotel],
        storage: HotelStorage,
    ) -> list[Path]:
        """Генерує звіти для всіх готелів.

        Args:
            hotels: Список готелів.
            storage: Сервіс збереження.

        Returns:
            Список шляхів до згенерованих HTML-файлів.
        """
        paths: list[Path] = []
        for hotel in hotels:
            slug = storage._slugify(hotel.name)
            paths.append(self.generate(hotel, slug, storage))
        return paths

