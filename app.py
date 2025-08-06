from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.wrappers import Response
from typing import Union, List, Dict, Any, Optional
import json
from dispatch_system import DispatchSystem
from flask import jsonify
import random
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True 
app.secret_key = 'your-secret-key-change-this'

ds: DispatchSystem = DispatchSystem("managers.json", "addresses.json")

def load_user_data(user_type: str) -> List[Dict[str, Any]]:
    file_mapping = {
        'users': 'data/customers.json',
        'couriers': 'data/courier.json', 
        'managers': 'data/managers.json'
    }
    
    filename = file_mapping.get(user_type)
    if not filename:
        return []
    
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def authenticate_user(user_type: str, user_id: str, password: str) -> Optional[Dict[str, Any]]:
    users = load_user_data(user_type)

    id_fields = {
        'users': 'customer_id',
        'couriers': 'courier_id',
        'managers': 'manager_id'
    }
    
    id_field = id_fields.get(user_type)
    if not id_field:
        return None
    
    for user in users:
        user_id_str = str(user.get(id_field, ''))
        if user_id_str == str(user_id) and user.get('password') == password:
            return user
    
    return None

@app.route("/")
def index() -> str:
    return render_template("index.html")

@app.route("/login/<user_type>")
def login_page(user_type: str) -> Union[str, Response]:
    if user_type not in ['users', 'couriers', 'managers']:
        flash('Invalid user type')
        return redirect(url_for('index'))
    
    return render_template("login.html", user_type=user_type)

@app.route("/authenticate", methods=['POST'])
@app.route("/authenticate", methods=['POST'])
def authenticate() -> Union[str, Response]:
    user_type = request.form.get('user_type') or 'users'  
    user_id = request.form.get('username') or ''          
    password = request.form.get('password') or ''            
    if not all([user_type, user_id, password]):
        error_message = 'Please fill in all fields'
        return render_template("login.html", user_type=user_type, error_message=error_message)
    
    user = authenticate_user(user_type, user_id, password)
    
    if user:
        session['user'] = user
        session['user_type'] = user_type
        session['user_id'] = user_id
        return redirect(url_for('dashboard', user_type=user_type))
    
    else:
        error_message = 'Wrong credentials. Please try again.'
        return render_template("login.html", user_type=user_type, error_message=error_message)

@app.route("/dashboard/<user_type>")
def dashboard(user_type: str) -> Union[str, Response]:
    if 'user' not in session:
        flash('Please log in first')
        return redirect(url_for('login_page', user_type=user_type))
    
    user = session['user']
    return render_template("dashboard.html", user=user, user_type=user_type)

@app.route("/signup/<user_type>")
def signup(user_type: str) -> str:
    return render_template("signup.html", user_type=user_type)

@app.route("/orders")
def show_all_orders() -> str:
    orders = ds.view_orders()
    orders_dicts = [order.to_dict() for order in orders]
    return render_template("order_list.html", orders=orders_dicts)

@app.route("/manager_dashboard")
def manager_dashboard():
    return render_template("manager_dashboard.html")

@app.route('/api/deliveries')
def get_delivery_data():
    # דוגמה לנתונים מזויפים – כל רענון מחזיר מספרים חדשים
    now = datetime.now()
    labels = [(now - timedelta(hours=i)).strftime('%H:%M') for i in reversed(range(6))]
    values = [random.randint(50, 150) for _ in range(6)]

    return jsonify({
        'labels': labels,
        'values': values
    })

@app.route('/api/deliveries_by_region')
def get_region_data():
    # נתונים לדוגמה – תוכלי להחליף בשליפה מ-DB
    labels = ['Tel Aviv', 'Haifa', 'Jerusalem', 'Beersheba', 'Eilat']
    values = [40, 25, 20, 10, 5]  # אחוזים/כמויות

    return jsonify({
        'labels': labels,
        'values': values
    })

@app.route('/api/orders')
def get_orders():
    with open('orders.json', 'r') as f:
        orders = json.load(f)

    return jsonify(orders)

if __name__ == "__main__":
    app.run(debug=True)