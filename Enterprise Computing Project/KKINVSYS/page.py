from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import date, timedelta
from . import db
from .database import Donut, Sale, Ingredient, RestockRequest

page = Blueprint('page', __name__)

@page.route('/')
def index():
    store = request.args.get('store', 'Sydney CBD')
    today = date.today()
    yesterday = today - timedelta(days=1)

    donuts = Donut.query.filter_by(store=store).all()
    total_stock = sum(d.stock for d in donuts) 

    today_sales = Sale.query.filter_by(store=store, date=yesterday).all()
    sold_today = sum(s.quantity for s in today_sales)  
    revenue_today = sum(s.revenue for s in today_sales)  
    low_alerts = len([d for d in donuts if d.stock / d.max_stock < 0.10])

    hourly = {}
    for s in today_sales:
        hourly[s.hour] = hourly.get(s.hour, 0) + s.quantity

    hourly_labels = []
    for h in range(7, 24):
        if h < 12:    hourly_labels.append(f"{h}am")
        elif h == 12: hourly_labels.append("12pm")
        else:         hourly_labels.append(f"{h-12}pm")

    hourly_data = [hourly.get(h, 0) for h in range(7, 24)]

    return render_template('index.html',
        active='overview', store=store,
        donuts=donuts, total_stock=total_stock,
        sold_today=sold_today, revenue_today=revenue_today,
        low_alerts=low_alerts,
        hourly_labels=hourly_labels, hourly_data=hourly_data,
    )

@page.route('/inventory')
def inventory():
    store = request.args.get('store', 'Sydney CBD')
    donuts = Donut.query.filter_by(store=store).all()
    ingredients = Ingredient.query.filter_by(store=store).all()
    total_stock = sum(d.stock for d in donuts)
    low_count = len([d for d in donuts if d.stock / d.max_stock < 0.10])

    return render_template('inventory.html',
        active='inventory', store=store,
        donuts=donuts, ingredients=ingredients,
        total_stock=total_stock, low_count=low_count
    )


@page.route('/sales')
def sales():
    store = request.args.get('store', 'Sydney CBD')
    today = date.today()
    yesterday = today - timedelta(days=1)

    donuts = Donut.query.filter_by(store=store).all()
    max_possible = sum(d.max_stock for d in donuts)
    total_stock = sum(d.stock for d in donuts)
    sold_today = max_possible - total_stock

    today_sales = Sale.query.filter_by(store=store, date=yesterday).order_by(Sale.hour).all()
    revenue_today = sum(s.revenue for s in today_sales)
    quota_pct = (revenue_today / 5000) * 100

    seven_days = []
    trend_labels = []
    for i in range(7):
        d = yesterday - timedelta(days=6 - i)
        day_sales = Sale.query.filter_by(store=store, date=d).all()
        seven_days.append(round(sum(s.revenue for s in day_sales), 2))
        trend_labels.append(d.strftime('%a'))

    # hourly for sales page too
    hourly = {}
    for s in today_sales:
        hourly[s.hour] = hourly.get(s.hour, 0) + s.quantity

    hourly_labels = []
    for h in range(7, 24):
        if h < 12:    hourly_labels.append(f"{h}am")
        elif h == 12: hourly_labels.append("12pm")
        else:         hourly_labels.append(f"{h-12}pm")

    hourly_data = [hourly.get(h, 0) for h in range(7, 24)]

    return render_template('sales.html',
        active='sales', store=store,
        sales=today_sales,
        revenue_today=revenue_today, sold_today=sold_today,
        quota_pct=quota_pct,
        seven_days=seven_days, trend_labels=trend_labels,
        hourly_labels=hourly_labels, hourly_data=hourly_data,
    )


@page.route('/alerts')
def alerts():
    store = request.args.get('store', 'Sydney CBD')
    donuts = Donut.query.filter_by(store=store).all()
    low    = [d for d in donuts if d.stock / d.max_stock < 0.10]
    medium = [d for d in donuts if 0.10 <= d.stock / d.max_stock < 0.50]
    restock_requests = RestockRequest.query.filter_by(store=store).order_by(
        RestockRequest.date_submitted.desc()).all()
    all_donuts = Donut.query.filter_by(store=store).all()

    return render_template('alerts.html',
        active='alerts', store=store,
        low=low, medium=medium,
        restock_requests=restock_requests,
        all_donuts=all_donuts,
    )

