import json
import os
from typing import Dict, Any, List

class Order:
    _json_filename = "orders.json"
    def __init__(self, package_id, customer_id, courier_id, origin, destination, status="confirmed"):
        self._package_id = package_id
        self._customer_id = customer_id
        self._courier_id = courier_id
        self._origin = origin
        self._destination = destination
        self._status = status
        self._order_to_json()           #save to JSON file

    def __str__(self):
        return f"Order(package_id={self._package_id}, customer_id={self._customer_id}, courier_id={self._courier_id}, origin={self._origin}, destination={self._destination}, status={self._status})"

    def _order_to_json(self):
        try:
            if os.path.exists(self._json_filename):
                with open(self._json_filename, 'r', encoding='utf-8') as file:
                    try:
                        orders = json.load(file)     #load existing orders form the json file
                        if not isinstance(orders, list):        #not valid json file
                            orders = []             #we will rewrite the json file
                    except json.JSONDecodeError:
                        orders = []          #we will rewrite the json file
            else:
                orders = []                 #first order to be written to the json file
            order_dict = self.to_dict()     #convert this order to dictionary
            orders.append(order_dict)       #add the recent order to orders list
            with open(self._json_filename, 'w', encoding='utf-8') as file:
                json.dump(orders, file, indent=2, ensure_ascii=False)   #save back to file
        except Exception as e:
            print(f"Error saving order to JSON: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert order object to dictionary."""
        return \
        {
            "package_id": self._package_id,
            "customer_id": self._customer_id,
            "courier_id": self._courier_id,
            "origin": self._origin,
            "destination": self._destination,
            "status": self._status,
        }
