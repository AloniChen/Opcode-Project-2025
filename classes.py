
class Courier:
    """
    Represents a courier with ID, name, password, location, and address.
    """

    def __init__(self, name: str, courier_id: int, password: str,
                 current_location: Address, address: Address):
        """
        Initialize Courier.

        Raises:
            ValueError: If name is empty.
            TypeError: If address is not Address.
            TypeError: If current_location is not Address.
        """
        if not name:
            raise ValueError("Courier must have a name.")
        if not isinstance(address, Address):
            raise TypeError("address must be an instance of Address.")
        if not isinstance(current_location, Address):
            raise TypeError("current_location must be an instance of Address.")
        self.name = name
        self.courier_id = courier_id
        self.address = address
        self.current_location = current_location
        self.password = password

    def __str__(self):
        """Return formatted courier info."""
        return (f"Courier(name={self.name}, ID={self.courier_id}, "
                f"address={self.address}, current location={self.current_location}, password={self.password})")