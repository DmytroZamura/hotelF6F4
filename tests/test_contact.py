import unittest

from models.contact import Contact


class TestContact(unittest.TestCase):
    def setUp(self):
        self.contact = Contact(
            name="Іван Перепилиця",
            email="ivan.p@gmail.com",
            phone="+3349853454",
            passport="AX044844"
        )
        self.base_parameters = {
            "name": "Василь Швидкий",
            "email": "v@gnail.com",
            "phone": "+33496653454",
            "passport": "AX03454"
        }

    def test_init(self):
        """Тестування ініціалізації Contact з валідними даними."""
        self.assertIsInstance(self.contact, Contact)
        self.assertEqual(self.contact.name, "Іван Перепилиця")
        self.assertEqual(self.contact.email, "ivan.p@gmail.com")
        self.assertEqual(self.contact.phone, "+3349853454")
        self.assertEqual(self.contact.passport, "AX044844")

    def test_str(self):
        """Тестування рядкового представлення Contact."""
        expected_str = "Контакт: Іван Перепилиця, Email: ivan.p@gmail.com, Телефон: +3349853454, Паспорт: AX044844"
        self.assertEqual(str(self.contact), expected_str)

    def test_repr(self):
        """Тестування офіційного представлення Contact."""
        expected_repr = "Contact(name='Іван Перепилиця', email='ivan.p@gmail.com', phone='+3349853454', passport='AX044844')"
        self.assertEqual(repr(self.contact), expected_repr)

    def test_eq(self):
        """Тестуємо порівняння двох Contact за паспортом."""
        contact2 = Contact(**{**self.base_parameters, "passport": "AX044844"})

        self.assertEqual(contact2, self.contact)
        self.assertEqual(self.contact == contact2, True)

        contact3 = Contact(
            **self.base_parameters,
        )

        self.assertNotEqual(contact3, self.contact)
        self.assertEqual(self.contact == contact3, False)

    def test_empty_or_wrong_type_name_validation(self):
        """Тестування валідації порожнього імені при створенні Contact."""
        with self.assertRaises(ValueError) as context:
            Contact(**{**self.base_parameters, "name": ""})
        self.assertIn("Ім'я контакту не може бути порожнім", str(context.exception))

        with self.assertRaises(TypeError) as context:
            Contact(**{**self.base_parameters, "name": 12123412})
            self.assertIn("Ім'я контакту має бути типу str", str(context.exception))

    def test_invalid_email_validation(self):
        """Тестування валідації невалідного email при створенні Contact."""
        with self.assertRaises(ValueError) as context:
            Contact(**{**self.base_parameters, "email": "invalid-email"})
        self.assertIn("Невалідна email адреса", str(context.exception))

        with self.assertRaises(TypeError) as context:
            Contact(**{**self.base_parameters, "email": 12312})

    def test_invalid_phone_validation(self):
        with self.assertRaises(ValueError) as context:
            Contact(**{**self.base_parameters, "phone": "invalid-phone"})
            self.assertIn("Номер телефона має бути від 8 до 15 цифр, може починатися с '+'", str(context.exception))

    def test_invalid_passport_validation(self):
        """Тестування валідації """
        with self.assertRaises(ValueError) as context:
            Contact(**{**self.base_parameters, "passport": ""})


if __name__ == "__main__":
    unittest.main()
