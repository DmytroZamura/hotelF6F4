def validate_non_empty_string(value: str, field_name: str) -> str:
    """Перевірити, що рядок не порожній, і повернути stripped версію.

    Args:
        value: Значення для перевірки.
        field_name: Назва поля (для повідомлення про помилку).
    Returns:
        Очищений рядок (stripped).
    Raises:
        ValueError: Якщо рядок порожній або складається лише з пробілів.
    """
    if not isinstance(value, str):
        raise TypeError(f"{field_name} має бути рядком")

    if not value or not value.strip():
        raise ValueError(f"{field_name} не може бути порожнім")
    return value.strip()

def validate_positive_int(value: int, field_name: str) -> int:
    """Перевірити, що значення — ціле додатне число (> 0).

    Raises:
        ValueError: Якщо значення не int або <= 0.
    """
    if not isinstance(value, int):
        raise TypeError(f"{field_name} має бути цілим числом")

    if value <= 0:
        raise ValueError(f"{field_name} повинно бути цілим додатним числом")
    return value

def validate_min_int(value: int, minimum: int, field_name: str) -> int:
    """Перевірити, що ціле значення >= minimum.

    Raises:
        ValueError: Якщо значення не int або < minimum.
    """
    if not isinstance(value, int):
        raise TypeError(f"{field_name} має бути цілим числом")

    if value < minimum:
        raise ValueError(f"{field_name} повинно бути >= {minimum}")
    return value


def validate_positive_float(value: float, field_name: str) -> float:
    """Перевірити, що числове значення > 0.

    Raises:
        ValueError: Якщо значення <= 0.
    """
    if not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} має бути числом")

    if value <= 0:
        raise ValueError(f"{field_name} повинно бути більше 0")
    return float(value)


def validate_range(value: float, low: float, high: float, field_name: str) -> float:
    """Перевірити, що значення знаходиться в діапазоні [low, high].

    Raises:
        ValueError: Якщо значення поза діапазоном.
    """
    if not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} має бути числом")

    if not (low <= value <= high):
        raise ValueError(f"{field_name} в діапазоні від {low} до {high}")
    return float(value)



def validate_email(email: str) -> str:
    """Перевірити, що рядок є валидным email.

    Raises:
        ValueError: Если строка не является валидным email.
    """
    email = validate_non_empty_string(email, "Email")
    if "@" not in email or "." not in email:
        raise ValueError("Невалідна email адреса")
    return email

def validate_phone_number(phone: str) -> str:
    """Перевірити, що рядок є валидным номером телефона.

    Raises:
        ValueError: Если строка не является валидным номером телефона.
    """
    phone = validate_non_empty_string(phone, "Номер телефона")
    if len(phone) < 8 or not phone.replace("+", "").isdigit() or len(phone) > 15:
        raise ValueError("Номер телефона має бути від 8 до 15 цифр, може починатися с '+'")
    return phone


def validate_date_not_past(value: "date", field_name: str = "Дата") -> "date":
    """Перевірити, що дата не в минулому.

    Args:
        value: Значення для перевірки.
        field_name: Назва поля (для повідомлення про помилку).

    Returns:
        Валідна дата.

    Raises:
        TypeError: Якщо значення не є типом date.
        ValueError: Якщо дата в минулому.
    """
    from datetime import date
    if not isinstance(value, date):
        raise TypeError(f"{field_name} має бути типу date")
    if value < date.today():
        raise ValueError(f"{field_name} не може бути в минулому")
    return value


def validate_type(value, expected_type, field_name: str):
    """Перевірити, що значення має ожидаемый тип.

    Raises:
        TypeError: Если значение не имеет ожидаемого типа.
    """
    if not isinstance(value, expected_type):
        raise TypeError(f"{field_name} має бути типу {expected_type.__name__}")
    return value