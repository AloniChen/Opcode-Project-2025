import json
def find_order_by_package_id(package_id):
    try:
        with open("orders.json", "r") as file:
            orders = json.load(file)
        for order in orders:
            if order.get("package_id") == package_id:
                print("ORDER FOUND:")
                print(f"Package ID: {order['package_id']}")
                print(f"Customer: {order['customer_id']}")
                print(f"Courier: {order['courier_id']}")
                print(f"Route: {order['origin']} → {order['destination']}")
                print(f"Status: {order['status']}")
                return
        print(f"Order {package_id} not found")
    except FileNotFoundError:
        print("Orders file not found")