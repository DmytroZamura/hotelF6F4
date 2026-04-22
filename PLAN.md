# 🏨 Система управління готелем — План реалізації

## Загальний огляд

Спрощена система обліку номерів готелю: бронювання, заселення/виселення гостей, облік доходів.

---

## Архітектура проєкту

```
hotelF6F4/
├── main.py                # Точка входу, демонстрація роботи системи
├── models/
│   ├── __init__.py
│   ├── enums.py           # Enum-статуси (FREE, OCCUPIED, RESERVED)
│   ├── guest.py           # Клас Guest
│   ├── amenity.py         # Клас Amenity (зручність номера)
│   ├── room.py            # Room (ABC), StandardRoom, DeluxeRoom, Suite
│   ├── booking.py         # Клас Booking
│   └── hotel.py           # Клас Hotel
├── services/
│   ├── __init__.py
│   ├── loyalty.py         # Система лояльності та знижок
│   ├── storage.py         # Збереження/завантаження даних у JSON
│   └── report.py          # Генерація HTML-звітів про готель
├── templates/
│   ├── hotel.html         # Jinja2-шаблон сторінки готелю
│   ├── room.html          # Шаблон картки номера
│   └── style.css          # Стилі для HTML-звітів
├── data/                      # Кореневий каталог даних
│   ├── grand_hotel/           # Директорія для кожного готелю (назва = slug)
│   │   ├── hotel.json         # Основні дані готелю (номери, статуси)
│   │   ├── guests.json        # Гості, пов'язані з цим готелем
│   │   ├── bookings.json      # Бронювання
│   │   └── media/             # Медіафайли готелю
│   │       ├── hotel/         # Фото самого готелю (фасад, лобі, ресторан…)
│   │       │   ├── facade.jpg
│   │       │   └── lobby.jpg
│   │       └── rooms/         # Фото номерів (папка = номер кімнати)
│   │           ├── 101/
│   │           │   ├── main.jpg
│   │           │   └── bathroom.jpg
│   │           └── 201/
│   │               └── main.jpg
│   ├── sea_resort/
│   │   ├── hotel.json
│   │   ├── guests.json
│   │   ├── bookings.json
│   │   └── media/
│   │       ├── hotel/
│   │       └── rooms/
│   └── registry.json          # Реєстр усіх готелів (список slug-ів)
├── reports/                   # Згенеровані HTML-звіти (автогенеровані)
│   ├── grand_hotel.html
│   └── sea_resort.html
├── tests/
│   ├── __init__.py
│   ├── test_guest.py
│   ├── test_rooms.py
│   ├── test_booking.py
│   ├── test_hotel.py
│   ├── test_storage.py
│   └── test_report.py
├── PLAN.md                # Цей файл
└── requirements.txt
```

---

## Ітерація 1 — Фундамент: Enum, Guest, Room (ABC)

### Мета
Створити базові сутності системи без бізнес-логіки бронювання.

### Завдання

#### 1.1 `models/enums.py` — Статуси номера
- [ ] `RoomStatus(Enum)`: `FREE`, `OCCUPIED`, `RESERVED`

#### 1.2 `models/guest.py` — Клас гостя
- [ ] Атрибути: `name: str`, `passport: str`, `contact: str`
- [ ] Валідація: всі поля — непорожні рядки
- [ ] `__str__` — повертає `"Гість: {name} (паспорт: {passport})"`
- [ ] `__repr__` — повертає `"Guest(name='{name}', passport='{passport}')"`
- [ ] `__eq__` — порівняння за номером паспорта

