from abc import ABC, abstractmethod

from constants.amenity import (
    WIFI, TV, MINI_BAR, AIR_CONDITIONING,
    JACUZZI, LIVING_ROOM, SAFE, BATHROBES, ROOM_SERVICE,
)
from models.amenity import Amenity
from models.enums import RoomStatus
from models.guest import Guest
from utils.data_utils import register_class
from utils.validators import validate_positive_float, validate_positive_int


class Room(ABC):
    """Абстрактний базовий клас номера готелю.

    Атрибути:
        number: Номер кімнати (ціле додатне).
        price_per_night: Ціна за одну ніч (> 0).
        status: Поточний статус номера.
        amenities: Список зручностей у номері.
        description: Текстовий опис номера.
    """

    def __init__(
        self,
        number: int,
        price_per_night: float,
        amenities: list[Amenity] | None = None,
        description: str = "",
        status: RoomStatus = RoomStatus.FREE,
        photos: list[str] | None = None,
    ) -> None:
        self.number: int = validate_positive_int(number, "Номер кімнати")
        self.price_per_night: float = validate_positive_float(
            price_per_night, "Ціна за ніч"
        )
        self.status: RoomStatus = status
        self.amenities: list[Amenity] = amenities if amenities is not None else []
        self.description: str = description
        self.photos: list[str] = photos if photos is not None else []

    # ---------- бізнес-логіка ----------

    def check_in(self, guest: Guest) -> None:
        """Заселити гостя у номер.

        Args:
            guest: Гість, якого заселяємо.

        Raises:
            ValueError: Якщо номер не вільний і не зарезервований.
        """
        if self.status not in (RoomStatus.FREE, RoomStatus.RESERVED):
            raise ValueError(
                f"Неможливо заселити гостя — номер №{self.number} "
                f"має статус «{self.status}»"
            )
        self.status = RoomStatus.OCCUPIED
        print(f"✅ Гостя {guest} заселено у номер №{self.number}")

    def check_out(self) -> None:
        """Виселити гостя з номера.

        Raises:
            ValueError: Якщо номер не зайнятий.
        """
        if self.status != RoomStatus.OCCUPIED:
            raise ValueError(
                f"Неможливо виселити — номер №{self.number} "
                f"має статус «{self.status}»"
            )
        self.status = RoomStatus.FREE
        print(f"🔓 Номер №{self.number} тепер вільний")

    # ---------- абстрактний метод ----------

    @abstractmethod
    def get_info(self) -> str:
        raise NotImplementedError
        """Повертає текстовий опис номера (реалізується у підкласах)."""

    # ---------- магічні методи ----------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Room):
            return NotImplemented
        return self.number == other.number

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(number={self.number}, "
            f"price_per_night={self.price_per_night}, "
            f"status={self.status.name})"
        )

    def __str__(self) -> str:
        return self.get_info()


@register_class
class StandardRoom(Room):
    """Стандартний номер готелю.

    Значення за замовчуванням:
        - Ціна: 800 грн/ніч
        - Зручності: Wi-Fi, TV
    """

    DEFAULT_PRICE: float = 800.0
    DEFAULT_DESCRIPTION: str = (
        "Затишний стандартний номер з усім необхідним для комфортного відпочинку"
    )
    DEFAULT_AMENITIES: list[Amenity] = [WIFI, TV]

    def __init__(
        self,
        number: int,
        price_per_night: float = DEFAULT_PRICE,
        amenities: list[Amenity] | None = None,
        description: str = DEFAULT_DESCRIPTION,
        status: RoomStatus = RoomStatus.FREE,
        photos: list[str] | None = None,
    ) -> None:
        super().__init__(
            number=number,
            price_per_night=price_per_night,
            amenities=(
                amenities if amenities is not None
                else list(self.DEFAULT_AMENITIES)
            ),
            description=description,
            status=status,
            photos=photos,
        )

    def get_info(self) -> str:
        """Повертає опис стандартного номера."""
        amenities_str = ", ".join(str(a) for a in self.amenities)
        return (
            f"Стандарт №{self.number}, {self.price_per_night} грн/ніч — "
            f"{self.description}. Зручності: {amenities_str}"
        )




@register_class
class DeluxeRoom(Room):
    """Номер підвищеного комфорту (Делюкс).

    Значення за замовчуванням:
        - Ціна: 1500 грн/ніч
        - Зручності: Wi-Fi, TV, Міні-бар, Кондиціонер, Сейф
    """

    DEFAULT_PRICE: float = 1500.0
    DEFAULT_DESCRIPTION: str = (
        "Просторий номер підвищеного комфорту з сучасним дизайном "
        "та додатковими зручностями"
    )
    DEFAULT_AMENITIES: list[Amenity] = [
        WIFI, TV, MINI_BAR, AIR_CONDITIONING, SAFE,
    ]

    def __init__(
        self,
        number: int,
        price_per_night: float = DEFAULT_PRICE,
        amenities: list[Amenity] | None = None,
        description: str = DEFAULT_DESCRIPTION,
        status: RoomStatus = RoomStatus.FREE,
        photos: list[str] | None = None,
    ) -> None:
        super().__init__(
            number=number,
            price_per_night=price_per_night,
            amenities=(
                amenities if amenities is not None
                else list(self.DEFAULT_AMENITIES)
            ),
            description=description,
            status=status,
            photos=photos,
        )

    def get_info(self) -> str:
        """Повертає опис делюкс-номера."""
        amenities_str = ", ".join(str(a) for a in self.amenities)
        return (
            f"Делюкс №{self.number}, {self.price_per_night} грн/ніч — "
            f"{self.description}. Зручності: {amenities_str}"
        )


@register_class
class Suite(Room):
    """Розкішний люкс-номер.

    Значення за замовчуванням:
        - Ціна: 3000 грн/ніч
        - Зручності: Wi-Fi, TV, Міні-бар, Кондиціонер, Джакузі,
          Вітальня, Сейф, Халати, Рум-сервіс
    """

    DEFAULT_PRICE: float = 3000.0
    DEFAULT_DESCRIPTION: str = (
        "Розкішний люкс-номер з окремою вітальнею, джакузі та панорамним видом"
    )
    DEFAULT_AMENITIES: list[Amenity] = [
        WIFI, TV, MINI_BAR, AIR_CONDITIONING,
        JACUZZI, LIVING_ROOM, SAFE, BATHROBES, ROOM_SERVICE,
    ]

    def __init__(
        self,
        number: int,
        price_per_night: float = DEFAULT_PRICE,
        amenities: list[Amenity] | None = None,
        description: str = DEFAULT_DESCRIPTION,
        status: RoomStatus = RoomStatus.FREE,
        photos: list[str] | None = None,
    ) -> None:
        super().__init__(
            number=number,
            price_per_night=price_per_night,
            amenities=(
                amenities if amenities is not None
                else list(self.DEFAULT_AMENITIES)
            ),
            description=description,
            status=status,
            photos=photos,
        )

    def get_info(self) -> str:
        """Повертає опис люкс-номера."""
        amenities_str = ", ".join(str(a) for a in self.amenities)
        return (
            f"Люкс №{self.number}, {self.price_per_night} грн/ніч — "
            f"{self.description}. Зручності: {amenities_str}"
        )

