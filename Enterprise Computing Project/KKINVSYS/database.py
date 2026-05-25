from.import db

class Donut(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    store = db.Column(db.String(100), nullable=False)  # Sydney CBD, Parramatta, Chatswood
    stock = db.Column(db.Integer, nullable=False)
    max_stock = db.Column(db.Integer, nullable=False)  # e.g. 500 for Original Glazed
    price = db.Column(db.Float, nullable=False)

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    store = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    max_quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)  # kg, L etc.

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donut_id = db.Column(db.Integer, db.ForeignKey('donut.id'), nullable=False)
    store = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    revenue = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    hour = db.Column(db.Integer, nullable=False)  # 8, 9, 10... for hourly chart

class RestockRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donut_id = db.Column(db.Integer, db.ForeignKey('donut.id'), nullable=False)
    store = db.Column(db.String(100), nullable=False)
    quantity_needed = db.Column(db.Integer, nullable=False)
    urgency = db.Column(db.String(20), nullable=False)  # Low, Medium, High
    notes = db.Column(db.String(500))
    date_submitted = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Pending')