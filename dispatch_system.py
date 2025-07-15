from customer import Customer
from customerList import add_customer, get_customer_by_id, update_customer

class DispatchSystem:

    def save_customer(self, customer_dict):
        existing = get_customer_by_id(customer_dict["customer_id"])
        if existing:
            update_customer(customer_dict)
            print("customer has been updated")
        else:
            add_customer(customer_dict)
            print("new customer has been added")

    