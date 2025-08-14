from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.wrappers import Response
from typing import Union, List, Dict, Any, Optional
from order import Order
from dispatch_system import DispatchSystem
import json
import logging
import re
import datetime as dt

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
def index() -> Union[str, Response]:
    if 'user' in session:
        logged_in_user_type = session.get('user_type')
        if logged_in_user_type:
            return redirect(url_for('show_all_orders', user_type=logged_in_user_type))
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
        print(f"[DEBUG] Authentication failed for user_id: {user_id}, user_type: {user_type}")
        return render_template("login.html", user_type=user_type, error_message=error_message)

@app.route("/dashboard/<user_type>")
def dashboard(user_type: str) -> Union[str, Response]:
    if 'user' not in session:
        flash('Please log in first')
        return redirect(url_for('login_page', user_type=user_type))

    user = session['user']
    return render_template("dashboard.html", user=user, user_type=user_type)

# If you have a global guard, make sure signup + static are allowed.
@app.before_request
def _allow_public_pages():
    from flask import request, abort
    open_endpoints = {"signup", "static"}
    if request.endpoint in open_endpoints:
        return
    # If you require user_type elsewhere, keep this; otherwise remove it.
    if "user_type" not in session:
        # Don’t block everything while testing; default to customers
        session["user_type"] = "customers"
        # Or: abort(401, "Unauthorized: user type not found in session.")

# --- Helpers ---------------------------------------------------------------

def _normalize_role(raw: str) -> str:
    """Map variants to plural roles used across the app: 'customers' or 'couriers' or 'managers'."""
    r = (raw or "").strip().lower()
    if r in {"courier", "couriers"}:  return "couriers"
    if r in {"manager", "managers"}:  return "managers"
    return "customers"

def _validate_payload(role: str, form) -> list[str]:
    """Minimal server-side validation matching the courier/customer forms."""
    errs = []
    full_name = (form.get("full_name") or "").strip()
    email     = (form.get("email") or "").strip()
    phone     = (form.get("phone") or "").strip()
    password  = (form.get("password") or "")

    if len(full_name) < 2: errs.append("Full name is too short.")
    if not re.fullmatch(r".+@.+\..+", email):
        errs.append("Email is invalid.")
    if not re.fullmatch(r"\+?[0-9\-\s]{9,15}", phone):
        errs.append("Phone must be 9–15 digits (spaces/dashes allowed).")
    if len(password) < 6:
        errs.append("Password must be at least 6 characters.")

    if role == "couriers":
        vehicle_type   = (form.get("vehicle_type") or "").strip()
        license_plate  = (form.get("license_plate") or "").strip()
        driver_license = (form.get("driver_license") or "").strip()
        license_expiry = (form.get("license_expiry") or "").strip()
        acct_holder    = (form.get("acct_holder") or "").strip()
        bank_name      = (form.get("bank_name") or "").strip()
        branch_code    = (form.get("branch_code") or "").strip()
        account_number = (form.get("account_number") or "").strip()

        if not vehicle_type:
            errs.append("Vehicle type is required.")
        if not re.fullmatch(r"\d{2}-\d{3}-\d{2}", license_plate):
            errs.append("License plate must match format 12-345-67.")
        if not re.fullmatch(r"\d{7,9}", driver_license):
            errs.append("Driver license should be 7–9 digits.")
        try:
            if dt.date.fromisoformat(license_expiry) <= dt.date.today():
                errs.append("License expiry must be a future date.")
        except ValueError:
            errs.append("Invalid license expiry date.")

        if not acct_holder:    errs.append("Account holder is required.")
        if not bank_name:      errs.append("Bank name is required.")
        if not re.fullmatch(r"\d{1,4}", branch_code):
            errs.append("Branch / Code must be 1–4 digits.")
        if not re.fullmatch(r"\d{5,12}", account_number):
            errs.append("Account number must be 5–12 digits.")
        if not form.get("agree"):
            errs.append("You must agree to the Terms and Privacy Policy.")

    return errs

# --- Route (drop-in replacement) ------------------------------------------