@page.route('/alerts/submit', methods=['POST'])
def submit_restock():
    store = request.args.get('store', 'Sydney CBD')
    try:
        donut_id        = int(request.form.get('donut_id'))
        quantity_needed = int(request.form.get('quantity_needed'))
        urgency         = request.form.get('urgency', 'Medium')
        notes           = request.form.get('notes', '')

        if quantity_needed < 1:
            raise ValueError("Quantity must be at least 1")

        donut = Donut.query.get(donut_id)
        if not donut:
            raise ValueError("Invalid donut selection")

        pct = donut.stock / donut.max_stock
    
        if pct >= 1.0:
            flash(f"{donut.name} is already at full capacity ({donut.stock}/{donut.max_stock}). No restock needed.", category="error")
            return redirect(url_for('page.alerts', store=store))

        if pct >= 0.50:
            flash(f"{donut.name} is at {int(pct*100)}% capacity — not low enough to require restocking.", category= "error")
            return redirect(url_for('page.alerts', store=store))
        
        if quantity_needed > donut.max_stock:
            flash(f"Requested quantity exceeds max capacity. Only {donut.max_stock - donut.stock} can be restocked.", category="error")
            return redirect(url_for('page.alerts', store=store))
        
        req = RestockRequest(
            donut_id=donut_id, store=store,
            quantity_needed=quantity_needed,
            urgency=urgency, notes=notes,
            date_submitted=date.today(), status='Pending'
        )
        db.session.add(req)
        db.session.commit()
        flash(f"Pending restock: {donut.name} × {quantity_needed} ({urgency} urgency)", category="success")

    except ValueError as e:
        flash(f"Error: {str(e)}", "error")
    except Exception:
        db.session.rollback()
        flash("Something went wrong. Please try again.", "error")

    return redirect(url_for('page.alerts', store=store))


@page.route('/reports')
def reports():
    store = request.args.get('store', 'Sydney CBD')
    today = date.today()
    yesterday = today - timedelta(days=1)

    # Stats for selected store
    week_sales = Sale.query.filter_by(store=store).filter(
        Sale.date >= yesterday - timedelta(days=6),
        Sale.date <= yesterday
    ).all()

    total_revenue_7d = round(sum(s.revenue for s in week_sales), 2)
    total_units_7d   = sum(s.quantity for s in week_sales)

    # Best seller by quantity
    donut_totals = {}
    for s in week_sales:
        donut_totals[s.donut.name] = donut_totals.get(s.donut.name, 0) + s.quantity
    best_seller = max(donut_totals, key=donut_totals.get) if donut_totals else "N/A"
    best_seller_short = best_seller.split()[0] + " " + best_seller.split()[1] if len(best_seller.split()) > 1 else best_seller

    # Sales by variety for doughnut chart
    variety_labels = list(donut_totals.keys())
    variety_data   = list(donut_totals.values())

    # Revenue vs quota per day
    quota_days = []
    daily_pcts = []
    for i in range(7):
        d = yesterday - timedelta(days=6 - i)
        day_sales = Sale.query.filter_by(store=store, date=d).all()
        rev = sum(s.revenue for s in day_sales)
        pct = (rev / 5000) * 100
        quota_days.append((d.strftime('%a'), pct))
        daily_pcts.append(pct)

    avg_quota = sum(daily_pcts) / len(daily_pcts) if daily_pcts else 0

    # All stores comparison
    all_stores = []
    for s_name in ['Sydney CBD', 'Parramatta', 'Chatswood']:
        s_donuts = Donut.query.filter_by(store=s_name).all()
        s_sales = Sale.query.filter_by(store=s_name).filter(
            Sale.date >= yesterday - timedelta(days=6),
            Sale.date <= yesterday
        ).all()
        s_rev   = round(sum(x.revenue for x in s_sales), 2)
        s_units = sum(x.quantity for x in s_sales)
        s_quota = (s_rev / (5000 * 7)) * 100
        s_alerts = len([d for d in s_donuts if d.stock / d.max_stock < 0.10])
        all_stores.append({
            'store': s_name, 'units': s_units,
            'revenue': s_rev, 'quota_pct': s_quota,
            'alerts': s_alerts
        })

    return render_template('reports.html',
        active='reports', store=store,
        total_revenue_7d=total_revenue_7d, total_units_7d=total_units_7d,
        best_seller=best_seller_short, avg_quota=avg_quota,
        variety_labels=variety_labels, variety_data=variety_data,
        quota_days=quota_days, all_stores=all_stores,
    )

