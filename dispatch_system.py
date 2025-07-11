from address_repository import AddressRepository
from pathlib import Path
from address import Address 

class DispatchSystem:
    def __init__(self, address_file: Path):
        self.address_repo = AddressRepository(address_file)
        # בעתיד נוכל להוסיף גם:
        # self.customer_repo = CustomerRepository(...)
        # self.order_repo = OrderRepository(...)
        # self.courier_repo = CourierRepository(...)

    def add_address(self, address_data: dict) -> int:
        """
        Creates and stores a new Address from dictionary data.
        Returns the new address ID.
        """
        new_address = Address(**address_data)
        self.address_repo.add(new_address)
        return new_address.id

    def get_address_by_id(self, address_id: int):
        return self.address_repo.get_by_id(address_id)

    def delete_address_by_id(self, address_id: int) -> bool:
        return self.address_repo.delete_by_id(address_id)

    def update_address_by_id(self, address_id: int, new_data: dict) -> bool:
        return self.address_repo.update_by_id(address_id, new_data)

    def list_all_addresses(self):
        return self.address_repo.get_all()
