import json
import logging
from typing import List, Optional, Dict
from courier import Courier
from enum import Enum
from customer import Customer
from customerList import add_customer, get_customer_by_id, update_customer
from address_repository import AddressRepository
from pathlib import Path
from address import Address
from order import Order

_logger = logging.getLogger(__name__)

class PackageStatus(Enum):
    CREATED = "created"
    CONFIRMED = "confirmed"
    ON_DELIVERY = "on-delivery"
    DELIVERED = "delivered"
    CANCELED = "canceled"

class DispatchSystem:
    """
    A class to manage the dispatch system, including couriers and their operations.
    """

    def add_courier(self, courier: Courier) -> bool:
        """
        Adds a new courier to the system.
        Returns True if successful, False if the courier already exists.
        """
        if Courier.courier_exists(courier.courier_id):
            _logger.error(
                f"Courier with ID {courier.courier_id} already exists")
            return False
        Courier.create_courier(courier)
        _logger.info(f"Courier {courier.name} added successfully.")
        return True

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

    @staticmethod
    def add_order(order_data: dict) -> Order:
        new_order = Order(**order_data)
        return new_order

    @staticmethod
    def update_order_status(package_id, package_status: PackageStatus) -> None:
        Order.update_by_package_id(package_id, "status", package_status.value)

    @staticmethod
    def view_orders() -> List[Order]:
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

    @staticmethod
    def find_order_by_package_id(package_id) -> Order | None:
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
    def save_customer(self, customer_dict):
        existing = get_customer_by_id(customer_dict["customer_id"])
        if existing:
            update_customer(customer_dict)
            print("customer has been updated")
        else:
            add_customer(customer_dict)
            print("new customer has been added")