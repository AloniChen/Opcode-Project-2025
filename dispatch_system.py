import json
import logging
from typing import List, Dict
from classes import Courier

_logger = logging.getLogger(__name__)


class DispatchSystem:
    """
    A class to manage the dispatch system, including couriers and their operations.
    """

    def add_courier(self, courier: Courier) -> bool:
        """
        Adds a new courier to the system.
        Returns True if successful, False if the courier already exists.
        """
        if Courier.courier_exists(courier.courier_id):
            _logger.error(
                f"Courier with ID {courier.courier_id} already exists")
            return False
        Courier.create_courier(courier)
        _logger.info(f"Courier {courier.name} added successfully.")
        return True
