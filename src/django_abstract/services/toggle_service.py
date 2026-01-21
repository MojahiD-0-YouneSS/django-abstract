from django_abstract.utilities import (
    ClassInfoProvider,Entry
)
from dataclasses import dataclass
from datetime import datetime, date


class ToggleSystem(ClassInfoProvider):
    def __init__(self):
        self.entries:list[Entry] = []  # List of all entries
        self.deactivated_entries:list[Entry] = []  # List for deactivated entries
        self.system_infos = self.get_class_info()
        self.dependency = None

        super().__init__()
    def register_entry(self, entry):
        """Register a new entry to the system."""
        self.entries.append(entry)
        print(f"'{entry.name}' registered.")
    
    def order_entries_by_start_date(self):
        """Order entries by their start date."""
        self.entries.sort(key=lambda entry: entry.query_obj.start_date)
    
    def activate_entries(self):
        """Activate entries based on the current date."""
        today = datetime.today()
        for entry in self.entries[:]:  # Iterate over a copy of the list to avoid modification during iteration
            # Only activate entries that should be active today
            data_base_entry_obj = getattr(self._dependency, entry.selector_obj)
            data_base_entry = data_base_entry_obj.get(id=entry.query_obj.entry_id)
            if datetime.combine(entry.query_obj.start_date, datetime.min.time()) <= today <= datetime.combine(entry.query_obj.end_date, datetime.min.time()):
                if entry.query_obj.status == "deactivated":  # Only activate if not already active
                    entry.activate()
                    data_base_entry.is_active = True
                    data_base_entry.save()
            elif today > entry.query_obj.end_date and entry.query_obj.status != "disabled":
                if entry.query_obj.status == "activated":  # Deactivate if today's date is after the end date
                    entry.deactivate()
                    data_base_entry.is_active = False
                    data_base_entry.save()
                    # Move deactivated entry to the deactivated list
                    self.deactivated_entries.append(entry)
                    self.entries.remove(entry)  # Remove the deactivated entry from active list
        return self
    
    def disable_entry(self, entry_name):
        """Explicitly disable a entry by admin."""
        for entry in self.entries:
            data_base_entry_obj = getattr(self._dependency, entry.selector_obj)
            data_base_entry = data_base_entry_obj.get(id=entry.query_obj.entry_id)
            if entry.query_obj.name == entry_name:
                entry.disable()
                data_base_entry.is_disabled = True
                data_base_entry.save()
                # Move disabled entry to deactivated list
                self.deactivated_entries.append(entry)
                self.entries.remove(entry)
                print(f"'{entry_name}' disabled by admin.")
    
    def load_external_entries(self, new_entries:list[Entry], extend=False,):
        if extend:
            self.entries.extend([entry for entry in new_entries if entry.query_obj.status == "activated"])
        else:
            self.entries = [entry for entry in new_entries if entry.query_obj.status == "activated"]
    
    def clean_up_deactivated_entries(self):
        """Remove deactivated entries to free up memory."""
        self.deactivated_entries.clear()
        print("Deactivated entries cleared from memory.")
    
    def get_active_entries(self):
    
        """Get all currently active entries."""
        return [entry for entry in self.entries if entry.query_obj.status == "activated"]
    
    def get_deactivated_entries(self):
        """Get all currently deactivated entries."""
        return [entry.query_obj.name for entry in self.deactivated_entries if entry.query_obj.status == "deactivated"]
