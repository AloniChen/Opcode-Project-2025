import json
from typing import Dict, Any, List, Union, Optional

COURIER_JSON = "courier.json"

class Courier:
    """
    Represents a courier with ID, name, password, location, and address.
    """

    def __init__(self, name: str, courier_id: int,
                 address_id: int, current_location: int, password: str):
        """
        Initialize Courier.
        """
        self.courier_id = courier_id
        self.name = name
        self.address_id = address_id
        self.current_location = current_location
        self.password = password

    def __str__(self):
        """Return formatted courier info."""
        return (f"Courier(name={self.name}, ID={self.courier_id}, "
                f"address={self.address}, current location={self.current_location})")

    def str_courier(self) -> str:
        """Return formatted courier info."""
        return (f"Courier(name={self.name}, ID={self.courier_id}, "
                f"address={self.address}, current location={self.current_location}, password={self.password})")

    def to_dict(self) -> Dict:
        """Converts the Courier object to a dictionary for JSON serialization."""
        return {
            "courier_id": self.courier_id,
            "name": self.name,
            "address": self.address.id,
            "current_location": self.current_location,
            "password": self.password}
    
    @classmethod
    def from_dict(cls, data: Dict) -> Courier:
        """Creates a Courier object from a dictionary."""
        return cls(data["name"], data["courier_id"], data["password"],
                   current_location, address)

    @staticmethod
    def _load_all_from_json(json_file: str = JSON_FILE) -> List[Dict]:
        """
        Helper static method to load all raw courier dictionaries from the JSON file.
        Returns an empty list if the file doesn't exist or is invalid.
        """
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print(f"Warning: {json_file} is empty or contains invalid JSON. Starting with empty data.")
            return []

    @staticmethod
    def _save_all_to_json(couriers_data: List[Dict], json_file: str = JSON_FILE):
        """
        Helper static method to save a list of raw courier dictionaries to the JSON file.
        """
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(couriers_data, f, indent=4, ensure_ascii=False)

    @classmethod
    def create_courier(cls, courier: 'Courier') -> bool:
        """
        Adds a new courier to the JSON file.
        Returns True if successful, False if a courier with the same ID already exists.
        Note: This re-reads and re-writes the entire file for each operation.
        """
        all_couriers_data = cls._load_all_from_json()
        all_couriers_data.append(courier.to_dict())
        cls._save_all_to_json(all_couriers_data)
        print(f"Courier {courier.name} created successfully.")
        return True

    @classmethod
    def get_courier_by_id(cls, courier_id: int) -> 'Courier':
        """
        Retrieves a courier by their ID from the JSON file.
        Returns the Courier object if found, otherwise None.
        Note: This re-reads the entire file for each operation.
        """
        all_couriers_data = cls._load_all_from_json()
        for data in all_couriers_data:
            if data['courier_id'] == courier_id:
                return cls.from_dict(data)
        print(f"Courier with ID {courier_id} not found.")
        return None

    @classmethod
    def update_courier(cls, courier_id: int, new_data: Dict[str, Union[str, int, Address]]) -> bool:
        """
        Updates an existing courier's information in the JSON file.
        new_data can contain 'name', 'password', 'current_location', 'address'.
        Returns True if successful, False if the courier is not found.
        Note: This re-reads and re-writes the entire file for each operation.
        """
        all_couriers_data = cls._load_all_from_json()
        found = False
        for i, data in enumerate(all_couriers_data):
            if data['courier_id'] == courier_id:
                if 'name' in new_data:
                    data['name'] = new_data['name']
                if 'password' in new_data:
                    data['password'] = new_data['password']
                if 'current_location' in new_data and isinstance(new_data['current_location'], Address):
                    data['current_location'] = new_data['current_location'].to_dict()
                if 'address' in new_data and isinstance(new_data['address'], Address):
                    data['address'] = new_data['address'].to_dict()
                all_couriers_data[i] = data
                found = True
                break

        if found:
            cls._save_all_to_json(all_couriers_data)
            print(f"Courier with ID {courier_id} updated successfully.")
            return True
        else:
            print(f"Error: Courier with ID {courier_id} not found for update.")
            return False

    @classmethod
    def delete_csourier(cls, courier_id: int) -> bool:
        """
        Deletes a courier by their ID from the JSON file.
        Returns True if successful, False if the courier is not found.
        Note: This re-reads and re-writes the entire file for each operation.
        """
        all_couriers_data = cls._load_all_from_json()
        initial_count = len(all_couriers_data)
        all_couriers_data = [d for d in all_couriers_data if d['courier_id'] != courier_id]

        if len(all_couriers_data) < initial_count:
            cls._save_all_to_json(all_couriers_data)
            print(f"Courier with ID {courier_id} deleted successfully.")
            return True
        else:
            print(f"Error: Courier with ID {courier_id} not found for deletion.")
            return False

    @classmethod
    def read_couriers(cls) -> List['Courier']:
        """
        Returns a list of all couriers from the JSON file.
        Note: This re-reads the entire file for each operation.
        """
        all_couriers_data = cls._load_all_from_json()
        return [cls.from_dict(d) for d in all_couriers_data]