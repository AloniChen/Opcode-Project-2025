import json
from typing import Optional, Tuple, List
from pathlib import Path


class Address:
    def __init__(self,street:str,house_number: int,city:str,postal_code:str,country:str,message:Optional[str]=None,apartment:Optional[int]=None,floor: Optional[int]=None,coordinates:Optional[Tuple[float,float]]=None)->None:
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
        """
        self.street=street
        self.house_number=house_number
        self.city=city
        self.postal_code=postal_code
        self.country=country
        self.apartment=apartment
        self.floor=floor
        self.coordinates=coordinates
        self.message=message
        
        
    def __str__(self) -> str:
        """Return a string representation of the Address object.

            Returns:
                str:  A comma-separated string containing the formatted address details.
                Format: "Street: [street], House number: [number], [Apt: apartment], [Floor: floor], City: [city], Postal: [postal_code], [country], [Location: coordinates], [Message: message]"
                (Optional fields in brackets are only included when present)
            
        """
        #todo - correct the documentation
        parts: list[str] = [f"Street: {self.street}, House number:{self.house_number}"]
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
    
   
    def to_dict(self)-> dict:
        """Converts the Address object to a dictionary representation.

        Returns:
            dict: A dictionary containing all relevant address fields and their values. the chosen fields are: "street", "house_number", "city",
            "postal_code", "country", "apartment", "floor", "coordinates", "message"
        """
        fields = ["street", "house_number", "city", "postal_code", "country", "apartment", "floor", "coordinates", "message"]
        return {field: getattr(self,field) for field in fields}
   
    #מקבלת את הפנקציה FROM DICT ומחזירה אובייקט מיוחד -
    #staticmethod ששומר את הפונקציה המקורית בפנים
    # זה גורם לפייתון להבין שמדובר במתודה סטטית כי - אין לה גישה לסלף (האובייקט) ואין לה  גישה ל
    #clf - המחלקה
    @staticmethod
    def from_dict(data:dict)->"Address":
        return Address(
            street=data["street"],
            house_number=data["house_number"],
            city=data["city"],
            postal_code=data["postal_code"],
            country=data["country"],
            #משתמשים ב GET 
            # כי כשמשהו יכול להיות None
            # אז עלול להיות KEYERR 
            #אם משתמשים בסוגריים המרובעות הרגילות
            apartment=data.get("apartment"),
            floor=data.get("floor"),
            coordinates=tuple(data["coordinates"])if data.get("coordinates") else None,
            message=data.get("message") 
            
        )
        
        
