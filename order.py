import json
import os
from typing import Dict, Any, List, Optional
from enum import Enum


class PackageStatus(Enum):
    CREATED = "created"
    CONFIRMED = "confirmed"
    DELIVERED = "delivered"
    CANCELED = "canceled"
    ON_DELIVERY = "on-delivery"


class Order:
    _json_filename = "orders.json"
    _package_number = 0

    def __init__(self, customer_id, courier_id, origin_id, destination_id, package_id=None, status=PackageStatus.CONFIRMED, auto_save=True):
        if Order._package_number == 0:
            Order._initialize_package_number()
        if package_id is None:
            self._package_id = Order._package_number
            Order._package_number += 1
        else:
            self._package_id = package_id
        self._customer_id = customer_id
        self._courier_id = courier_id
        self._origin_id = origin_id
        self._destination_id = destination_id
        self._status = status
        # Only save to JSON if auto_save is True
        if auto_save:
            self.create()  # save to JSON file

    def __str__(self):
        return f"Order(package_id={self._package_id}, customer_id={self._customer_id}, courier_id={self._courier_id}, origin_id={self._origin_id}, destination_id={self._destination_id}, status={self._status})"

    @classmethod
    def _initialize_package_number(cls):
        """Initialize _package_number based on existing orders in JSON file"""
        try:
            if os.path.exists(cls._json_filename):
                with open(cls._json_filename, 'r', encoding='utf-8') as file:
                    try:
                        orders = json.load(file)
                        if isinstance(orders, list) and orders:
                            # Find the highest package_id and set _package_number to be higher
                            max_id = max(order.get("package_id", 0)
                                         for order in orders)
                            cls._package_number = max_id + 1
                        else:
                            cls._package_number = 1
                    except json.JSONDecodeError:
                        cls._package_number = 1
            else:
                cls._package_number = 1
        except Exception as e:
            print(f"Error initializing package number: {e}")
            cls._package_number = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert order object to dictionary."""
        return \
            {
                "package_id": self._package_id,
                "customer_id": self._customer_id,
                "courier_id": self._courier_id,
                "origin_id": self._origin_id,
                "destination_id": self._destination_id,
                "status": self._status.value if hasattr(self._status, "value") else self._status,
            }

    def _load_orders(self) -> List[Dict[str, Any]]:
        """Load orders from JSON file"""
        try:
            if os.path.exists(self._json_filename):
                with open(self._json_filename, 'r', encoding='utf-8') as file:
                    try:
                        orders = json.load(file)
                        if not isinstance(orders, list):
                            return []
                        return orders
                    except json.JSONDecodeError:
                        return []
            else:
                return []
        except Exception as e:
            print(f"Error loading orders: {e}")
            return []

    def _save_orders(self, orders: List[Dict[str, Any]]) -> bool:
        """Save orders to JSON file"""
        try:
            with open(self._json_filename, 'w', encoding='utf-8') as file:
                json.dump(orders, file, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving orders: {e}")
            return False

    def create(self) -> bool:
        """Create new order in JSON file"""
        try:
            orders = self._load_orders()
            # Check for duplicate package_id
            for existing_order in orders:
                if existing_order.get("package_id") == self._package_id:
                    return False
            # Add new order
            order_dict = self.to_dict()
            orders.append(order_dict)
            # Save to file
            if self._save_orders(orders):
                return True
            else:
                return False
        except Exception as e:
            print(f"Error creating order: {e}")
            return False

    @classmethod
    def update_by_package_id(cls, package_id: int, field_name: str, new_value: int) -> bool:
        """Update an order by package_id without creating an object"""
        try:
            with open(cls._json_filename, 'r', encoding='utf-8') as file:
                orders = json.load(file)
            for order in orders:
                if order.get("package_id") == package_id:
                    order[field_name] = new_value
                    with open(cls._json_filename, 'w', encoding='utf-8') as file:
                        json.dump(orders, file, indent=2, ensure_ascii=False)
                    return True
            return False
        except:
            return False

    @classmethod
    def delete_by_package_id(cls, package_id: str) -> bool:
        """Delete an order by package_id"""
        try:
            if not os.path.exists(cls._json_filename):
                return False
            with open(cls._json_filename, 'r', encoding='utf-8') as file:
                orders = json.load(file)
                if not isinstance(orders, list):
                    return False
            # Find and remove the order
            original_count = len(orders)
            orders = [order for order in orders if order.get(
                "package_id") != package_id]
            if len(orders) < original_count:
                # Order was found and removed
                with open(cls._json_filename, 'w', encoding='utf-8') as file:
                    json.dump(orders, file, indent=2, ensure_ascii=False)
                return True
            else:
                return False
        except Exception as e:
            print(f"Error deleting order: {e}")
            return False
