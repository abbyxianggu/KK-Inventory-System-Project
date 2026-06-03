from flask import Blueprint, render_template, request
from datetime import date
from . import db
from .database import Donut, Sale

page = Blueprint('page', __name__)

@page.route('/')
def index():
    store = request.args.get('store', 'Sydney CBD')
    today = date.today()

    donuts = Donut.query.filter_by(store=store).all()
    total_stock = sum(d.stock for d in donuts)

    today_sales = Sale.query.filter_by(store=store, date=today).all()
    sold_today = sum(s.quantity for s in today_sales)
    revenue_today = sum(s.revenue for s in today_sales)
    low_alerts = len([d for d in donuts if d.stock / d.max_stock < 0.50])

    hourly = {}
    for s in today_sales:
        hourly[s.hour] = hourly.get(s.hour, 0) + s.quantity
    hourly_labels = [f"{h}am" if h < 12 else ("12pm" if h == 12 else f"{h-12}pm") for h in range(8, 16)]
    hourly_data = [hourly.get(h, 0) for h in range(8, 16)]

    alerts = [d for d in donuts if d.stock / d.max_stock < 0.50]

    return render_template('index.html',
        active='overview',
        store=store,
        donuts=donuts,
        total_stock=total_stock,
        sold_today=sold_today,
        revenue_today=revenue_today,
        low_alerts=low_alerts,
        hourly_labels=hourly_labels,
        hourly_data=hourly_data,
        alerts=alerts
    )
    
