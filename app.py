from dispatch_system import DispatchSystem
from flask import Flask, render_template

app = Flask(__name__)


ds: DispatchSystem = DispatchSystem("managers.json", "addresses.json")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/orders")
def show_all_orders():
    orders = ds.view_orders()
    orders_dicts = [order.to_dict() for order in orders]
    return render_template("order_list.html", orders=orders_dicts)


if __name__ == "__main__":
    app.run(debug=True)
