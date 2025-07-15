import json
from typing import List, Dict
from order import Order

_logger = logging.getLogger(__name__)


class DispatchSystem:
    """
    A class to manage the dispatch system.
    """

    def update_order_status(self, package_id, package_status) -> None:
        Order.update_by_package_id(package_id, "status", package_status)

    def view_orders(self) -> List[Order]:
        try:
            with open("orders.json", "r") as file:
                orders = json.load(file)
            orders_list = []
            for order in orders:
                orders_list.append(Order(order.get("customer_id"), order.get("courier_id"), order.get("origin_id"),
                                         order.get('destination_id'), order.get("package_id"), order.get("status"), auto_save=False))
            return orders_list
        except FileNotFoundError:
            print("Orders file not found")
            return []

    def find_order_by_package_id(self, package_id) -> Order:
        try:
            with open("orders.json", "r") as file:
                orders = json.load(file)
            for order in orders:
                if order.get("package_id") == package_id:
                    this_order = Order(order.get("customer_id"), order.get("courier_id"), order.get("origin_id"),
                                       order.get('destination_id'), order.get("package_id"), order.get("status"), auto_save=False)
                    return this_order
            print(f"Order {package_id} not found")
            return None
        except FileNotFoundError:
            print("Orders file not found")
            return None
