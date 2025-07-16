import json
import logging
from pathlib import Path
from typing import Optional, List
from manager import Manager  # You must have a Manager class in manager.py

_logger = logging.getLogger(__name__)


class ManagerDispatchSystem:

    def __init__(self, managers_file: Path):
        self.managers_file = managers_file
        if not self.managers_file.exists():
            self._save_all([])  # Create file if missing

    def _load_all(self) -> List[dict]:
        try:
            with open(self.managers_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            _logger.warning("Managers file not found.")
            return []

    def _save_all(self, managers: List[dict]) -> None:
        with open(self.managers_file, "w") as file:
            json.dump(managers, file, indent=4)

    def add_manager(self, manager: Manager) -> bool:
    
        managers = self._load_all()
        if any(m["manager_id"] == manager.manager_id for m in managers):
            _logger.warning(f"Manager ID {manager.manager_id} already exists.")
            return False

        managers.append(manager.to_dict())
        self._save_all(managers)
        _logger.info(f"Manager {manager.name} added successfully.")
        return True

    def get_manager_by_id(self, manager_id: str) -> Optional[Manager]:
        managers = self._load_all()
        for m in managers:
            if m["manager_id"] == manager_id:
                return Manager.from_dict(m)
        _logger.info(f"Manager ID {manager_id} not found.")
        return None

    def list_all_managers(self) -> List[Manager]:
        return [Manager.from_dict(m) for m in self._load_all()]
