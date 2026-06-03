from flask import Blueprint, render_template, request
from datetime import date, timedelta
from .import db
from .database import Donut, Sale, Ingredient, RestockRequest

page = Blueprint('page', __name__)

@page.route('/')
def index():
    store = request.args.get('store', 'Sydney CBD')
    today = date.today()
    yesterday = today - timedelta(days=1)

    donuts = Donut.query.filter_by(store=store).all()
    total_stock = sum(d.stock for d in donuts)

    today_sales = Sale.query.filter_by(store=store, date=today).all()
    max_possible = sum(d.max_stock for d in donuts)
    sold_today = max_possible - total_stock
    revenue_today = sum(s.revenue for s in today_sales)
    low_alerts = len([d for d in donuts if d.stock / d.max_stock < 0.10])

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
        alerts=alerts)
    
@page.route('/inventory')
def inventory():
    store = request.args.get('store', 'Sydney CBD')
    donuts = Donut.query.filter_by(store=store).all()
    ingredients = Ingredient.query.filter_by(store=store).all()
    
    return render_template('inventory.html',
        active='inventory',
        store=store,
        donuts=donuts,
        ingredients=ingredients
    )
    
@page.route('/sales')
def sales():
    store = request.args.get('store', 'Sydney CBD')
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    donuts = Donut.query.filter_by(store=store).all()
    sales = Sale.query.filter_by(store=store, date=yesterday).order_by(Sale.hour).all()
    
    # 7 day trend
    seven_days = []
    for i in range(7):
        d = yesterday - timedelta(days=6 - i)
        day_sales = Sale.query.filter_by(store=store, date=d).all()
        seven_days.append(sum(s.revenue for s in day_sales))
    
    trend_labels = [(yesterday - timedelta(days=6 - i)).strftime('%a') for i in range(7)]
    
    return render_template('sales.html',
        active='sales',
        store=store,
        donuts=donuts,
        sales=sales,
        seven_days=seven_days,
        trend_labels=trend_labels
    )

@page.route('/alerts')
def alerts():
    store = request.args.get('store', 'Sydney CBD')
    donuts = Donut.query.filter_by(store=store).all()
    low = [d for d in donuts if d.stock / d.max_stock < 0.10]