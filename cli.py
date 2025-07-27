from dispatch_system import DispatchSystem

from order import PackageStatus


def main_menu():
    print("\n--- Delivery Management System ---")
    print("1. Customer Management")
    print("2. Courier Management")
    print("3. Manager Management")
    print("4. Address Management")
    print("5. Order Management")
    print("6. Exit")
    return input("Choose an option (1-6): ")


def customer_menu():
    print("\n--- Customer Management ---")
    print("1. Add Customer")
    print("2. Update Customer")
    print("3. Delete Customer")
    print("4. Show Customer")
    print("5. Back")
    return input("Choose an option (1-5): ")


def courier_menu():
    print("\n--- Courier Management ---")
    print("1. Add Courier")
    print("2. Delete Courier")
    print("3. Show Courier")
    print("4. Back")
    return input("Choose an option (1-4): ")


def manager_menu():
    print("\n--- Manager Management ---")
    print("1. Add Manager")
    print("2. Show Manager")
    print("3. Back")
    return input("Choose an option (1-3): ")


def address_menu():
    print("\n--- Address Management ---")
    print("1. Add Address")
    print("2. Show Address")
    print("3. Back")
    return input("Choose an option (1-3): ")


def order_menu():
    print("\n--- Order Management ---")
    print("1. Create New Order")
    print("2. Update Order Status")
    print("3. Track Order")
    print("4. Delete Order")
    print("5. Show Order")
    print("6. Back")
    return input("Choose an option (1-6): ")


def run_cli():
    ds: DispatchSystem = DispatchSystem("managers.json", "addresses.json")
    while True:
        choice = main_menu()
        if choice == "1":
            while True:
                c_choice = customer_menu()
                if c_choice == "1":
                    data = {
                        "name": input("Name: "),
                        "customer_id": input("Customer ID: "),
                        "phone_number": input("Phone: "),
                        "email": input("Email: "),
                        "password": input("Password: "),
                        "credit": float(input("Credit: "))
                    }
                    success = ds.add_customer(data)
                    print(
                        "Customer added successfully." if success else "Failed to add customer.")
                elif c_choice == "2":
                    customer_id = input("Customer ID: ")
                    customer = ds.get_customer_by_id(customer_id)
                    if not customer:
                        print("Customer not found.")
                        continue
                    print("Leave blank to keep current value.")
                    for field in ["name", "phone_number", "email", "password", "credit"]:
                        val = input(
                            f"{field.capitalize()} ({getattr(customer, field)}): ")
                        if val:
                            setattr(customer, field, float(val)
                                    if field == "credit" else val)
                    updated = ds.update_customer(customer)
                    print(
                        "Customer updated." if updated else "Failed to update customer.")
                elif c_choice == "3":
                    customer_id = input("Customer ID: ")
                    deleted = ds.delete_customer(customer_id)
                    print("Customer deleted." if deleted else "Customer not found.")
                elif c_choice == "4":
                    customer_id = input("Customer ID: ")
                    customer = ds.get_customer_by_id(customer_id)
                    print(customer if customer else "Not found.")
                elif c_choice == "5":
                    break
                else:
                    print("Invalid choice.")
        elif choice == "2":
            while True:
                co_choice = courier_menu()
                if co_choice == "1":
                    data = {
                        "name": input("Name: "),
                        "courier_id": int(input("Courier ID: ")),
                        "address_id": int(input("Address ID: ")),
                        "current_location": int(input("Current Location: ")),
                        "password": input("Password: ")
                    }
                    success = ds.add_courier(data)
                    print(
                        "Courier added successfully." if success else "Failed to add courier.")
                elif co_choice == "2":
                    courier_id = int(input("Courier ID: "))
                    deleted = ds.delete_courier(courier_id)
                    print("Courier deleted." if deleted else "Courier not found.")
                elif co_choice == "3":
                    courier_id = int(input("Courier ID: "))
                    courier = ds.get_courier_by_id(courier_id)
                    print(courier if courier else "Not found.")
                elif co_choice == "4":
                    break
                else:
                    print("Invalid choice.")
        elif choice == "3":
            while True:
                m_choice = manager_menu()
                if m_choice == "1":
                    data = {
                        "name": input("Name: "),
                        "manager_id": input("Manager ID: "),
                        "phone_number": input("Phone: "),
                        "email": input("Email: "),
                        "password": input("Password: ")
                    }
                    success = ds.add_manager(data)
                    print(
                        "Manager added successfully." if success else "Failed to add manager.")
                elif m_choice == "2":
                    manager_id = input("Manager ID: ")
                    manager = ds.get_manager_by_id(manager_id)
                    print(manager if manager else "Not found.")
                elif m_choice == "3":
                    break
                else:
                    print("Invalid choice.")
        elif choice == "4":
            while True:
                a_choice = address_menu()
                if a_choice == "1":
                    data = {
                        "street": input("Street: "),
                        "house_number": int(input("House Number: ")),
                        "city": input("City: "),
                        "postal_code": input("Postal Code: "),
                        "country": input("Country: "),
                        "apartment": int(input("Apartment (optional): ") or 0) or None,
                        "floor": int(input("Floor (optional): ") or 0) or None,
                        "message": input("Message to courier (optional): ") or None
                    }
                    addr = ds.add_address(data)
                    print(f"Address added: {addr}")
                elif a_choice == "2":
                    address_id = int(input("Address ID: "))
                    addr = ds.get_address_by_id(address_id)
                    print(addr if addr else "Not found.")
                elif a_choice == "3":
                    break
                else:
                    print("Invalid choice.")
        elif choice == "5":
            while True:
                o_choice = order_menu()
                if o_choice == "1":
                    data = {
                        "customer_id": input("Customer ID: "),
                        "courier_id": int(input("Courier ID: ")),
                        "origin_id": int(input("Origin Address ID: ")),
                        "destination_id": int(input("Destination Address ID: "))
                    }
                    order = ds.add_order(data)
                    print("Order created." if order else "Failed to create order.")
                elif o_choice == "2":
                    package_id = int(input("Package ID: "))
                    print("Choose new status:")
                    status_options = list(PackageStatus)
                    for idx, status in enumerate(status_options, 1):
                        print(f"{idx}. {status.value}")
                    status_choice = int(input("Enter status number: "))
                    if 1 <= status_choice <= len(status_options):
                        # שלח את ה-Enum עצמו
                        status = status_options[status_choice - 1]
                        updated = ds.update_order_status(package_id, status)
                        print("Status updated." if updated else "Order not found.")
                    else:
                        print("Invalid status choice.")
                elif o_choice == "3":
                    orders = ds.view_orders()
                    if not orders:
                        print("No orders found.")
                    else:
                        for order in orders:
                            print(order)
                elif o_choice == "4":
                    package_id = int(input("Package ID: "))
                    deleted = ds.delete_order(package_id)
                    print("Order deleted." if deleted else "Order not found.")
                elif o_choice == "5":
                    package_id = int(input("Package ID: "))
                    order = ds.find_order_by_package_id(package_id)
                    print(order if order else "Not found.")
                elif o_choice == "6":
                    break
                else:
                    print("Invalid choice.")
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    run_cli()
