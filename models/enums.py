from enum import Enum


class RoomStatus(Enum):
    """Статус номера готелю."""

    FREE = "free"
    OCCUPIED = "occupied"
    RESERVED = "reserved"

    def __str__(self) -> str:
        labels = {
            RoomStatus.FREE: "Вільний",
            RoomStatus.OCCUPIED: "Зайнятий",
            RoomStatus.RESERVED: "Зарезервований",
        }
        return labels[self]
