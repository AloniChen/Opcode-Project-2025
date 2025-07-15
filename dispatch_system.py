
from address_repository import AddressRepository
from pathlib import Path
from address import Address 
import json
from typing import List, Dict
from order import Order

_logger = logging.getLogger(__name__)


class DispatchSystem:
    """
    A class to manage the dispatch system.
    """
    def __init__(self, address_file: Path):
        self.address_repo = AddressRepository(address_file)
        # בעתיד נוכל להוסיף גם:
        # self.customer_repo = CustomerRepository(...)
        # self.order_repo = OrderRepository(...)
        # self.courier_repo = CourierRepository(...)

    def add_address(self, address_data: dict) -> Address:
        """
        Creates and stores a new Address from dictionary data.
        Returns the new address ID.
        """
        new_address = Address(**address_data)
        self.address_repo.add(new_address)
        return new_address

    def get_address_by_id(self, address_id: int):
        return self.address_repo.get_by_id(address_id)

    def delete_address_by_id(self, address_id: int) -> bool:
        return self.address_repo.delete_by_id(address_id)

    def update_address_by_id(self, address_id: int, new_data: dict) -> bool:
        return self.address_repo.update_by_id(address_id, new_data)

    def list_all_addresses(self):
        return self.address_repo.get_all()

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

