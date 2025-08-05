from flask import Flask, render_template, request, redirect, session
from dispatch_system import DispatchSystem
from order import Order, PackageStatus

app = Flask(__name__)
ds = DispatchSystem("managers.json", "addresses.json")

app.secret_key = 'my_secret_key'
role = "courier"  # Example role, can be 'customer' or 'courier'
user_id = 3


@app.route("/")
def index():
    return render_template("index.html")


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
