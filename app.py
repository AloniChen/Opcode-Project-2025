from flask import Flask, render_template, request, redirect, session, Response, flash, url_for, get_flashed_messages, jsonify
from datetime import datetime, timedelta
from werkzeug.wrappers import Response
from typing import Union, List, Dict, Any, Optional
from order import Order, PackageStatus
from dispatch_system import DispatchSystem
import json
import random
from collections import Counter
import logging

# ----------------- Logging -----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------- App & DS -----------------
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.secret_key = "my_secret_key"

ds = DispatchSystem(
    "managers.json",
    "addresses.json",
    "orders.json",
    "couriers.json",
    "customers.json"
)

# orders = ds.view_orders()
# print(orders)


def load_user_data(user_type: str) -> List[Dict[str, Any]]:
    file_mapping = {
        'customers': 'data/customers.json',
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


# ----------------- Helpers -----------------
def authenticate_user(user_type: str, user_id: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate user using DispatchSystem methods.
    Returns a dict (to_dict) on success, None otherwise.
    """
    try:
        if user_type == "managers":
            manager = ds.get_manager_by_id(user_id)
            if manager and getattr(manager, "password", None) == password:
                return manager.to_dict()
        elif user_type == "customers":
            customer = ds.get_customer_by_id(user_id)
            if customer and getattr(customer, "password", None) == password:
                return customer.to_dict()
        elif user_type == "couriers":
            courier = ds.get_courier_by_id(int(user_id))
            if courier and getattr(courier, "password", None) == password:
                return courier.to_dict()
    except (ValueError, AttributeError) as e:
        logger.error(f"Authentication error: {e}")
    return None


def _status_str_to_enum(value: str) -> Optional[PackageStatus]:
    """
    Map various form/input strings to PackageStatus.
    Supports legacy 'confirmed'.
    """
    if not value:
        return None
    v = value.strip().lower()
    mapping = {
        "created": PackageStatus.CREATED,
        "confirmed": PackageStatus.CONFIRMED,  # legacy
        "confirmed - assigned to courier": PackageStatus.CONFIRMED,
        "on-delivery": PackageStatus.ON_DELIVERY,
        "delivered": PackageStatus.DELIVERED,
        "no assigned courier": PackageStatus.NOT_ASSIGNED,
        "canceled": PackageStatus.CANCELED,
        "cancelled": PackageStatus.CANCELED,   # just in case
    }
    return mapping.get(v)


# ----------------- Routes -----------------
@app.route("/")
def index() -> Union[str, Response]:
    if 'user' in session:
        logged_in_user_type = session.get('user_type')
        if logged_in_user_type:
            return redirect(url_for('show_all_orders', user_type=logged_in_user_type))
    return render_template("index.html")


@app.route("/login/<user_type>")
def login_page(user_type: str) -> Union[str, Response]:
    if user_type not in ["customers", "couriers", "managers"]:
        flash("Invalid user type")
        return redirect(url_for("index"))
    return render_template("login.html", user_type=user_type)


@app.route("/authenticate", methods=['POST'])
def authenticate() -> Union[str, Response]:
    user_type = request.form.get('user_type') or 'customers'
    user_id = request.form.get('username') or ''
    password = request.form.get('password') or ''
    if not all([user_type, user_id, password]):
        error_message = "Please fill in all fields"
        return render_template("login.html", user_type=user_type, error_message=error_message)

    user = authenticate_user(user_type, user_id, password)
    if user:
        session["user"] = user
        session["user_type"] = user_type
        session["user_id"] = user_id
        return redirect(url_for('show_all_orders', user_type=session.get('user_type')))

    else:
        error_message = "Wrong credentials. Please try again."
        return render_template("login.html", user_type=user_type, error_message=error_message)


@app.route("/manager_dashboard/<user_type>")
def manager_dashboard(user_type: str) -> Union[str, Response]:
    if 'user' not in session:
        flash('Please log in first')
        return redirect(url_for('login_page', user_type=user_type))

    user = session['user']
    return render_template("manager_dashboard.html", user=user, user_type=user_type)


@app.route("/signup/<user_type>")
def signup(user_type: str) -> str:
    return render_template("signup.html", user_type=user_type)


@app.route('/api/deliveries')
def get_delivery_data():
    # דוגמה לנתונים מזויפים – כל רענון מחזיר מספרים חדשים
    now = datetime.now()
    labels = [(now - timedelta(hours=i)).strftime('%H:%M')
              for i in reversed(range(6))]
    values = [random.randint(50, 150) for _ in range(6)]

    return jsonify({
        'labels': labels,
        'values': values
    })


@app.route("/api/orders/count")
def orders_count():
    try:
        orders = ds.view_orders()        # מחזיר רשימת Order
        return jsonify({"count": len(orders)})
    except Exception:
        return jsonify({"count": 0})


@app.route("/api/customers_amount/count")
def customers_count():
    try:
        with open("data/customers.json", "r") as file:
            customers = json.load(file)
        customer_list = []
        for customer in customers:
            customer_list.append(customer(customer_id=customer.get("customer_id"), name=customer.get("name"), address=customer.get("address"),
                                          phone_number=customer.get('phone_number'), email=customer.get("email"), password=customer.get("password"), credit=customer.get("credit")))
        return jsonify({"count": len(customer_list)})
    except FileNotFoundError:
        return jsonify({"count": 0})


@app.route('/api/deliveries_by_region')
def get_region_data():
    # נתונים לדוגמה – תוכלי להחליף בשליפה מ-DB
    labels = ['Tel Aviv', 'Haifa', 'Jerusalem', 'Beersheba', 'Eilat']
    values = [40, 25, 20, 10, 5]  # אחוזים/כמויות

    return jsonify({
        'labels': labels,
        'values': values
    })


@app.route("/orders/<user_type>")
def show_all_orders(user_type: str) -> Union[str, Response]:
    # Require login
    user_type = user_type or session.get("user_type")
    user_id = session.get("user_id")
    if not user_type or not user_id:
        flash("You must log in first")
        return redirect(url_for("index"))

    orders = ds.view_orders()

    # Filter by role (normalize IDs to str to avoid int/str mismatch)
    if user_type == "couriers":
        courier_id = str(user_id)
        orders = [o for o in orders if str(o._courier_id) == courier_id]
    elif user_type == "customers":
        customer_id = str(user_id)
        orders = [o for o in orders if str(o._customer_id) == customer_id]
    elif user_type == "managers":
        pass  # managers see all
    else:
        flash("Unauthorized access")
        return redirect(url_for("index"))

    # Enrich for template (addresses & string status)
    enriched_orders = []
    for order in orders:
        origin_address = ds.get_address_by_id(order._origin_id)
        destination_address = ds.get_address_by_id(order._destination_id)

        od = order.to_dict()  # status already stringified if Enum
        od["origin_address_str"] = str(
            origin_address) if origin_address else "N/A"
        od["destination_address_str"] = str(
            destination_address) if destination_address else "N/A"
        enriched_orders.append(od)

    return render_template("orders_list.html", orders=enriched_orders)


def _order_context_for_template(order: Order, ds: DispatchSystem) -> Dict[str, Any]:
    """
    Build dict for order_details.html with enriched address strings
    and status as a plain string.
    """
    od = order.to_dict()  # status already string if Enum
    origin_address = ds.get_address_by_id(order._origin_id)
    destination_address = ds.get_address_by_id(order._destination_id)
    od["origin_address_str"] = str(origin_address) if origin_address else "N/A"
    od["destination_address_str"] = str(
        destination_address) if destination_address else "N/A"
    return od


# ---------- NEW: GET route for opening order details from the list ----------
@app.route("/orders/<int:package_id>")
def order_details_get(package_id: int):
    # Require login
    if not session.get("user_type") or not session.get("user_id"):
        flash("You must log in first")
        return redirect(url_for("index"))

    order = ds.find_order_by_package_id(package_id)
    if not order:
        flash("Order not found")
        return redirect(url_for('show_all_orders', user_type=session.get('user_type')))

    order_ctx = _order_context_for_template(order, ds)
    role = session.get("user_type", "")
    return render_template("order_details.html", order=order_ctx, role=role)
# ---------------------------------------------------------------------------


@app.route("/update_order", methods=["POST"])
def update_order():
    # managers only
    if not session.get("user_type") or not session.get("user_id"):
        flash("You must log in first")
        return redirect(url_for("index"))
    if session.get("user_type") != "managers":
        return "Unauthorized", 403

    try:
        package_id = int(request.form["package_id"])
    except (KeyError, ValueError):
        return "Invalid package_id", 400

    action = (request.form.get("action") or "").strip().lower()
    message = None

    if action == "assign":
        new_courier_raw = (request.form.get("courier_id") or "").strip()
        if not new_courier_raw.isdigit():
            message = "Courier ID must be a number"
        else:
            success = ds.update_order_courier(package_id, int(new_courier_raw))
            if success:
                ds.update_order_status(
                    package_id, PackageStatus.CONFIRMED.value)
                message = "Courier assigned and status set to confirmed."
            else:
                message = "Update failed."

        # stay on order details page
        order = ds.find_order_by_package_id(package_id)
        if not order:
            flash("Order not found")
            return redirect(url_for('show_all_orders', user_type=session.get('user_type')))

        order_ctx = _order_context_for_template(order, ds)
        return render_template("order_details.html", order=order_ctx, role="managers", message=message)

    elif action == "assign_closest":
        success = ds.assign_closest_courier_to_order(package_id)
        if success:
            ds.update_order_status(package_id, PackageStatus.CONFIRMED.value)
            message = "Assigned the closest available courier and confirmed."
        else:
            message = "No available courier found (or assignment failed)."

        # stay on order details page
        order = ds.find_order_by_package_id(package_id)
        if not order:
            flash("Order not found")
            return redirect(url_for('show_all_orders', user_type=session.get('user_type')))

        order_ctx = _order_context_for_template(order, ds)
        return render_template("order_details.html", order=order_ctx, role="managers", message=message)

    elif action == "cancel":
        success = ds.update_order_status(
            package_id, PackageStatus.CANCELED.value)
        flash("Order canceled." if success else "Cancel failed.")
        # after cancel – go back to list
        return redirect(url_for('show_all_orders', user_type=session.get('user_type')))

    else:
        flash("Unknown action.")
        return redirect(url_for('show_all_orders', user_type=session.get('user_type')))


@app.route("/update_status", methods=["POST"])
def update_status():
    # couriers only
    if not session.get("user_type") or not session.get("user_id"):
        flash("You must log in first")
        return redirect(url_for("index"))
    if session.get("user_type") != "couriers":
        return "Unauthorized", 403

    try:
        package_id = int(request.form["package_id"])
    except (KeyError, ValueError):
        return "Invalid package_id", 400

    new_status_raw = request.form.get("status", "")
    enum_status = _status_str_to_enum(new_status_raw)
    if enum_status not in (PackageStatus.ON_DELIVERY, PackageStatus.DELIVERED):
        return "Invalid status", 400

    # Save as string to JSON
    success = ds.update_order_status(package_id, enum_status.value)
    flash("Status updated." if success else "Update failed.")
    return redirect(url_for('show_all_orders', user_type=session.get('user_type')))


@app.route("/new_order")
def new_order():
    return render_template("new_order.html")
    orders_dicts = []
    for order in orders:
        order_dict = {
            'package_id': order._package_id,
            'customer_id': order._customer_id,
            'courier_id': order._courier_id,
            'origin_id': order._origin_id,
            'destination_id': order._destination_id,
            'status': order._status.value if hasattr(order._status, 'value') else str(order._status)
        }
        orders_dicts.append(order_dict)
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
                flash('Order created but courier assignment failed!')
        else:
            flash('Order created but no available courier could be assigned!')

        return redirect(url_for('show_all_orders', user_type=session.get('user_type')))
    else:
        flash('Failed to create order')
        return render_template("create_new_order.html", user_type=session.get('user_type'))


@app.route("/logout")
def logout() -> Response:
    session.clear()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
