import json
import logging
from typing import List, Dict, Optional
from courier import Courier

from manager import Manager

from customer import Customer
from customerList import add_customer, get_customer_by_id, update_customer
from address_repository import AddressRepository
from pathlib import Path
from address import Address
from order import Order
from order import PackageStatus


_logger = logging.getLogger(__name__)

class DispatchSystem:
    """
    A class to manage the dispatch system, including couriers and their operations.
    """

    def __init__(self, managers_file: str, address_file: str):
        managers_file = Path("data\\"+managers_file)
        address_file = Path("data\\"+address_file)
        self.managers_file = managers_file
        if not self.managers_file.exists():
            self._save_all_managers([])  # Create file if missing
        self.address_repo = AddressRepository(address_file)

    def _load_all_managers(self) -> List[dict]:
        try:
            with open(self.managers_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            _logger.warning("Managers file not found.")
            return []

    def _save_all_managers(self, managers: List[dict]) -> None:
        with open(self.managers_file, "w") as file:
            json.dump(managers, file, indent=4)

    def add_manager(self, manager: Manager) -> bool:

        managers = self._load_all_managers()
        if any(m["manager_id"] == manager.manager_id for m in managers):
            _logger.warning(f"Manager ID {manager.manager_id} already exists.")
            return False

        managers.append(manager.to_dict())
        self._save_all_managers(managers)
        _logger.info(f"Manager {manager.name} added successfully.")
        return True

    def get_manager_by_id(self, manager_id: str) -> Optional[Manager]:
        managers = self._load_all_managers()
        for m in managers:
            if m["manager_id"] == manager_id:
                return Manager.from_dict(m)
        _logger.info(f"Manager ID {manager_id} not found.")
        return None

    def list_all_managers(self) -> List[Manager]:
        return [Manager.from_dict(m) for m in self._load_all_managers()]

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
    def find_order_by_package_id(package_id) -> Order:
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

