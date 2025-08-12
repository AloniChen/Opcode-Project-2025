import json
import logging
from re import M
from typing import List, Optional
from courier import Courier
from manager import Manager
from customer import Customer
from customerList import add_customer, get_customer_by_id, update_customer, delete_customer
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
        self.managers_file: Path = Path("data") / managers_file
        address_path: Path = Path("data") / address_file

        if not self.managers_file.exists():
            self._save_all_managers([])

        self.address_repo = AddressRepository(address_path)

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

    def add_manager(self, manager_dict: dict) -> bool:
        """
        Adds a new manager to the system.
        Returns True if added successfully, False if manager already exists.
        """
        managers = self._load_all_managers()
        if any(m["manager_id"] == manager_dict["manager_id"] for m in managers):
            _logger.warning(
                f"Manager ID {manager_dict['manager_id']} already exists.")
            return False

        # Create a Manager object from the dict
        manager = Manager(
            manager_dict["name"],
            manager_dict["manager_id"],
            manager_dict["phone_number"],
            manager_dict["email"],
            manager_dict["password"]
        )
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

    def add_courier(self, courier_dict: dict) -> bool:
        """
        Adds a new courier to the system.
        Returns True if successful, False if the courier already exists.
        """
        # צור אובייקט Courier מה־dict
        courier = Courier(
            courier_dict["name"],
            courier_dict["courier_id"],
            courier_dict["address_id"],
            courier_dict["current_location"],
            courier_dict["password"]
        )
        if Courier.courier_exists(courier.courier_id):
            _logger.error(
                f"Courier with ID {courier.courier_id} already exists")
            return False
        Courier.create_courier(courier)
        _logger.info(f"Courier {courier.name} added successfully.")
        return True

    def delete_courier(self, courier_id: int) -> bool:
        """
        Deletes a courier by their ID.
        Returns True if deleted successfully, False if courier does not exist.
        """
        if Courier.courier_exists(courier_id):
            Courier.delete_courier(courier_id)
            _logger.info(f"Courier with ID {courier_id} deleted successfully.")
            return True
        _logger.warning(f"Courier with ID {courier_id} not found.")
        return False

    def get_courier_by_id(self, courier_id: int) -> Optional[Courier]:
        """
        Returns the Courier object with the given courier_id, or None if not found.
        """
        courier = Courier.get_courier_by_id(courier_id)
        if courier:
            return courier
        _logger.info(f"Courier with ID {courier_id} not found.")
        return None

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
    def update_order_status(package_id, package_status: PackageStatus) -> bool:
        return Order.update_by_package_id(package_id, "status", package_status.value)

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
    def find_order_by_package_id(package_id) -> Optional[Order]:
        try:
            with open("data/orders.json", "r") as file:
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

    @staticmethod
    def delete_order(package_id) -> bool:
        try:
            with open("orders.json", "r") as file:
                orders = json.load(file)
            new_orders = [order for order in orders if order.get(
                "package_id") != package_id]
            if len(new_orders) == len(orders):
                print(f"Order {package_id} not found")
                return False
            with open("orders.json", "w") as file:
                json.dump(new_orders, file, indent=4)
            print(f"Order {package_id} deleted successfully")
            return True
        except FileNotFoundError:
            print("Orders file not found")
            return False

    def save_customer(self, customer_dict):
        existing = get_customer_by_id(customer_dict["customer_id"])
        if existing:
            update_customer(customer_dict)
            print("customer has been updated")
        else:
            add_customer(customer_dict)
            print("new customer has been added")

    def add_customer(self, customer_dict: dict) -> bool:
        """
        Adds a new customer to the system.
        Returns True if added successfully, False if customer already exists.
        """
        existing = get_customer_by_id(customer_dict["customer_id"])
        if existing:
            # Customer already exists
            return False
        add_customer(customer_dict)
        return True

    def get_customer_by_id(self, customer_id: str) -> Optional[Customer]:
        """
        Returns the Customer object with the given customer_id, or None if not found.
        """
        customer_dict = get_customer_by_id(customer_id)
        if customer_dict:
            # ודא שיש לך from_dict במחלקה Customer
            return Customer.from_dict(customer_dict)
        return None

    def update_customer(self, customer: Customer) -> bool:
        """
        Updates an existing customer in the system.
        Returns True if updated successfully, False if customer does not exist.
        """
        customer_dict = customer.to_dict()
        existing = get_customer_by_id(customer.customer_id)
        if not existing:
            return False
        update_customer(customer_dict)
        return True

    def delete_customer(self, customer_id: str) -> bool:
        """
        Deletes a customer by their ID.
        Returns True if deleted successfully, False if customer does not exist.
        """
        existing = get_customer_by_id(customer_id)
        if not existing:
            return False
        delete_customer(customer_id)
        return True

    def assign_closest_courier_to_order(self, package_id) -> bool:
        """
        Assigns the closest courier to the order by calculating the distance between
        the courier's current_location and the order's destination_id using their Address coordinates.
        Assumes all couriers are available.
        Returns True if successful, False otherwise.
        """
        order = self.find_order_by_package_id(package_id)
        if not order:
            _logger.error(f"Order with package ID {package_id} not found.")
            return False

        couriers = Courier.read_couriers()
        if not couriers:
            _logger.error("No couriers available.")
            return False

        # Get Address objects for destination and couriers' locations
        destination_address = self.get_address_by_id(order._destination_id)
        if not destination_address:
            _logger.error(
                f"Destination address ID {order._destination_id} not found.")
            return False

        closest_courier = None
        min_distance = float('inf')
        for courier in couriers:
            courier_address = self.get_address_by_id(courier.current_location)
            if not courier_address or not courier_address.coordinates or not destination_address.coordinates:
                continue
            # Calculate Euclidean distance between coordinates
            x1, y1 = courier_address.coordinates
            x2, y2 = destination_address.coordinates
            distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_courier = courier

        if not closest_courier:
            _logger.error(
                "No available couriers with valid addresses to assign.")
            self.update_order_status(package_id, PackageStatus.NOT_ASSIGNED)
            return False

        # Assign the closest courier using the static method
        if Order.update_by_package_id(order._package_id, "courier_id", closest_courier.courier_id):
            _logger.info(
                f"Order {package_id} assigned to courier {closest_courier.courier_id}.")
            self.update_order_status(package_id, PackageStatus.CONFIRMED)
            return True
        else:
            _logger.error(
                f"Failed to update order {package_id} with courier {closest_courier.courier_id}.")
            self.update_order_status(package_id, PackageStatus.NOT_ASSIGNED)
            return False
