from models.contact import Contact
from utils.validators import validate_type
from datetime import date


class Guest:
    """Клас, для гостя готелю."""

    def __init__(self, contact: Contact, birthday: date) -> None:
        self.contact = validate_type(contact, Contact, "Контакт гостя")
        self.birthday = validate_type(birthday, date, "Дата народження гостя")

    def __repr__(self) -> str:
        return f"Guest(contact={self.contact!r}, birthday={self.birthday!r})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Guest):
            return NotImplemented
        return self.contact == other.contact

    def __str__(self) -> str:
        return f"Гість: {str(self.contact)}, Дата народження: {self.birthday}"