#### 1.3 `models/amenity.py` — Клас зручності
- [ ] Атрибути: `name: str`, `description: str`
- [ ] Валідація: `name` — непорожній рядок
- [ ] `__str__` — повертає `"{name}"`
- [ ] `__repr__` — повертає `"Amenity(name='{name}')"`
- [ ] `__eq__` — порівняння за `name`
- [ ] `__hash__` — для використання в множинах/словниках
- [ ] Готові константи (на рівні модуля):
  ```python
  WIFI = Amenity("Wi-Fi", "Безкоштовний бездротовий інтернет")
  TV = Amenity("TV", "Телевізор з кабельними каналами")
  MINI_BAR = Amenity("Міні-бар", "Міні-бар з напоями та снеками")
  AIR_CONDITIONING = Amenity("Кондиціонер", "Клімат-контроль у номері")
  JACUZZI = Amenity("Джакузі", "Гідромасажна ванна")
  LIVING_ROOM = Amenity("Вітальня", "Окрема вітальня зона")
  SAFE = Amenity("Сейф", "Персональний сейф у номері")
  BATHROBES = Amenity("Халати", "Махрові халати та капці")
  ROOM_SERVICE = Amenity("Рум-сервіс", "Цілодобове обслуговування у номері")
  ```

#### 1.4 `models/room.py` — Абстрактний клас номера та підкласи
- [ ] `Room(ABC)`:
  - Атрибути: `number: int`, `price_per_night: float`, `status: RoomStatus`, `amenities: list[Amenity]`, `description: str`
  - Валідація: `number` — ціле додатне, `price_per_night > 0`
  - `check_in(guest)` — змінює статус на `OCCUPIED`, друкує повідомлення; кидає виняток, якщо номер не `FREE`/`RESERVED`
  - `check_out()` — змінює статус на `FREE`, друкує повідомлення; кидає виняток, якщо номер не `OCCUPIED`
  - `get_info()` — **абстрактний метод**, повертає опис номера
  - `__eq__` — порівняння за `number`
  - `__repr__`
- [ ] `StandardRoom(Room)`:
  - Ціна за замовчуванням: **800 грн/ніч**
  - Опис за замовчуванням: `"Затишний стандартний номер з усім необхідним для комфортного відпочинку"`
  - Зручності за замовчуванням: `[WIFI, TV]`
  - `get_info()` → `"Стандарт №{number}, {price} грн/ніч — {description}. Зручності: {amenities}"`
- [ ] `DeluxeRoom(Room)`:
  - Ціна за замовчуванням: **1500 грн/ніч**
  - Опис за замовчуванням: `"Просторий номер підвищеного комфорту з сучасним дизайном та додатковими зручностями"`
  - Зручності за замовчуванням: `[WIFI, TV, MINI_BAR, AIR_CONDITIONING, SAFE]`
  - `get_info()` → `"Делюкс №{number}, {price} грн/ніч — {description}. Зручності: {amenities}"`
- [ ] `Suite(Room)`:
  - Ціна за замовчуванням: **3000 грн/ніч**
  - Опис за замовчуванням: `"Розкішний люкс-номер з окремою вітальнею, джакузі та панорамним видом"`
  - Зручності за замовчуванням: `[WIFI, TV, MINI_BAR, AIR_CONDITIONING, JACUZZI, LIVING_ROOM, SAFE, BATHROBES, ROOM_SERVICE]`
  - `get_info()` → `"Люкс №{number}, {price} грн/ніч — {description}. Зручності: {amenities}"`

### Критерії завершення ітерації
- Можна створити зручності, гостя і кімнати різних типів
- Кожен тип номера має опис та набір зручностей за замовчуванням
- `check_in` / `check_out` коректно змінюють статус
- Валідація не пропускає некоректні дані
- Юніт-тести: `test_guest.py`, `test_rooms.py` ✅

---

## Ітерація 2 — Бронювання: Booking

### Мета
Реалізувати сутність бронювання та прив'язати її до гостя і номера.

### Завдання

#### 2.1 `models/booking.py` — Клас бронювання
- [ ] Атрибути:
  - `guest: Guest`
  - `room: Room`
  - `check_in_date: date` (дата заїзду)
  - `nights: int` (кількість ночей, >= 1)
- [ ] Валідація: `nights >= 1`, `check_in_date` — не в минулому (або поточна дата)
- [ ] `total_cost() -> float` — `room.price_per_night * nights`
- [ ] `check_out_date` (property) — `check_in_date + timedelta(days=nights)`
- [ ] `__repr__` — `"Booking(guest='{name}', room=№{number}, {check_in} → {check_out}, total={cost})"`
- [ ] `__str__` — людиночитабельний опис бронювання
- [ ] При створенні бронювання номер переходить у статус `RESERVED`

