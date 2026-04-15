from datetime import date

from models.contact import Contact
from models.enums import RoomStatus
from models.guest import Guest

if __name__ == '__main__':
    c = Contact(name="Іван Петров", email="ivan.petr@gmail.com", phone="+380631234567", passport="АА111222")
    g = Guest(contact=c, birthday=date(1990, 5, 20))
    print(g)

    c2 = Contact(name="Марія Подопригора", email="m.podoprygora@gmail", phone="+380631234568", passport="АА111242")
    g2 = Guest(contact=c2, birthday=date(1992, 8, 15))
    print(g2)

    print("Гості однакові?", g == g2)