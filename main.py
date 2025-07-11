from dispatch_system import DispatchSystem
from pathlib import Path

dispatch = DispatchSystem(Path("addresses.json"))

# Add a new address
address_id = dispatch.add_address({
    "street": "Herzl",
    "house_number": 10,
    "city": "Tel Aviv",
    "postal_code": "12345",
    "country": "Israel"
})

# Show it
print(dispatch.get_address_by_id(address_id))
