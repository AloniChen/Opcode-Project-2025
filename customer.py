class Customer:
    def __init__(self, name, customer_id, phone_number, email, password, credit):

        self.name = name
        self.customer_id = customer_id
        self.address = []
        self.phone_number =phone_number
        self.email = email
        self.password = password
        self.credit = credit
    
    def add_address(self, address):
        self.address.append(address)

    def __str__(self):
        return f"{self.name}, {self.customer_id}, {self.address}, {self.phone_number}, {self.email},  {self.password}, {self.credit}"
    
    def to_dict(self):
        return {
            "name": self.name,
            "customer_id": self.customer_id,
            "address": self.address, #loop for list of IDs
            "phone_number": self.phone_number,
            "email": self.email,
            "password": self.password,
            "credit": self.credit
        }
    
    