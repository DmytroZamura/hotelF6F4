"""Модуль бронювання номера готелю."""

from datetime import date, timedelta

from models.guest import Guest
from models.room import Room
from models.enums import RoomStatus
from utils.data_utils import register_class
from utils.validators import validate_positive_int, validate_type, validate_date_not_past


@register_class
class Booking:
    """Бронювання номера готелю.

    Атрибути:
        guest: Гість, який бронює номер.
        room: Номер, що бронюється.
        check_in_date: Дата заїзду.
        nights: Кількість ночей (>= 1).
    """

    # Прапорець для пропуску валідації при десеріалізації
    _deserializing: bool = False

    def __init__(
        self,
        guest: Guest,
        room: Room,
        check_in_date: date,
        nights: int,
    ) -> None:
        self.guest: Guest = validate_type(guest, Guest, "Гість")
        self.room: Room = validate_type(room, Room, "Номер")
        self.nights: int = validate_positive_int(nights, "Кількість ночей")
        self.check_in_date: date = validate_type(check_in_date, date, "Дата заїзду")

        if not Booking._deserializing:
            validate_date_not_past(check_in_date, "Дата заїзду")
            if self.room.status != RoomStatus.FREE:
                raise ValueError(
                    f"Неможливо забронювати номер №{self.room.number} — "
                    f"він має статус «{self.room.status}»"
                )
            self.room.status = RoomStatus.RESERVED

    # ---------- властивості ----------

    @property
    def check_out_date(self) -> date:
        """Дата виїзду (розраховується автоматично)."""
        return self.check_in_date + timedelta(days=self.nights)

    def total_cost(self) -> float:
        """Повна вартість бронювання.

        Returns:
            Вартість = ціна за ніч × кількість ночей.
        """
        return self.room.price_per_night * self.nights

    # ---------- магічні методи ----------

    def __repr__(self) -> str:
        return (
            f"Booking(guest='{self.guest.contact.name}', "
            f"room=№{self.room.number}, "
            f"{self.check_in_date} → {self.check_out_date}, "
            f"total={self.total_cost()})"
        )

    def __str__(self) -> str:
        return (
            f"Бронювання: {self.guest.contact.name}, "
            f"номер №{self.room.number}, "
            f"{self.check_in_date} → {self.check_out_date} "
            f"({self.nights} ноч.), "
            f"вартість: {self.total_cost()} грн"
        )