### Критерії завершення ітерації
- Можна створити бронювання і розрахувати вартість
- Статус номера автоматично змінюється на `RESERVED`
- Юніт-тести: `test_booking.py` ✅

---

## Ітерація 3 — Готель: Hotel

### Мета
Зібрати все в єдиний клас-менеджер — `Hotel`.

### Завдання

#### 3.1 `models/hotel.py` — Клас готелю
- [ ] Атрибути:
  - `name: str` — назва готелю
  - `rooms: list[Room]` — колекція номерів
  - `bookings: list[Booking]` — список бронювань
- [ ] `add_room(room)` — додати номер до готелю (перевірка на дублікат за номером)
- [ ] `find_available(room_type: type = None) -> list[Room]` — повертає вільні номери; якщо `room_type` задано — фільтрує за типом
- [ ] `book(guest, room, nights, check_in_date=None) -> Booking` — створює бронювання, додає до списку; кидає виняток, якщо номер не вільний
- [ ] `check_in_guest(booking)` — заселяє гостя за бронюванням
- [ ] `check_out_guest(booking)` — виселяє гостя
- [ ] `total_revenue() -> float` — сумарний дохід по всіх бронюваннях
- [ ] `__len__` — загальна кількість номерів
- [ ] `__str__` — `"Готель '{name}': {n} номерів, {m} вільних"`

### Критерії завершення ітерації
- Повний цикл: створення готелю → додавання номерів → бронювання → заселення → виселення
- Облік доходів працює коректно
- Юніт-тести: `test_hotel.py` ✅

---

## Ітерація 4 — Додатковий функціонал

### Мета
Розширити систему: лояльність, знижки, історія.

### Завдання

#### 4.1 Система лояльності (`services/loyalty.py`)
- [ ] `LoyaltyProgram`:
  - Рівні: `BRONZE` (0–2 бронювання), `SILVER` (3–5), `GOLD` (6+)
  - Знижки: Bronze — 0%, Silver — 5%, Gold — 10%
  - `get_discount(guest) -> float` — повертає розмір знижки (0.0–0.1)
  - `get_level(guest) -> str` — повертає рівень лояльності

#### 4.2 Історія перебувань гостя
- [ ] У `Guest` додати `history: list[Booking]` — список завершених бронювань
- [ ] При `check_out` бронювання додається в історію гостя
- [ ] `Guest.total_spent() -> float` — скільки гість витратив загалом

#### 4.3 Інтеграція знижок у Booking
- [ ] `Booking.total_cost()` враховує знижку лояльності
- [ ] У `__repr__` / `__str__` відображається знижка, якщо є

#### 4.4 Збереження даних у JSON (`services/storage.py`)

##### Структура файлів — окрема директорія на кожен готель
```
data/
├── registry.json              # {"hotels": ["grand_hotel", "sea_resort"]}
├── grand_hotel/
│   ├── hotel.json             # Назва, список номерів зі статусами
│   ├── guests.json            # Гості цього готелю
│   ├── bookings.json          # Бронювання цього готелю
│   └── media/                 # Медіафайли
│       ├── hotel/             # Фото готелю (фасад, лобі…)
│       └── rooms/             # Фото номерів (папка = номер кімнати)
│           ├── 101/
│           └── 201/
└── sea_resort/
    ├── hotel.json
    ├── guests.json
    ├── bookings.json
    └── media/
        ├── hotel/
        └── rooms/
```

##### Серіалізація та десеріалізація — універсальні утиліти `utils/data_utils.py`

