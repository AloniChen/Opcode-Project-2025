from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.wrappers import Response
from typing import Union, List, Dict, Any, Optional
import json
from dispatch_system import DispatchSystem
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True 
app.secret_key = 'your-secret-key-change-this'

ds: DispatchSystem = DispatchSystem("managers.json", "addresses.json")

def authenticate_user(user_type: str, user_id: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate user using DispatchSystem methods
    """
    try:
        if user_type == 'managers':
            manager = ds.get_manager_by_id(user_id)
            if manager and getattr(manager, 'password', None) == password:
                return manager.to_dict()    
        elif user_type == 'customers':
            customer = ds.get_customer_by_id(user_id)
            if customer and getattr(customer, 'password', None) == password:
                return customer.to_dict()  
        elif user_type == 'couriers':
            courier = ds.get_courier_by_id(int(user_id))
            if courier and getattr(courier, 'password', None) == password:
                return courier.to_dict()
    except (ValueError, AttributeError) as e:
        logger.error(f"Authentication error: {e}")
        
    return None

@app.route("/")
def index() -> str:
    return render_template("index.html")

@app.route("/login/<user_type>")
def login_page(user_type: str) -> Union[str, Response]:
    if user_type not in ['customers', 'couriers', 'managers']:
        flash('Invalid user type')
        return redirect(url_for('index'))
    
    return render_template("login.html", user_type=user_type)

@app.route("/authenticate", methods=['POST'])
def authenticate() -> Union[str, Response]:
    user_type = request.form.get('user_type') or 'customers'  
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

if __name__ == "__main__":
    app.run(debug=True)