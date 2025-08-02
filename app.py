from dispatch_system import DispatchSystem
from flask import Flask, render_template, request, redirect, url_for, session, flash
import json

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True 
app.secret_key = 'your-secret-key-change-this'

ds: DispatchSystem = DispatchSystem("managers.json", "addresses.json")

def load_user_data(user_type):
    """Load user data from appropriate JSON file"""
    file_mapping = {
        'users': 'customers.json',
        'couriers': 'courier.json', 
        'managers': 'managers.json'
    }
    
    filename = file_mapping.get(user_type)
    if not filename:
        return []
    
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def authenticate_user(user_type, user_id, password):
    """Authenticate user against JSON file"""
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
def index():
    return render_template("index.html")

@app.route("/login/<user_type>")
def login_page(user_type):
    """Login page for specific user type"""
    if user_type not in ['users', 'couriers', 'managers']:
        flash('Invalid user type')
        return redirect(url_for('index'))
    
    return render_template("login.html", user_type=user_type)

@app.route("/authenticate", methods=['POST'])
def authenticate():
    """Handle login form submission"""
    user_type = request.form.get('user_type')
    user_id = request.form.get('username')
    password = request.form.get('password')
    
    if not all([user_type, user_id, password]):
        flash('Please fill in all fields')
        return redirect(url_for('login_page', user_type=user_type))
    
    user = authenticate_user(user_type, user_id, password)
    
    if user:
        session['user'] = user
        session['user_type'] = user_type
        session['user_id'] = user_id
        
        flash(f'Welcome, {user.get("name", "User")}!')
        return redirect(url_for('dashboard', user_type=user_type))
    else:
        flash('Wrong credentials. Please try again or create a new user.')
        return redirect(url_for('login_page', user_type=user_type))

@app.route("/dashboard/<user_type>")
def dashboard(user_type):
    """Dashboard after login"""
    if 'user' not in session:
        flash('Please log in first')
        return redirect(url_for('login_page', user_type=user_type))
    
    user = session['user']
    return render_template("dashboard.html", user=user, user_type=user_type)

@app.route("/orders")
def show_all_orders():
    orders = ds.view_orders()
    orders_dicts = [order.to_dict() for order in orders]
    return render_template("order_list.html", orders=orders_dicts)


if __name__ == "__main__":
    app.run(debug=True)