> **Замість** індивідуальних `to_dict()` / `from_dict()` у кожному класі використовуємо
> універсальні функції з `utils/data_utils.py`:
>
> - [x] `obj_to_dict(obj)` — рекурсивно конвертує будь-який об'єкт у `dict` через `__dict__`, додає поле `__class__` для відновлення типу.
> - [x] `dict_to_class(data)` — рекурсивно відновлює об'єкт із `dict` за збереженим `__class__`, викликаючи конструктор `TargetClass(**data)`.
> - [x] `save_data(file_path, data_object)` — серіалізує об'єкт і записує у JSON-файл (`ensure_ascii=False`, `indent=4`).
> - [x] `read_data(file_path)` — зчитує JSON-файл і повертає відновлений об'єкт.
>
> Це означає, що моделям (`Amenity`, `Guest`, `Room`, `Booking`, `Hotel`) **не потрібні** методи `to_dict()` та `from_dict()`.
> Єдина вимога — конструктор кожного класу має приймати всі атрибути як іменовані аргументи (`**kwargs`-сумісний).

##### `HotelStorage` — сервіс збереження/завантаження
- [ ] `__init__(base_dir: str = "data")` — кореневий каталог для всіх готелів
- [ ] `_get_hotel_dir(hotel: Hotel) -> Path` — повертає шлях до директорії готелю (`data/{slug}/`); slug формується з назви (транслітерація/lowercase, пробіли → `_`)
- [ ] `save(hotel: Hotel) -> None`:
  1. Створює директорію `data/{slug}/` якщо не існує
  2. Використовує `save_data()` з `utils/data_utils` для запису `hotel.json`, `guests.json`, `bookings.json`
  3. Оновлює `data/registry.json` — додає slug якщо його ще немає
- [ ] `load(hotel_slug: str) -> Hotel` — завантажує один готель за slug-ом:
  1. Використовує `read_data()` з `utils/data_utils` для зчитування JSON-файлів
  2. Об'єкти автоматично відновлюються у правильні класи через `dict_to_class()`
  3. Повертає повністю відновлений об'єкт `Hotel`
- [ ] `load_all() -> list[Hotel]` — завантажує всі готелі з `registry.json`
- [ ] `list_hotels() -> list[str]` — повертає список slug-ів зареєстрованих готелів
- [ ] `delete(hotel_slug: str) -> None` — видаляє директорію готелю та прибирає з реєстру
- [ ] Обробка помилок:
  - `FileNotFoundError` — готель не знайдено → зрозуміле повідомлення
  - `json.JSONDecodeError` — пошкоджений файл → логування + виняток
  - Відсутній `registry.json` → створюється автоматично

##### Формат файлів

`data/registry.json`:
```json
{
  "hotels": ["grand_hotel", "sea_resort"]
}
```

`data/grand_hotel/hotel.json`:
```json
{
  "name": "Grand Hotel",
  "rooms": [
    {
      "type": "StandardRoom",
      "number": 101,
      "price_per_night": 800.0,
      "status": "FREE",
      "description": "Затишний стандартний номер з усім необхідним для комфортного відпочинку",
      "amenities": [
        {"name": "Wi-Fi", "description": "Безкоштовний бездротовий інтернет"},
        {"name": "TV", "description": "Телевізор з кабельними каналами"}
      ]
    },
    {
      "type": "DeluxeRoom",
      "number": 201,
      "price_per_night": 1500.0,
      "status": "OCCUPIED",
      "description": "Просторий номер підвищеного комфорту з сучасним дизайном",
      "amenities": [
        {"name": "Wi-Fi", "description": "Безкоштовний бездротовий інтернет"},
        {"name": "TV", "description": "Телевізор з кабельними каналами"},
        {"name": "Міні-бар", "description": "Міні-бар з напоями та снеками"},
        {"name": "Кондиціонер", "description": "Клімат-контроль у номері"},
        {"name": "Сейф", "description": "Персональний сейф у номері"}
      ]
    }
  ]
}
```

`data/grand_hotel/guests.json`:
```json
{
  "guests": [
    {"name": "Іван Петренко", "passport": "АА123456", "contact": "+380501234567"}
  ]
}
```

`data/grand_hotel/bookings.json`:
```json
{
  "bookings": [
    {
      "guest_passport": "АА123456",
      "room_number": 201,
      "check_in_date": "2026-04-08",
      "nights": 3
    }
  ]
}
```

