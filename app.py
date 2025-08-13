from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.wrappers import Response
from typing import Union, List, Dict, Any, Optional
from order import Order
from dispatch_system import DispatchSystem
import json
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
        elif user_type == 'users':
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

    if 'user' in session:
        logged_in_user_type = session.get('user_type', user_type)
        return redirect(url_for('show_all_orders', user_type=logged_in_user_type))

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
        return redirect(url_for('show_all_orders', user_type=session.get('user_type')))

    else:
        error_message = 'Wrong credentials. Please try again.'
        print(
            f"[DEBUG] Authentication failed for user_id: {user_id}, user_type: {user_type}")
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


@app.route("/orders/<user_type>")
def order_list(user_type: str) -> str:
    orders = ds.view_orders()
    orders_dicts = [order.to_dict() for order in orders]
    return render_template("order_list.html", orders=orders_dicts, user_type=user_type)


@app.route("/create_new_order/<user_type>")
def create_new_order(user_type: str) -> Union[str, Response]:
    # Check if user is logged in
    if 'user' not in session:
        flash('Please log in first')
        return redirect(url_for('login_page', user_type=user_type))

    # Check if user is a customer (not courier or manager)
    if session.get('user_type') != 'customers':
        flash('Only customers can create orders')
        return redirect(url_for('show_all_orders', user_type=session.get('user_type')))

    # Check if user has a valid ID
    if not session.get('user_id'):
        flash('Invalid user. Please log in again.')
        return redirect(url_for('login_page', user_type=user_type))

    return render_template("create_new_order.html", user_type=user_type)


@app.route("/create_order", methods=['POST'])
def create_order() -> Union[str, Response]:
    try:
        # Address data with validation - no customer_id needed
        street = request.form.get('street', '').strip()
        house_number_str = request.form.get('house_number', '0')
        city = request.form.get('city', '').strip()
        postal_code = request.form.get('postal_code', '').strip()
        country = request.form.get('country', '').strip()

        if not all([street, house_number_str, city, country]):
            flash('Street, house number, city and country are required')
            return render_template("create_new_order.html")

        house_number = int(house_number_str)
        apartment_str = request.form.get('apartment', '').strip()
        apartment = int(
            apartment_str) if apartment_str and apartment_str.isdigit() else None

        floor_str = request.form.get('floor', '').strip()
        floor = int(floor_str) if floor_str and floor_str.isdigit() else None

        # Special instructions
        message = request.form.get('message', '').strip()

        # Create address data dictionary for DispatchSystem
        address_data = {
            'street': street,
            'house_number': house_number,
            'city': city,
            'postal_code': postal_code,
            'country': country,
            'apartment': apartment,
            'floor': floor,
            'message': message if message else None
        }

        # Add address using ONLY DispatchSystem methods
        address = ds.add_address(address_data)

        # Get customer_id from session if logged in, otherwise use guest
        customer_id = session.get('user_id', 'GUEST_001')

        # Create order using Order class through dispatch system
        order_data = {
            'customer_id': customer_id,
            'courier_id': None,  # Will be assigned later by system
            'origin_id': None,  # Default origin - could be made dynamic
            'destination_id': address.id,
            'status': 'created'
        }

        # Create order through dispatch system
        order = ds.add_order(order_data)

        if order:
            # Assign closest courier to the order
            assignment_success = ds.assign_closest_courier_to_order(
                order._package_id)

            if assignment_success:
                # Get the updated order with courier assignment
                updated_order = ds.find_order_by_package_id(order._package_id)
                if updated_order and updated_order._courier_id:
                    # Get the assigned courier
                    assigned_courier = ds.get_courier_by_id(
                        updated_order._courier_id)
                    if assigned_courier:
                        # Update the order's origin_id to courier's current location
                        Order.update_by_package_id(
                            order._package_id, "origin_id", assigned_courier.current_location)
                        flash('Order created successfully and assigned to courier!')
                    else:
                        flash('Order created but courier assignment failed!')
                else:
                    flash('Order created but courier assignment failed!')
            else:
                flash('Order created but no available courier could be assigned!')

            return redirect(url_for('order_list', user_type=session.get('user_type', 'users')))
        else:
            flash('Failed to create order')
            return render_template("create_new_order.html")

    except ValueError as e:
        flash(f'Invalid input data: {str(e)}')
        return render_template("create_new_order.html")
    except Exception as e:
        flash(f'Error creating order: {str(e)}')
        return render_template("create_new_order.html")


@app.route("/logout")
def logout() -> Response:
    session.clear()
    flash('You have been logged out successfully')
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run()
