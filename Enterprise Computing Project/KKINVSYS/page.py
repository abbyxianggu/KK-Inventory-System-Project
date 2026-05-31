from flask import Blueprint, render_template
from datetime import date
page = Blueprint("page", __name__)

@page.route('/')
def index():
    return render_template('index.html')


@page.route('/inventory')
def inv():
    return render_template ('inventory.html')

@page.route('/sales')
def sales():
    return render_template ('sales.html')

@page.route('/alerts')
def alerts():
    return render_template ('alerts.html')

@page.route('/reports')
def reports():
    return render_template ('reports.html')