#### 4.5 Медіафайли готелю та номерів

##### Структура медіа
```
data/{slug}/media/
├── hotel/                 # Фото готелю
│   ├── facade.jpg         # Фасад
│   ├── lobby.jpg          # Лобі
│   └── restaurant.jpg     # Ресторан тощо
└── rooms/                 # Фото номерів (папка = номер кімнати)
    ├── 101/
    │   ├── main.jpg       # Головне фото
    │   ├── bathroom.jpg
    │   └── view.jpg
    └── 201/
        └── main.jpg
```

##### Робота з медіа у `HotelStorage`
- [ ] `_ensure_media_dirs(hotel_slug: str)` — створює структуру `media/hotel/` та `media/rooms/{room_number}/` для кожного номера при `save()`
- [ ] `add_hotel_photo(hotel_slug: str, photo_path: str) -> Path` — копіює фото у `data/{slug}/media/hotel/`, повертає шлях
- [ ] `add_room_photo(hotel_slug: str, room_number: int, photo_path: str) -> Path` — копіює фото у `data/{slug}/media/rooms/{room_number}/`, повертає шлях
- [ ] `get_hotel_photos(hotel_slug: str) -> list[Path]` — список усіх фото готелю
- [ ] `get_room_photos(hotel_slug: str, room_number: int) -> list[Path]` — список фото конкретного номера
- [ ] `delete_photo(photo_path: str) -> None` — видаляє фото
- [ ] Підтримувані формати: `.jpg`, `.jpeg`, `.png`, `.webp` — валідація при додаванні
- [ ] При `delete(hotel_slug)` видаляється вся директорія `media/` разом з готелем

##### Інтеграція медіа у моделі
- [ ] `Room.photos: list[str]` — список відносних шляхів до фото (заповнюється при `load()`)
- [ ] `Hotel.photos: list[str]` — фото самого готелю
- [ ] Поле `photos` серіалізується автоматично через `obj_to_dict()` — додаткові методи не потрібні

#### 4.6 Генерація HTML-звіту (`services/report.py`)

##### Залежність
- [ ] Додати `Jinja2` у `requirements.txt`

##### `HotelReportGenerator`
- [ ] `__init__(template_dir: str = "templates", output_dir: str = "reports")` — каталоги шаблонів та вихідних файлів
- [ ] `generate(hotel: Hotel, hotel_slug: str, storage: HotelStorage) -> Path`:
  1. Збирає дані: назва, номери, статуси, фото, бронювання, статистика
  2. Рендерить Jinja2-шаблон `templates/hotel.html`
  3. Копіює `templates/style.css` в `reports/` (або вбудовує inline)
  4. Зберігає результат у `reports/{slug}.html`
  5. Повертає шлях до згенерованого файлу
- [ ] `generate_all(hotels: list[Hotel], storage: HotelStorage) -> list[Path]` — генерує звіти для всіх готелів

##### Шаблони

`templates/hotel.html` — головна сторінка готелю:
- [ ] Назва готелю + галерея фото готелю
- [ ] Статистика: загальна кількість номерів, вільних, зайнятих, зарезервованих
- [ ] Загальний дохід
- [ ] Список номерів (кожен рендериться через `room.html`)

`templates/room.html` — картка номера (include-шаблон):
- [ ] Номер кімнати, тип, ціна за ніч
- [ ] Опис номера (`description`)
- [ ] Статус (кольорова мітка: 🟢 вільний, 🔴 зайнятий, 🟡 зарезервований)
- [ ] Зручності — список з іконками: назва + опис при наведенні (tooltip)
- [ ] Галерея фото номера (якщо є)
- [ ] Поточний гість (якщо зайнятий)

`templates/style.css` — стилі:
- [ ] Адаптивна сітка карток номерів (CSS Grid / Flexbox)
- [ ] Стилі для статусних міток
- [ ] Галерея фото (сітка мініатюр)
- [ ] Базова типографіка

