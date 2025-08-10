from flask import Flask, render_template, request, redirect, session, Response, flash, url_for
from dispatch_system import DispatchSystem
from typing import Optional, Dict, Any, Union
from order import Order, PackageStatus

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = Flask(__name__)
ds = DispatchSystem("managers.json", "addresses.json")

app.secret_key = 'my_secret_key'
role = "courier"  # Example role, can be 'customer' or 'courier'
user_id = 3


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
def index():
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
def show_all_orders():
    orders = ds.view_orders()
    enriched_orders = []
    if role == "courier":
        courier_id = user_id
        orders = [order for order in orders if order._courier_id == courier_id]

    elif role == "customer":
        customer_id = user_id
        orders = [order for order in orders if order._customer_id == customer_id]

    for order in orders:
        origin_address = ds.get_address_by_id(order._origin_id)
        destination_address = ds.get_address_by_id(order._destination_id)

        order_dict = order.to_dict()
        order_dict["origin_address_str"] = str(
            origin_address) if origin_address else "N/A"
        order_dict["destination_address_str"] = str(
            destination_address) if destination_address else "N/A"

        enriched_orders.append(order_dict)

    return render_template("orders_list.html", orders=enriched_orders)


@app.route("/order_details", methods=["POST"])
def order_details():

    # קבלת הנתונים מהטופס הנשלח
    order = {
        "package_id": request.form["package_id"],
        "customer_id": request.form["customer_id"],
        "courier_id": request.form["courier_id"],
        "origin_address_str": request.form["origin_address_str"],
        "destination_address_str": request.form["destination_address_str"],
        "status": request.form["status"]
    }
    return render_template("order_details.html", order=order, role=role)


@app.route("/update_order", methods=["POST"])
def update_order():  # Update order status
    if role != "manager":
        return "Unauthorized", 403

    package_id = int(request.form["package_id"])
    action = request.form["action"]

    if action == "assign":
        new_courier = request.form["courier_id"]
        success = ds.update_order_courier(package_id, int(new_courier))
        message = "Courier updated." if success else "Update failed."
    elif action == "cancel":
        success = ds.update_order_status(package_id, PackageStatus.CANCELED)
        message = "Order canceled." if success else "Cancel failed."
    else:
        message = "Unknown action."

    return redirect("/orders")


@app.route("/update_status", methods=["POST"])
def update_status():
    if role != "courier":
        return "Unauthorized", 403

    package_id = int(request.form["package_id"])
    new_status = request.form["status"]

    if new_status not in ["on-delivery", "delivered"]:
        return "Invalid status", 400

    success = ds.update_order_status(package_id, new_status)
    return redirect("/orders")


@app.route('/new_order')
def new_order():
    return render_template("new_order.html")


if __name__ == "__main__":
    app.run(debug=True)
