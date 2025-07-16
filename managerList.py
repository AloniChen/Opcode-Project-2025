import json
import os

JSON_FILE = 'managers.json'


def load_managers():
    if not os.path.exists(JSON_FILE):
        return []
    with open(JSON_FILE, 'r') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            # print error message if needed
            return []


def save_managers(managers):
    with open(JSON_FILE, 'w') as file:
        json.dump(managers, file, indent=4)


def get_manager_by_id(manager_id):
    managers = load_managers()
    for manager in managers:
        if manager['id'] == manager_id:
            return manager
    return None


def add_manager(manager):
    managers = load_managers()
    managers.append(manager.to_dict())
    save_managers(managers)


def update_manager(manager_id, updated_manager):
    managers = load_managers()
    for i, manager in enumerate(managers):
        if manager['manager_id'] == manager_id:
            managers[i] = updated_manager.to_dict()
            save_managers(managers)
            return True
    return False


def delete_manager(manager_id):
    managers = load_managers()
    for i, manager in enumerate(managers):
        if manager['manager_id'] == manager_id:
            del managers[i]
            save_managers(managers)
            return True
    return False
