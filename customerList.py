import json
import os

def add_customer_to_json_file(customer, filename= "customerList.json"):
        data = []

        if os.path.exists(filename):
            with open(filename, "r") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    pass
        data.append(customer.to_dictionary())

        with open(filename, "w") as file:
            json.dump(data, file, indent=4)            

