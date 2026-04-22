import unittest
from datetime import date

from models.amenity import Amenity
from models.contact import Contact
from models.enums import RoomStatus
from models.guest import Guest
from models.room import Room, StandardRoom, DeluxeRoom, Suite
from constants.amenity import WIFI, TV, MINI_BAR, AIR_CONDITIONING, SAFE


class TestRoomABC(unittest.TestCase):
    """Перевіряємо, що Room — абстрактний клас і не створюється напряму."""

    def test_cannot_instantiate_room(self):
        """Room — абстрактний, створити його напряму не можна."""
        with self.assertRaises(TypeError):
            Room(number=1, price_per_night=500.0)


class _RoomTestBase(unittest.TestCase):
    """Базовий клас-хелпер з загальними об'єктами для тестів."""

    def setUp(self) -> None:
        self.contact = Contact(
            name="Іван Перепилиця",
            email="ivan@gmail.com",
            phone="+3349853454",
            passport="AX044844",
        )
        self.guest = Guest(contact=self.contact, birthday=date(1990, 5, 15))


# ───────────────────── StandardRoom ─────────────────────


class TestStandardRoomInit(_RoomTestBase):
    """Ініціалізація StandardRoom."""

    def test_defaults(self):
        """Стандартний номер створюється з правильними значеннями за замовчуванням."""
        room = StandardRoom(number=101)
        self.assertEqual(room.number, 101)
        self.assertEqual(room.price_per_night, 800.0)
        self.assertEqual(room.status, RoomStatus.FREE)
        self.assertEqual(len(room.amenities), 2)
        self.assertIn(WIFI, room.amenities)
        self.assertIn(TV, room.amenities)
        self.assertIn("стандартний", room.description.lower())

    def test_custom_values(self):
        """Стандартний номер можна створити з кастомними параметрами."""
        custom_amenities = [WIFI]
        room = StandardRoom(
            number=102,
            price_per_night=900.0,
            amenities=custom_amenities,
            description="Особливий номер",
            status=RoomStatus.RESERVED,
        )
        self.assertEqual(room.price_per_night, 900.0)
        self.assertEqual(room.amenities, custom_amenities)
        self.assertEqual(room.description, "Особливий номер")
        self.assertEqual(room.status, RoomStatus.RESERVED)


class TestStandardRoomValidation(_RoomTestBase):
    """Валідація параметрів StandardRoom."""

    def test_invalid_number_zero(self):
        """Номер кімнати 0 — невалідний."""
        with self.assertRaises(ValueError):
            StandardRoom(number=0)

    def test_invalid_number_negative(self):
        """Від'ємний номер кімнати — невалідний."""
        with self.assertRaises(ValueError):
            StandardRoom(number=-5)

    def test_invalid_number_type(self):
        """Номер кімнати має бути цілим числом."""
        with self.assertRaises(TypeError):
            StandardRoom(number="101")

    def test_invalid_price_zero(self):
        """Ціна 0 — невалідна."""
        with self.assertRaises(ValueError):
            StandardRoom(number=101, price_per_night=0)

    def test_invalid_price_negative(self):
        """Від'ємна ціна — невалідна."""
        with self.assertRaises(ValueError):
            StandardRoom(number=101, price_per_night=-100)

    def test_invalid_price_type(self):
        """Ціна має бути числом."""
        with self.assertRaises(TypeError):
            StandardRoom(number=101, price_per_night="дорого")


class TestStandardRoomGetInfo(_RoomTestBase):
    """Метод get_info() у StandardRoom."""

    def test_get_info_format(self):
        """get_info() повертає рядок у правильному форматі."""
        room = StandardRoom(number=101)
        info = room.get_info()
        self.assertIn("Стандарт №101", info)
        self.assertIn("800.0 грн/ніч", info)
        self.assertIn("Зручності:", info)


# ───────────────────── DeluxeRoom ─────────────────────


class TestDeluxeRoomInit(_RoomTestBase):
    """Ініціалізація DeluxeRoom."""

    def test_defaults(self):
        """Делюкс-номер створюється з правильними значеннями за замовчуванням."""
        room = DeluxeRoom(number=201)
        self.assertEqual(room.price_per_night, 1500.0)
        self.assertEqual(len(room.amenities), 5)
        self.assertIn(MINI_BAR, room.amenities)
        self.assertIn(AIR_CONDITIONING, room.amenities)
        self.assertIn(SAFE, room.amenities)

    def test_get_info_format(self):
        """get_info() повертає рядок у правильному форматі."""
        room = DeluxeRoom(number=201)
        info = room.get_info()
        self.assertIn("Делюкс №201", info)
        self.assertIn("1500.0 грн/ніч", info)


