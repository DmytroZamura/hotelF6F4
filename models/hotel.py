"""Модуль класу Hotel — менеджер готелю."""

from datetime import date

from models.booking import Booking
from models.enums import RoomStatus
from models.guest import Guest
from models.room import Room
from utils.data_utils import register_class
from utils.validators import validate_non_empty_string, validate_type


@register_class
class Hotel:
    """Готель — об'єднує номери, бронювання та гостей.

    Атрибути:
        name: Назва готелю.
        rooms: Список номерів готелю.
        bookings: Список усіх бронювань.
    """

    def __init__(
        self,
        name: str,
        rooms: list[Room] | None = None,
        bookings: list[Booking] | None = None,
        photos: list[str] | None = None,
    ) -> None:
        self.name: str = validate_non_empty_string(name, "Назва готелю")
        self.rooms: list[Room] = rooms if rooms is not None else []
        self.bookings: list[Booking] = bookings if bookings is not None else []
        self.photos: list[str] = photos if photos is not None else []

    # ---------- управління номерами ----------

    def add_room(self, room: Room) -> None:
        """Додати номер до готелю.

        Args:
            room: Номер для додавання.

        Raises:
            TypeError: Якщо room не є екземпляром Room.
            ValueError: Якщо номер з таким number вже існує.
        """
        validate_type(room, Room, "Номер")
        if room in self.rooms:
            raise ValueError(
                f"Номер №{room.number} вже існує у готелі «{self.name}»"
            )
        self.rooms.append(room)

    # ---------- пошук ----------

    def find_available(self, room_type: type[Room] | None = None) -> list[Room]:
        """Повернути список вільних номерів.

        Args:
            room_type: Якщо задано — фільтрує за типом (StandardRoom, DeluxeRoom, Suite).

        Returns:
            Список вільних номерів.
        """
        return [
            r for r in self.rooms
            if r.status == RoomStatus.FREE
            and (room_type is None or isinstance(r, room_type))
        ]

    # ---------- бронювання ----------

    def book(
        self,
        guest: Guest,
        room: Room,
        nights: int,
        check_in_date: date | None = None,
    ) -> Booking:
        """Створити бронювання для гостя.

        Args:
            guest: Гість.
            room: Номер для бронювання.
            nights: Кількість ночей.
            check_in_date: Дата заїзду (за замовчуванням — сьогодні).

        Returns:
            Створене бронювання.

        Raises:
            ValueError: Якщо номер не вільний або не належить готелю.
        """
        if room not in self.rooms:
            raise ValueError(
                f"Номер №{room.number} не належить готелю «{self.name}»"
            )
        actual_date: date = check_in_date if check_in_date is not None else date.today()

        booking = Booking(
            guest=guest,
            room=room,
            check_in_date=actual_date,
            nights=nights,
        )
        self.bookings.append(booking)
        return booking

    # ---------- заселення / виселення ----------

    def check_in_guest(self, booking: Booking) -> None:
        """Заселити гостя за бронюванням.

        Args:
            booking: Бронювання, за яким заселяємо.
        """
        booking.room.check_in(booking.guest)

    def check_out_guest(self, booking: Booking) -> None:
        """Виселити гостя за бронюванням.

        Args:
            booking: Бронювання, за яким виселяємо.
        """
        booking.room.check_out()

    # ---------- фінанси ----------

    def total_revenue(self) -> float:
        """Сумарний дохід по всіх бронюваннях.

        Returns:
            Загальна сума доходів (грн).
        """
        return sum(b.total_cost() for b in self.bookings)

    # ---------- магічні методи ----------

    def __len__(self) -> int:
        """Загальна кількість номерів у готелі."""
        return len(self.rooms)

    def __str__(self) -> str:
        free_count = len(self.find_available())
        return (
            f"Готель '{self.name}': {len(self.rooms)} номерів, "
            f"{free_count} вільних"
        )

    def __repr__(self) -> str:
        return f"Hotel(name='{self.name}')"

