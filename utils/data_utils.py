"""Універсальні утиліти серіалізації/десеріалізації об'єктів у JSON."""

from datetime import date
from enum import Enum
from typing import Any
import json

# Реєстр класів — щоб dict_to_class знав, який клас створювати
_CLASS_REGISTRY: dict[str, type] = {}


def register_class(cls: type) -> Any:
    """Реєструє клас для десеріалізації.

    Використовується як декоратор або викликається вручну.
    Після реєстрації dict_to_class зможе відновити об'єкт цього класу.

    Args:
        cls: Клас для реєстрації.

    Returns:
        Той самий клас (зручно як декоратор).
    """
    _CLASS_REGISTRY[cls.__name__] = cls
    return cls


def obj_to_dict(obj: Any) -> Any:
    """Рекурсивно конвертує об'єкт у dict/list для JSON-серіалізації.

    Додає поле ``__class__`` з назвою класу для подальшого відновлення.
    Не мутує оригінальний об'єкт — працює з копією ``__dict__``.

    Args:
        obj: Будь-який об'єкт (модель, список, примітив).

    Returns:
        dict, list або примітивне значення, готове для json.dump.
    """
    # Список — обробляємо кожен елемент
    if isinstance(obj, list):
        return [obj_to_dict(item) for item in obj]

    # Enum — зберігаємо значення та клас
    if isinstance(obj, Enum):
        return {
            "value": obj.value,
            "__class__": type(obj).__name__,
        }

    # date — зберігаємо компоненти
    if isinstance(obj, date):
        return {
            "year": obj.year,
            "month": obj.month,
            "day": obj.day,
            "__class__": "date",
        }

    # Примітивні типи (str, int, float, bool, None) — повертаємо як є
    if not hasattr(obj, "__dict__"):
        return obj

    # Об'єкт з __dict__ — робимо копію, щоб не мутувати оригінал
    result = dict(obj.__dict__)
    result["__class__"] = type(obj).__name__

    for key, value in result.items():
        if key == "__class__":
            continue
        if isinstance(value, list):
            result[key] = [obj_to_dict(item) for item in value]
        elif isinstance(value, Enum):
            result[key] = obj_to_dict(value)
        elif isinstance(value, date):
            result[key] = obj_to_dict(value)
        elif hasattr(value, "__dict__"):
            result[key] = obj_to_dict(value)

    return result


def dict_to_class(data: Any) -> Any:
    """Рекурсивно відновлює об'єкт із dict за збереженим ``__class__``.

    Шукає клас у реєстрі ``_CLASS_REGISTRY``. Для ``date`` та ``Enum``
    використовує спеціальну логіку.

    Args:
        data: dict, list або примітив із JSON.

    Returns:
        Відновлений об'єкт відповідного класу.

    Raises:
        KeyError: Якщо клас не зареєстрований у реєстрі.
    """
    if isinstance(data, list):
        return [dict_to_class(item) for item in data]

    if not isinstance(data, dict):
        return data

    class_name = data.pop("__class__", '')
    if class_name == '':
        return data

    # date — спеціальна обробка
    if class_name == "date":
        return date(year=data["year"], month=data["month"], day=data["day"])

    # Шукаємо клас у реєстрі
    if class_name not in _CLASS_REGISTRY:
        raise KeyError(
            f"Клас '{class_name}' не зареєстрований. "
            f"Використайте register_class({class_name}) перед десеріалізацією."
        )

    target_class = _CLASS_REGISTRY[class_name]

    # Enum — відновлюємо за значенням
    if issubclass(target_class, Enum):
        return target_class(data["value"])

    # Рекурсивно відновлюємо вкладені об'єкти
    for key, value in data.items():
        if isinstance(value, list):
            data[key] = [dict_to_class(item) for item in value]
        elif isinstance(value, dict) and "__class__" in value:
            data[key] = dict_to_class(value)

    # Якщо клас підтримує прапорець _deserializing — вмикаємо його,
    # щоб конструктор пропустив побічні ефекти (наприклад, зміну статусу)
    has_flag = hasattr(target_class, "_deserializing")
    if has_flag:
        target_class._deserializing = True
    try:
        return target_class(**data)
    finally:
        if has_flag:
            target_class._deserializing = False


def save_data(file_path: str, data_object: Any) -> None:
    """Серіалізує об'єкт і записує у JSON-файл.

    Args:
        file_path: Шлях до файлу.
        data_object: Об'єкт для збереження.
    """
    dict_to_save = obj_to_dict(data_object)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(dict_to_save, f, ensure_ascii=False, indent=4)


def read_data(file_path: str) -> Any:
    """Зчитує JSON-файл і повертає відновлений об'єкт.

    Args:
        file_path: Шлях до файлу.

    Returns:
        Відновлений об'єкт (або dict/list, якщо ``__class__`` відсутній).

    Raises:
        FileNotFoundError: Якщо файл не знайдено.
        json.JSONDecodeError: Якщо файл містить невалідний JSON.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return dict_to_class(data)