##### Приклад згенерованого HTML
```html
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <title>Grand Hotel — Звіт</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>🏨 Grand Hotel</h1>
    <div class="gallery">
        <img src="../data/grand_hotel/media/hotel/facade.jpg" alt="Фасад">
        <img src="../data/grand_hotel/media/hotel/lobby.jpg" alt="Лобі">
    </div>
    <div class="stats">
        <p>Номерів: 7 | Вільних: 4 | Зайнятих: 2 | Зарезервованих: 1</p>
        <p>Загальний дохід: 12 500 грн</p>
    </div>
    <h2>Номери</h2>
    <div class="rooms-grid">
        <!-- картки номерів -->
    </div>
</body>
</html>
```

### Критерії завершення ітерації
- Гість із 6+ бронюваннями отримує 10% знижку
- Історія перебувань доступна через `guest.history`
- Дані готелю зберігаються у JSON і коректно відновлюються після перезапуску
- Round-trip тест: `save → load → порівняння` — дані ідентичні
- Медіафайли зберігаються у правильних директоріях, `get_photos()` повертає шляхи
- HTML-звіт генерується з фото, інформацією про номери та статистикою
- Юніт-тести оновлені: `test_storage.py`, `test_report.py` ✅

---

## Ітерація 5 — Демонстрація та фінальна інтеграція

### Мета
Зібрати все разом у `main.py` — демонстраційний сценарій.

### Завдання

#### 5.1 `main.py` — Демо-сценарій
- [ ] Створити **2 готелі** (наприклад, "Grand Hotel" та "Sea Resort") із 5–7 номерами кожен (мікс типів)
- [ ] Створити 3–4 гостей
- [ ] Виконати повний цикл:
  1. Показати вільні номери в обох готелях
  2. Забронювати номери для гостей у різних готелях
  3. Заселити гостей
  4. Показати стан готелів
  5. Зберегти обидва готелі у JSON (`HotelStorage.save()`) — кожен у свою директорію
  6. Додати фото готелів і номерів (`add_hotel_photo()`, `add_room_photo()`)
  7. Показати список збережених готелів (`HotelStorage.list_hotels()`)
  8. Завантажити готель за slug-ом (`HotelStorage.load("grand_hotel")`) — підтвердити, що стан відновився
  9. Виселити гостей
  10. Показати дохід по кожному готелю
  11. Показати історію гостя та рівень лояльності
  12. Згенерувати HTML-звіти для обох готелів (`HotelReportGenerator.generate_all()`)
  13. Зберегти фінальний стан у JSON

#### 5.2 Фінальна перевірка
- [ ] Запустити всі тести: `python -m pytest tests/`
- [ ] Перевірити валідацію (некоректні дані → виключення)
- [ ] Перевірити edge-cases: подвійне заселення, бронювання зайнятого номера тощо

---

## Підсумкова таблиця ітерацій

| Ітерація | Що робимо | Файли | Орієнтовний час |
|----------|-----------|-------|----------------|
| **1** | Enum, Amenity, Guest, Room (ABC) + підкласи | `enums.py`, `amenity.py`, `guest.py`, `room.py`, тести | 2–2.5 год |
| **2** | Booking | `booking.py`, тести | 1–1.5 год |
| **3** | Hotel (менеджер) | `hotel.py`, тести | 1.5–2 год |
| **4** | Лояльність, знижки, історія, JSON-збереження, медіа, HTML-звіт | `loyalty.py`, `storage.py`, `report.py`, шаблони, тести | 3–4 год |
| **5** | `main.py` демо + фінальні тести | `main.py`, тести | 1–1.5 год |

**Загалом: ~8–11 годин**

---

## Ключові принципи

- 🧱 **SOLID**: абстрактний `Room` → конкретні підкласи (Open/Closed)
- 🛡️ **Валідація**: перевіряємо все на вході (ціна, ночі, статус)
- 🧪 **Тести**: кожна ітерація завершується зеленими тестами
- 📦 **Інкапсуляція**: статус номера змінюється тільки через `check_in`/`check_out`
- 🔢 **Enum замість рядків**: `RoomStatus.FREE` замість `"free"`
