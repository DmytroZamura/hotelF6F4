from utils.data_utils import register_class
from utils.validators import validate_non_empty_string


@register_class
class Amenity:
    """Клас для додавання зручностей до готелю"""
    def __init__(self, name: str, description: str) -> None:
        self.name = validate_non_empty_string(name, "Назва зручності")
        self.description = validate_non_empty_string(description, "Опис зручності")

    def __repr__(self) -> str:
        return f"Amenity(name={self.name!r}, description={self.description!r})"

    def __str__(self) -> str:
        return f"Amenity(name={self.name!r}, description={self.description!r})"

    def __hash__(self) -> int:
        return hash(self.name)