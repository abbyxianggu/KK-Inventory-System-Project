from KKINVSYS import create_app, db
from KKINVSYS.database import Donut, Sale, Ingredient
from datetime import date, timedelta
import random

app = create_app()

donuts_data = [
    {"name": "Original Glazed", "max_stock": 500, "price": 2.50},
    {"name": "Strawberry Iced", "max_stock": 350, "price": 2.50},
    {"name": "Choc Iced Custard", "max_stock": 400, "price": 3.00},
    {"name": "Cinnamon Scroll", "max_stock": 400, "price": 3.50},
    {"name": "Lemon Filled", "max_stock": 350, "price": 3.00},
    {"name": "Raspberry Filled", "max_stock": 350, "price": 3.00},
]

stores = ["Sydney CBD", "Parramatta", "Chatswood"]

with app.app_context():
    db.drop_all()
    db.create_all()

    for store in stores:
        for d in donuts_data:
            stock = random.randint(20, d["max_stock"])
            db.session.add(Donut(
                name=d["name"], store=store,
                stock=stock, max_stock=d["max_stock"], price=d["price"]
            ))

        for ingredient, max_q, unit in [
            ("Flour", 50, "kg"), ("Sugar", 20, "kg"),
            ("Glaze Mix", 20, "L"), ("Frying Oil", 40, "L")
        ]:
            db.session.add(Ingredient(
                name=ingredient, store=store,
                quantity=round(random.uniform(5, max_q), 1),
                max_quantity=max_q, unit=unit
            ))

    db.session.commit()

    all_donuts = Donut.query.all()
    today = date.today()

    for day_offset in range(7):
        sale_date = today - timedelta(days=6 - day_offset)
        for donut in all_donuts:
            for hour in range(8, 16):
                qty = random.randint(2, 30)
                db.session.add(Sale(
                    donut_id=donut.id, store=donut.store,
                    quantity=qty,
                    revenue=round(qty * donut.price, 2),
                    date=sale_date, hour=hour
                ))

    db.session.commit()
    print("Seeded successfully!")