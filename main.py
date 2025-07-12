from customer import Customer
from customerList import add_or_update_customer, get_customer_by_id, update_customer, delete_customer

# יצירת לקוח חדש
cust = Customer("Chen", 1, "050-1234567", "aaa@example.com", "mypassword", 150)
cust.add_address("Tel Aviv")
add_or_update_customer(cust.to_dict())

# עדכון כתובת ומספר טלפון ללקוח קיים
existing = get_customer_by_id(1)
if existing:
    existing["phone_number"] = "050-9999999"
    if "Beer Sheva" not in existing["address"]:
        existing["address"].append("Beer Sheva")
    update_customer(existing)
else:
    print("הלקוח לא נמצא")

delete_customer(1)

