class Manager:
    def __init__(self, name, manager_id, phone_number, email, password):

        self.name = name
        self.manager_id = manager_id
        self.phone_number = phone_number
        self.email = email
        self.password = password

    def __str__(self):
        return f"Manager(Name: {self.name}, ID: {self.manager_id}, Phone: {self.phone_number}, Email: {self.email})"
    
    def to_dict(self):
        return {
            "name": self.name,
            "manager_id": self.manager_id,
            "phone_number": self.phone_number,
            "email": self.email,
            "password": self.password
        }
    