from utils.data_utils import register_class
from utils.validators import validate_non_empty_string, validate_email, validate_phone_number


@register_class
class Contact:
    """Клас для представлення контактної інформації користувача."""

    def __init__(self, name: str, email: str, phone: str, passport: str):
        self.name = validate_non_empty_string(name, "Ім'я контакту")
        self.email = validate_email(email)
        self.phone = validate_phone_number(phone)
        self.passport = validate_non_empty_string(passport, "Номер паспорта")

    def __repr__(self):
        """Офіційне представлення Contact для розробників."""
        return f"Contact(name={self.name!r}, email={self.email!r}, phone={self.phone!r}, passport={self.passport!r})"

    def __str__(self):
        return f"Контакт: {self.name}, Email: {self.email}, Телефон: {self.phone}, Паспорт: {self.passport}"

    def __eq__(self, other):
        if not isinstance(other, Contact):
            return NotImplemented
        return self.passport == other.passport
