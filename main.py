from customer import Customer
from customerList import add_customer, get_customer_by_id, update_customer, delete_customer


def save_customer(customer_dict):
    existing = get_customer_by_id(customer_dict["customer_id"])
    if existing:
        update_customer(customer_dict)
        print("customer has been updated")
    else:
        add_customer(customer_dict)
        print("new customer has been added")

# Create new customer
cust = Customer("Chen", 1, "050-1234567", "aaa@example.com", "mypassword", 150)
cust.add_address("Tel Aviv")
save_customer(cust.to_dict())

# update address and phone number to an existin customer
existing = get_customer_by_id(1)
if existing:
    existing["phone_number"] = "050-9999999"
    if "Beer Sheva" not in existing["address"]:
        existing["address"].append("Beer Sheva")
    update_customer(existing)
else:
    print("הלקוח לא נמצא")

delete_customer(1)

