import json
import os

JSON_FILE = "customers.json"

def load_customers():
    if not os.path.exists(JSON_FILE):
        return []
    with open(JSON_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_customers(customers):
    with open(JSON_FILE, "w") as f:
        json.dump(customers, f, indent=4)

def add_or_update_customer(customer_dict):
    customers = load_customers()
    for idx, existing_customer in enumerate(customers):
        if existing_customer["customer_id"] == customer_dict["customer_id"]:
            customers[idx] = customer_dict
            break
    else:
        customers.append(customer_dict)
    save_customers(customers)

def get_customer_by_id(customer_id):
    customers = load_customers()
    for customer in customers:
        if customer["customer_id"] == customer_id:
            return customer
    return None

def update_customer(updated_customer):
    customers = load_customers()
    for idx, customer in enumerate(customers):
        if customer["customer_id"] == updated_customer["customer_id"]:
            customers[idx] = updated_customer
            save_customers(customers)
            return True
    return False

def update_customer_address(customer_id, new_address=None, address_to_remove=None):
    customers = load_customers()
    updated = False

    for customer in customers:
        if customer["customer_id"] == customer_id:
            if new_address and new_address not in customer["address"]:
                customer["address"].append(new_address)
                updated = True
            if address_to_remove and address_to_remove in customer["address"]:
                customer["address"].remove(address_to_remove)
                updated = True
            break

    if updated:
        save_customers(customers)

def delete_customer(customer_id):
    customers = load_customers()
    new_customers = [c for c in customers if c["customer_id"] != customer_id]

    if len(new_customers) != len(customers):
        save_customers(new_customers)
        print(f"Customer {customer_id} deleted.")
        return True
    else:
        print("Customer not found.")
        return False
