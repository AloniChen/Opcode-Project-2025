import json
from address import Address
from pathlib import Path
from typing import List, Optional
import itertools


class AddressRepository:
    def __init__(self, path: Path):
        """
        Initialize the repository with a file path.
        Loads existing addresses from the file and updates the ID counter.
        """
        self.path = path
        self.addresses: List[Address] = self._load_from_file()
        self._update_id_counter()

    def _load_from_file(self) -> List[Address]:
        if not self.path.exists() or self.path.stat().st_size == 0:
            return []
        with self.path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return [Address.from_dict(d) for d in data]

    def _update_id_counter(self):
        if self.addresses:
            max_id = max(a.id for a in self.addresses)
            Address._id_counter = itertools.count(max_id + 1)
        else:
            Address._id_counter = itertools.count(1)

    def save(self) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump([a.to_dict() for a in self.addresses],
                      f, ensure_ascii=False, indent=4)

    def add(self, address: Address) -> None:
        self.addresses.append(address)
        self.save()  # 🔥 auto-save

    def get_by_id(self, address_id: int) -> Optional[Address]:
        return next((a for a in self.addresses if a.id == address_id), None)

    def update_by_id(self, address_id: int, new_data: dict) -> bool:
        for a in self.addresses:
            if a.id == address_id:
                for key, value in new_data.items():
                    if hasattr(a, key):
                        setattr(a, key, value)
                self.save()  # 🔥 auto-save
                return True
        return False

    def delete_by_id(self, address_id: int) -> bool:
        before = len(self.addresses)
        self.addresses = [a for a in self.addresses if a.id != address_id]
        if len(self.addresses) < before:
            self.save()  # 🔥 auto-save
            return True
        return False

    def get_all(self) -> List[Address]:
        return self.addresses


if __name__ == '__main__':
    repo = AddressRepository(Path("addresses.json"))

    a1 = Address("Even Gvirol", 33, "Tel Aviv",
                 "11111", "Israel", message="buzz 2")
    repo.add(a1)

    found = repo.get_by_id(a1.id)
    if found:
        print("Found:", found)

    repo.update_by_id(a1.id, {"city": "Jerusalem"})

    repo.delete_by_id(a1.id)