# ───────────────────── Suite ─────────────────────


class TestSuiteInit(_RoomTestBase):
    """Ініціалізація Suite."""

    def test_defaults(self):
        """Люкс-номер створюється з правильними значеннями за замовчуванням."""
        room = Suite(number=301)
        self.assertEqual(room.price_per_night, 3000.0)
        self.assertEqual(len(room.amenities), 9)

    def test_get_info_format(self):
        """get_info() повертає рядок у правильному форматі."""
        room = Suite(number=301)
        info = room.get_info()
        self.assertIn("Люкс №301", info)
        self.assertIn("3000.0 грн/ніч", info)


# ───────────────────── check_in / check_out ─────────────────────


class TestCheckIn(_RoomTestBase):
    """Заселення гостя у номер."""

    def test_check_in_free(self):
        """Можна заселити у вільний номер."""
        room = StandardRoom(number=101)
        room.check_in(self.guest)
        self.assertEqual(room.status, RoomStatus.OCCUPIED)

    def test_check_in_reserved(self):
        """Можна заселити у зарезервований номер."""
        room = StandardRoom(number=101, status=RoomStatus.RESERVED)
        room.check_in(self.guest)
        self.assertEqual(room.status, RoomStatus.OCCUPIED)

    def test_check_in_occupied_raises(self):
        """Не можна заселити у зайнятий номер."""
        room = StandardRoom(number=101, status=RoomStatus.OCCUPIED)
        with self.assertRaises(ValueError) as ctx:
            room.check_in(self.guest)
        self.assertIn("Неможливо заселити", str(ctx.exception))


class TestCheckOut(_RoomTestBase):
    """Виселення гостя з номера."""

    def test_check_out_occupied(self):
        """Можна виселити із зайнятого номера."""
        room = StandardRoom(number=101, status=RoomStatus.OCCUPIED)
        room.check_out()
        self.assertEqual(room.status, RoomStatus.FREE)

    def test_check_out_free_raises(self):
        """Не можна виселити з вільного номера."""
        room = StandardRoom(number=101)
        with self.assertRaises(ValueError) as ctx:
            room.check_out()
        self.assertIn("Неможливо виселити", str(ctx.exception))

    def test_check_out_reserved_raises(self):
        """Не можна виселити із зарезервованого номера."""
        room = StandardRoom(number=101, status=RoomStatus.RESERVED)
        with self.assertRaises(ValueError) as ctx:
            room.check_out()
        self.assertIn("Неможливо виселити", str(ctx.exception))


# ───────────────────── магічні методи ─────────────────────


class TestRoomMagicMethods(_RoomTestBase):
    """__eq__, __repr__, __str__ для Room."""

    def test_eq_same_number(self):
        """Номери з однаковим number — рівні."""
        room1 = StandardRoom(number=101)
        room2 = DeluxeRoom(number=101)
        self.assertEqual(room1, room2)

    def test_eq_different_number(self):
        """Номери з різними number — нерівні."""
        room1 = StandardRoom(number=101)
        room2 = StandardRoom(number=102)
        self.assertNotEqual(room1, room2)

    def test_eq_not_room(self):
        """Порівняння з не-Room повертає NotImplemented."""
        room = StandardRoom(number=101)
        self.assertEqual(room.__eq__("not a room"), NotImplemented)

    def test_repr(self):
        """repr() містить клас, номер, ціну і статус."""
        room = StandardRoom(number=101)
        r = repr(room)
        self.assertIn("StandardRoom", r)
        self.assertIn("101", r)
        self.assertIn("FREE", r)

    def test_str_delegates_to_get_info(self):
        """str() повертає те саме, що get_info()."""
        room = StandardRoom(number=101)
        self.assertEqual(str(room), room.get_info())


# ───────────────────── незалежність за замовчуванням ─────────────────────


class TestDefaultAmenitiesIsolation(unittest.TestCase):
    """Зміна amenities одного номера не впливає на інший."""

    def test_mutation_isolation(self):
        """Додавання зручності до одного номера не змінює інший."""
        room1 = StandardRoom(number=101)
        room2 = StandardRoom(number=102)
        room1.amenities.append(Amenity("Тест", "Тестова зручність"))
        self.assertEqual(len(room2.amenities), 2)


if __name__ == "__main__":
    unittest.main()
