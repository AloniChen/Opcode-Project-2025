import json
from typing import Optional, Tuple, List
from pathlib import Path
import itertools
import requests


class Address:
    _id_counter = itertools.count(1)

    def __init__(self,
                 street: str,
                 house_number: int,
                 city: str,
                 postal_code: str,
                 country: str,
                 message: Optional[str] = None,
                 apartment: Optional[int] = None,
                 floor: Optional[int] = None,
                 coordinates: Optional[Tuple[float, float]] = None,
                 id: Optional[int] = None

                 ) -> None:
        """Initialize an Address Object.

        Args:
            street (str): The street name
            house_number (int): The house number
            city (str): The city name
            postal_code (str): The postal code
            country (str): The Country name
            apartment (Optional[int], optional): The apartment number. Defaults to None.
            floor (Optional[int], optional): The floor number. Defaults to None.
            coordinates (Optional[Tuple[float,float]]): GPS coordinates as (latitude, longitude). Defaults to None.
            message (Optional [str]): Customer's message. Defaults to None.
            id (Optional[int]): Unique ID of the address. If None, a new ID is generated automatically.

        """
        self.id = id if id is not None else next(Address._id_counter)
        self.street = street
        self.house_number = house_number
        self.city = city
        self.postal_code = postal_code
        self.country = country
        self.apartment = apartment
        self.floor = floor
        self.coordinates = coordinates
        self.message = message

        if self.coordinates is None:
            self.fetch_coordinates()

    def fetch_coordinates(self) -> None:
        """
        Use OpenStreetMap Nominatim API to fetch GPS coordinates for the address.
        Sets self.coordinates to (latitude, longitude).
        """
        query = f"{self.house_number} {self.street}, {self.city}, {self.postal_code}, {self.country}"
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": query,
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "DeliverySim/1.0 (tmunot1234567@gmail.com)"
        }

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                self.coordinates = (lat, lon)
                print(f"[Geocoding] Coordinates found: {self.coordinates}")
            else:
                print("[Geocoding] No coordinates found for the given address.")
        except requests.RequestException as e:
            print(f"[Geocoding] Error: {e}")

    def __str__(self) -> str:
        """Return a string representation of the Address object.

        Returns:
            str: A comma-separated string showing all address details including the unique ID.
        """
        parts: list[str] = [
            f"ID: {self.id}", f"Street: {self.street}, House number:{self.house_number}"]
        if self.apartment:
            parts.append(f"Apt: {self.apartment}")
        if self.floor:
            parts.append(f"Floor: {self.floor}")
        parts.append(f"City: {self.city}, Postal: {self.postal_code}")
        parts.append(self.country)
        if self.coordinates:
            parts.append(f"Location: {self.coordinates}")
        if self.message:
            parts.append(f"Message: {self.message}")
        return ", ".join(parts)

    def to_dict(self) -> dict:
        """Convert the Address object to a dictionary.

        Returns:
            dict: A dictionary with keys:
                'id', 'street', 'house_number', 'city', 'postal_code',
                'country', 'apartment', 'floor', 'coordinates', 'message'
        """
        fields = ["id", "street", "house_number", "city", "postal_code",
                  "country", "apartment", "floor", "coordinates", "message"]
        return {field: getattr(self, field) for field in fields}

    # מקבלת את הפנקציה FROM DICT ומחזירה אובייקט מיוחד -
    # staticmethod ששומר את הפונקציה המקורית בפנים
    # זה גורם לפייתון להבין שמדובר במתודה סטטית כי - אין לה גישה לסלף (האובייקט) ואין לה  גישה ל
    # clf - המחלקה
    @staticmethod
    def from_dict(data: dict) -> "Address":
        """Create an Address object from a dictionary.

        Args:
            data (dict): Dictionary containing address data.

        Returns:
            Address: A new Address instance populated with the dictionary values.
        """
        return Address(
            id=data["id"],
            street=data["street"],
            house_number=data["house_number"],
            city=data["city"],
            postal_code=data["postal_code"],
            country=data["country"],
            # משתמשים ב GET
            # כי כשמשהו יכול להיות None
            # אז עלול להיות KEYERR
            # אם משתמשים בסוגריים המרובעות הרגילות
            apartment=data.get("apartment"),
            floor=data.get("floor"),
            coordinates=tuple(data["coordinates"])if data.get(
                "coordinates") else None,
            message=data.get("message")

        )


if __name__ == '__main__':
    # Example of using the address
    addr1 = Address("Herzl", 10, "Tel Aviv", "12345", "Israel")
    addr2 = Address("Ben Yehuda", 5, "Haifa", "54321", "Israel")
    addr3 = Address("Ben Yehuda1", 5, "Haifa", "54321", "Israel")
