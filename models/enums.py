from enum import Enum

from utils.data_utils import register_class


@register_class
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
