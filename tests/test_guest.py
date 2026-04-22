import unittest
from datetime import date

from models.contact import Contact
from models.guest import Guest


class TestGuest(unittest.TestCase):
    def setUp(self):
        self.contact = Contact(
            name="Іван Перепилиця",
            email="ivan.p@gmail.com",
            phone="+3349853454",
            passport="AX044844"
        )
        self.guest = Guest(
            contact=self.contact,
            birthday=date(1990, 5, 15)
        )

    def test_init(self):
        """Тестування ініціалізації Guest з валідними даними."""
        self.assertIsInstance(self.guest, Guest)
        self.assertEqual(self.guest.contact, self.contact)
        self.assertEqual(self.guest.birthday, date(1990, 5, 15))

    def test_str(self):
        """Тестування рядкового представлення Guest."""
        expected_str = (
            f"Гість: {str(self.contact)}, Дата народження: 1990-05-15"
        )
        self.assertEqual(str(self.guest), expected_str)

    def test_repr(self):
        """Тестування офіційного представлення Guest."""
        expected_repr = f"Guest(contact={self.contact!r}, birthday={self.guest.birthday!r})"
        self.assertEqual(repr(self.guest), expected_repr)

    def test_eq_same_contact(self):
        """Тестуємо порівняння двох Guest з однаковим контактом (паспортом)."""
        contact2 = Contact(
            name="Інше Ім'я",
            email="other@gmail.com",
            phone="+3809991234",
            passport="AX044844"  # той самий паспорт
        )
        guest2 = Guest(contact=contact2, birthday=date(1985, 1, 1))
        self.assertEqual(self.guest, guest2)

    def test_eq_different_contact(self):
        """Тестуємо порівняння двох Guest з різними контактами."""
        contact2 = Contact(
            name="Василь Швидкий",
            email="v@gmail.com",
            phone="+3809991234",
            passport="BX099999"
        )
        guest2 = Guest(contact=contact2, birthday=date(1990, 5, 15))
        self.assertNotEqual(self.guest, guest2)

    def test_eq_not_guest(self):
        """Тестуємо порівняння Guest з об'єктом іншого типу."""
        self.assertEqual(self.guest.__eq__("not a guest"), NotImplemented)

    def test_invalid_contact_type(self):
        """Тестування валідації: contact має бути типу Contact."""
        with self.assertRaises(TypeError) as context:
            Guest(contact="not a contact", birthday=date(1990, 5, 15))
        self.assertIn("Контакт гостя має бути типу Contact", str(context.exception))

    def test_invalid_contact_none(self):
        """Тестування валідації: contact не може бути None."""
        with self.assertRaises(TypeError) as context:
            Guest(contact=None, birthday=date(1990, 5, 15))
        self.assertIn("Контакт гостя має бути типу Contact", str(context.exception))

    def test_invalid_birthday_type(self):
        """Тестування валідації: birthday має бути типу date."""
        with self.assertRaises(TypeError) as context:
            Guest(contact=self.contact, birthday="1990-05-15")
        self.assertIn("Дата народження гостя має бути типу date", str(context.exception))

    def test_invalid_birthday_int(self):
        """Тестування валідації: birthday не може бути цілим числом."""
        with self.assertRaises(TypeError) as context:
            Guest(contact=self.contact, birthday=19900515)
        self.assertIn("Дата народження гостя має бути типу date", str(context.exception))

    def test_invalid_birthday_none(self):
        """Тестування валідації: birthday не може бути None."""
        with self.assertRaises(TypeError) as context:
            Guest(contact=self.contact, birthday=None)
        self.assertIn("Дата народження гостя має бути типу date", str(context.exception))


if __name__ == "__main__":
    unittest.main()
