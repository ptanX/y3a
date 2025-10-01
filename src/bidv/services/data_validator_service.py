from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class InconsistentField:
    key_name: str
    contained_documents: List[str]
    values: Dict[str, Any]


class DataValidatorService:
    """
    Service class to find inconsistent fields across nested JSON structures
    and unify data into a standard schema.
    """

    def __init__(self):
        self.key_value_map: Dict[str, Dict[str, Any]] = {}

    def validate_and_unify(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate consistency and unify data into standard schema.

        Args:
            data: The nested dictionary to validate and unify

        Returns:
            Dictionary with 'inconsistent_fields' and 'unified_data'
        """
        inconsistent_fields = self.get_inconsistent_fields(data)
        unified_data = self.unify_to_schema(data)

        return {
            "inconsistent_fields": inconsistent_fields,
            "unified_data": unified_data
        }

    def get_inconsistent_fields(self, data: Dict[str, Any]) -> List[InconsistentField]:
        """
        Find all fields that have inconsistent values across the data structure.

        Args:
            data: The nested dictionary to validate

        Returns:
            List of InconsistentField objects containing inconsistent fields only
        """
        # Reset state
        self.key_value_map = {}

        # Collect all key-value pairs with their document paths
        self._collect_key_values(data)

        # Find inconsistent fields
        inconsistent_fields = []

        for key, path_value_map in self.key_value_map.items():
            if len(path_value_map) > 1:  # Key appears in multiple places
                values = list(path_value_map.values())
                unique_values = list(set(values))

                if len(unique_values) > 1:  # Values are different - inconsistent
                    # Extract document names from paths
                    contained_documents = list(set(path.split('.')[0] for path in path_value_map.keys()))

                    inconsistent_field = InconsistentField(
                        key_name=key,
                        contained_documents=contained_documents,
                        values=path_value_map
                    )
                    inconsistent_fields.append(inconsistent_field)

        return inconsistent_fields

    def _collect_key_values(self, data: Any, current_path: str = "") -> None:
        """
        Recursively collect all key-value pairs and their JSON paths.
        """
        if isinstance(data, dict):
            for key, value in data.items():
                full_path = f"{current_path}.{key}" if current_path else key

                # If the value is not a nested dict/list, record it
                if not isinstance(value, (dict, list)):
                    if key not in self.key_value_map:
                        self.key_value_map[key] = {}
                    self.key_value_map[key][full_path] = value

                # Continue recursion
                self._collect_key_values(value, full_path)

        elif isinstance(data, list):
            for index, item in enumerate(data):
                indexed_path = f"{current_path}[{index}]"

    def unify_to_schema(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Unify the data into the standard schema format.

        Args:
            data: The original nested data structure

        Returns:
            Unified data in the target schema format
        """
        # Initialize the target schema
        unified_schema = {
            "business_info": {
                "company_name_vn": "",
                "company_name_en": "",
                "company_abbr": "",
                "office_address": "",
                "phone": "",
                "email": "",
                "charter_capital": "",
                "par_value": "",
                "total_shares": ""
            },
            "legal_rep_info": {
                "legal_rep": "",
                "full_name": "",
                "gender": "",
                "position": "",
                "birth_date": "",
                "ethnicity": "",
                "nationality": "",
                "id_type": "",
                "id_number": "",
                "issue_date": "",
                "issue_place": "",
                "expiry_date": "",
                "permanent_address": "",
                "contact_address": ""
            }
        }

        # Collect all values from the data
        self.key_value_map = {}
        self._collect_key_values(data)

        # Fill the unified schema
        for key, path_value_map in self.key_value_map.items():
            # Get the best value (no mapping logic needed)
            value = self._get_best_value(path_value_map)

            # Place the value in the correct section of unified schema
            if key in unified_schema["business_info"]:
                unified_schema["business_info"][key] = value
            elif key in unified_schema["legal_rep_info"]:
                unified_schema["legal_rep_info"][key] = value

        return unified_schema

    def _get_best_value(self, path_value_map: Dict[str, Any]) -> Any:
        """
        Get the best value from multiple occurrences.
        Priority: non-empty values first, then first occurrence.
        """
        # Filter out empty/null values
        non_empty_values = {path: value for path, value in path_value_map.items()
                            if value and str(value).strip()}

        if non_empty_values:
            # Return first non-empty value
            return list(non_empty_values.values())[0]
        else:
            # Return first value even if empty
            return list(path_value_map.values())[0] if path_value_map else ""