@app.route("/signup", methods=["GET", "POST"])  # type: ignore[name-defined]
def signup():
    """Create accounts for customers or couriers.

    Role precedence: session -> querystring -> default 'customers'.
    Uses plural role names to match the rest of the app.
    """
    role = _normalize_role(session.get("user_type") or request.args.get("user_type") or "customers")

    # Compute safe links here (no template logic)
    login_href = url_for("login_page", user_type=role) if "login_page" in app.view_functions else "#"  # type: ignore[name-defined]
    home_href  = url_for("index") if "index" in app.view_functions else "/"  # type: ignore[name-defined]

    if request.method == "POST":
        errors = _validate_payload(role, request.form)
        if errors:
            for e in errors:
                flash(e, "error")
            return redirect(url_for("signup", user_type=role))

        role = (request.args.get("user_type") or "customers").strip().lower()
        if role == "customers":
            customer_id = _gen_customer_id()
            ds.add_customer({
                "name":         (request.form.get("full_name") or "").strip(),
                "customer_id":  (request.form.get("customer_id") or "").strip(),
                "phone_number": (request.form.get("phone") or "").strip(),
                "email":        (request.form.get("email") or "").strip(),
                "password":     request.form.get("password") or "",
                "credit":       0.0,
            })
            session['user'] = {"customer_id": customer_id, "user_type": "customers"}
            session['user_type'] = 'customers'
            session['user_id'] = customer_id

            flash("Your account was created successfully.", "success")
            return redirect(url_for("signup", user_type=role))
        elif role == "couriers":
            # 0) Take the ID exactly as typed by the manager
            raw_id = (request.form.get("courier_id") or "").strip()
            if not raw_id or not raw_id.isdigit():
                flash("Courier ID must be a numeric value.", "error")
                return redirect(url_for("signup", user_type="couriers"))
            courier_id = int(raw_id)

            # 1) Create the address first and reuse its id (also as initial current_location)
            addr_obj = ds.add_address({
                "street": (request.form.get("street") or "").strip(),
                "house_number": (request.form.get("house_number") or "").strip(),
                "apartment": ((request.form.get("apartment") or "").strip() or None),
                "floor": ((request.form.get("floor") or "").strip() or None),
                "city": (request.form.get("city") or "").strip(),
                "postal_code": (request.form.get("postal_code") or "").strip(),
                "coordinates": None,
                "message": ((request.form.get("message_to_courier") or "").strip() or None),  # ← correct
            })

            address_id = getattr(addr_obj, "address_id", None) or getattr(addr_obj, "id", None)
            try:
                address_id = int(address_id)
            except Exception:
                flash("Failed to create/resolve address id.", "error")
                return redirect(url_for("signup", user_type="couriers"))

            # 2) Build payload exactly as courier.json expects
            payload = {
                "courier_id":       courier_id,
                "name":             (request.form.get("full_name") or "").strip(),
                "address_id":       address_id,
                "current_location": address_id,
                "password":         request.form.get("password") or "",
            }

            # 3) Persist via DispatchSystem; reject duplicates gracefully
            ok = ds.add_courier(payload)
            if not ok:
                flash("A courier with this ID already exists.", "error")
                return redirect(url_for("signup", user_type="couriers"))

            flash("Courier account created.", "success")
            return redirect(url_for("login_page", user_type="couriers"))

    # GET -> choose the correct template while keeping signup.html as the common option
    if role == "couriers":
        # Serve your validated courier page if present; fallback to the shared template
        try:
            return render_template("signup_courier.html", user_type=role, login_href=login_href, home_href=home_href)
        except Exception:
            pass

    return render_template("signup.html", user_type=role, login_href=login_href, home_href=home_href)

def _gen_customer_id() -> str:
    """
    Generate a unique customer ID based on existing customers in the DispatchSystem.
    """
    existing_customers = ds.customers if hasattr(ds, 'customers') else []
    if isinstance(existing_customers, dict):
        ids = [c.get('customer_id') for c in existing_customers.values()]
    else:
        ids = [getattr(c, 'customer_id', None) for c in existing_customers]
    ids = [i for i in ids if i and str(i).startswith('CUST_')]
    max_num = 0
    for cid in ids:
        try:
            num = int(str(cid).replace('CUST_', ''))
            if num > max_num:
                max_num = num
        except Exception:
            continue
    return f"CUST_{max_num + 1}"

def _gen_unique_courier_id(ds: DispatchSystem) -> str:
    """
    Generate a unique courier ID based on existing couriers in the DispatchSystem.
    """
    existing_couriers = ds.couriers if hasattr(ds, 'couriers') else []
    if isinstance(existing_couriers, dict):
        ids = [c.get('courier_id') for c in existing_couriers.values()]
    else:
        ids = [getattr(c, 'courier_id', None) for c in existing_couriers]
    ids = [i for i in ids if i and str(i).startswith('COURIER_')]
    max_num = 0
    for cid in ids:
        try:
            num = int(str(cid).replace('COURIER_', ''))
            if num > max_num:
                max_num = num
        except Exception:
            continue
    return f"COURIER_{max_num + 1}"

def _gen_manager_id() -> str:
    """
    Generate a unique manager ID based on existing managers in the DispatchSystem.
    """
    existing_managers = ds.managers if hasattr(ds, 'managers') else []
    if isinstance(existing_managers, dict):
        ids = [m.get('manager_id') for m in existing_managers.values()]
    else:
        ids = [getattr(m, 'manager_id', None) for m in existing_managers]
    ids = [i for i in ids if i and str(i).startswith('MANAGER_')]
    max_num = 0
    for mid in ids:
        try:
            num = int(str(mid).replace('MANAGER_', ''))
            if num > max_num:
                max_num = num
        except Exception:
            continue
    return f"MANAGER_{max_num + 1}"

@app.route("/orders")
def show_all_orders() -> str:
    orders = ds.view_orders()
    orders_dicts = [order.to_dict() for order in orders]
    return render_template("order_list.html", orders=orders_dicts)

@app.route("/orders/create_courier")
def orders_create_courier():
    # must be logged in + manager
    if 'user' not in session:
        flash('Please log in first', 'error')
        return redirect(url_for('login_page', user_type='managers'))
    if session.get('user_type') != 'managers':
        flash('Only managers can create couriers', 'error')
        return redirect(url_for('show_all_orders', user_type=session.get('user_type', 'customers')))

    # send them into your existing signup flow
    return redirect(url_for('signup', user_type='managers', create='courier'))

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
        apartment = int(apartment_str) if apartment_str and apartment_str.isdigit() else None

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
            assignment_success = ds.assign_closest_courier_to_order(order._package_id)

            if assignment_success:
                # Get the updated order with courier assignment
                updated_order = ds.find_order_by_package_id(order._package_id)
                if updated_order and updated_order._courier_id:
                    # Get the assigned courier
                    assigned_courier = ds.get_courier_by_id(updated_order._courier_id)
                    if assigned_courier:
                        # Update the order's origin_id to courier's current location
                        Order.update_by_package_id(order._package_id, "origin_id", assigned_courier.current_location)
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

@app.route("/signup_courier")
def signup_courier():
    return render_template("signup_courier.html", user_type="couriers")

if __name__ == "__main__":
    app.run()
