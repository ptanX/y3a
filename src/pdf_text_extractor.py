from typing import Dict, Any, List, Optional
from collections import defaultdict
import json
from google.cloud import documentai
from google.api_core.client_options import ClientOptions
from google.cloud.documentai_v1 import Document


class DocumentAIExtractor:
    """
    Extracts and normalizes text from PDFs using Google Cloud Document AI.

    Features:
    - Multi-language support
    - Various document types
    - Intelligent field merging with preference for cleaner values
    """

    def __init__(
            self,
            project_id: str,
            location: str,
            processor_id: str,
            processor_version: Optional[str] = None
    ):
        """
        Initialize Document AI client.

        Args:
            project_id: GCP project ID
            location: Processor location (e.g., 'us', 'eu')
            processor_id: Document AI processor ID
            processor_version: Optional specific processor version
        """
        self.project_id = project_id
        self.location = location
        self.processor_id = processor_id
        self.processor_version = processor_version

        self._client = self._initialize_client()
        self._resource_name = self._build_resource_name()

    def _initialize_client(self) -> documentai.DocumentProcessorServiceClient:
        """Create and configure Document AI client."""
        api_endpoint = f"{self.location}-documentai.googleapis.com"
        options = ClientOptions(api_endpoint=api_endpoint)
        return documentai.DocumentProcessorServiceClient(client_options=options)

    def _build_resource_name(self) -> str:
        """Build the full resource name for the processor."""
        if self.processor_version:
            return self._client.processor_version_path(
                self.project_id,
                self.location,
                self.processor_id,
                self.processor_version
            )
        return self._client.processor_path(
            self.project_id,
            self.location,
            self.processor_id
        )

    def extract_raw_document(
            self,
            file_path: str,
            mime_type: str = "application/pdf",
            field_mask: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process document and return raw Document AI response.

        Args:
            file_path: Path to the document file
            mime_type: MIME type of the document
            field_mask: Optional field mask to limit response fields

        Returns:
            Raw Document AI response as dictionary
        """
        with open(file_path, "rb") as file:
            content = file.read()

        raw_document = documentai.RawDocument(content=content, mime_type=mime_type)
        process_options = documentai.ProcessOptions()

        request = documentai.ProcessRequest(
            name=self._resource_name,
            raw_document=raw_document,
            field_mask=field_mask,
            process_options=process_options,
        )

        result = self._client.process_document(request=request)
        document_json = Document.to_json(result.document)

        return json.loads(document_json)

    def extract_normalized_text(self, file_path: str) -> Dict[str, Any]:
        """
        Extract and normalize document text with intelligent field merging.

        Args:
            file_path: Path to the document file

        Returns:
            Normalized document structure with merged fields
        """
        raw_document = self.extract_raw_document(file_path, field_mask="entities")
        structured_data = self._structure_entities(raw_document)
        normalized_data = self._normalize_fields(structured_data)
        return normalized_data

    def _structure_entities(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Document AI entity format to structured JSON.

        Groups entities by type and organizes properties as key-value pairs.
        Handles nested properties and multiple occurrences.

        Args:
            document_data: Raw Document AI response

        Returns:
            Structured data with entities organized by type
        """
        result = {}
        entities = document_data.get('entities', [])

        for entity in entities:
            entity_type = self._get_entity_type(entity)
            if not entity_type:
                continue

            entity_properties = self._extract_entity_properties(entity)
            result = self._add_entity_to_result(result, entity_type, entity_properties)

        return result

    @staticmethod
    def _get_entity_type(entity: Dict[str, Any]) -> Optional[str]:
        """Extract entity type from entity object."""
        return entity.get('type') or entity.get('type_')

    def _extract_entity_properties(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and organize properties from an entity.

        Args:
            entity: Entity object from Document AI

        Returns:
            Dictionary of property types to values
        """
        properties = entity.get('properties', [])
        property_groups = defaultdict(list)

        for prop in properties:
            prop_type = self._get_entity_type(prop)
            mention_text = self._get_mention_text(prop)

            if not (prop_type and mention_text is not None):
                continue

            mention_text = self._clean_text(mention_text)
            nested_properties = prop.get('properties', [])

            if nested_properties:
                nested_data = self._extract_nested_properties(nested_properties)
                property_groups[prop_type].append(nested_data)
            else:
                property_groups[prop_type].append(mention_text)

        return self._flatten_single_values(property_groups)

    @staticmethod
    def _get_mention_text(property_obj: Dict[str, Any]) -> Optional[str]:
        """Extract mention text from property object."""
        return property_obj.get('mentionText') or property_obj.get('mention_text')

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean text by removing newlines and extra whitespace."""
        return text.replace("\n", " ").rstrip(".;")

    def _extract_nested_properties(
            self,
            nested_props: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Extract nested properties recursively.

        Args:
            nested_props: List of nested property objects

        Returns:
            Dictionary of nested property types to values
        """
        nested_data = defaultdict(list)

        for nested_prop in nested_props:
            nested_type = self._get_entity_type(nested_prop)
            nested_text = self._get_mention_text(nested_prop)

            if nested_type and nested_text is not None:
                nested_data[nested_type].append(nested_text)

        return self._flatten_single_values(nested_data)

    def _flatten_single_values(
            self,
            data: Dict[str, List[Any]]
    ) -> Dict[str, Any]:
        """
        Convert single-item lists to single values.

        Args:
            data: Dictionary with list values

        Returns:
            Dictionary with single values flattened
        """
        return {
            key: values[0] if len(values) == 1 else values
            for key, values in data.items()
        }

    def _add_entity_to_result(
            self,
            result: Dict[str, Any],
            entity_type: str,
            entity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add entity data to result, handling duplicates by creating lists.

        Args:
            result: Current result dictionary
            entity_type: Type of entity to add
            entity_data: Entity property data

        Returns:
            Updated result dictionary
        """
        if entity_type in result:
            # Convert to list if not already
            if not isinstance(result[entity_type], list):
                result[entity_type] = [result[entity_type]]
            result[entity_type].append(entity_data)
        else:
            result[entity_type] = entity_data

        return result

    def _normalize_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize fields by merging duplicate entries intelligently.

        Converts arrays of similar objects into single objects,
        preferring cleaner, more complete values.

        Args:
            data: Structured entity data

        Returns:
            Normalized data with merged fields
        """
        normalized = {}

        for key, value in data.items():
            if isinstance(value, list) and self._is_mergeable_list(value):
                normalized[key] = self._merge_field_values(value)
            else:
                normalized[key] = value

        return normalized

    def _is_mergeable_list(self, value: List[Any]) -> bool:
        """Check if list contains dictionaries that can be merged."""
        return all(isinstance(item, dict) for item in value)

    def _merge_field_values(self, field_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge list of dictionaries into single dictionary.

        For each key, selects the best value based on:
        1. Lists preferred over strings
        2. Single statements over multi-statements
        3. Longer values over shorter ones

        Args:
            field_list: List of dictionaries with overlapping keys

        Returns:
            Merged dictionary with best values
        """
        merged = {}

        for item in field_list:
            for key, value in item.items():
                if key not in merged:
                    merged[key] = value
                elif self._should_replace_value(merged[key], value):
                    merged[key] = value

        return merged

    def _should_replace_value(self, current_value: Any, new_value: Any) -> bool:
        """
        Determine if new value should replace current value.

        Priority rules:
        1. Lists preferred over strings (more information)
        2. Single statements preferred over multi-statements (cleaner)
        3. Longer values preferred (more complete)

        Args:
            current_value: Current field value
            new_value: Candidate replacement value

        Returns:
            True if new_value should replace current_value
        """
        # Prefer lists to strings
        if isinstance(current_value, str) and isinstance(new_value, list):
            return True

        if isinstance(current_value, list) and isinstance(new_value, str):
            return False

        # If both lists, prefer longer
        if isinstance(current_value, list) and isinstance(new_value, list):
            return len(new_value) > len(current_value)

        # For strings, check statement quality
        current_is_single = self._is_single_statement(current_value)
        new_is_single = self._is_single_statement(new_value)

        # Prefer single statements
        if new_is_single and not current_is_single:
            return True

        if current_is_single and not new_is_single:
            return False

        if current_value[0].isupper() and not new_value[0].isupper():
            return False
        if new_value[0].isupper() and not current_value[0].isupper():
            return True

        # Both same type, prefer longer
        return len(str(new_value)) > len(str(current_value))

    @staticmethod
    def _is_single_statement(text: Any) -> bool:
        has_separator_in_middle = '.' in str(text) or ';' in str(text)
        return not has_separator_in_middle


if __name__ == "__main__":
    PROJECT_ID = "387819483924"
    LOCATION = "us"
    business_registration_processor_id = "5110722c3ac24f03"
    company_character_processor_id = "12676ebbd1c0ed5"
    hoso1_file_path = "/Users/anhdv7/Desktop/practice/y3a/documentations/ho-so-dnse-1.pdf"
    hoso2_file_path = "/Users/anhdv7/Desktop/practice/y3a/documentations/ho-so-dnse-2.pdf"
    field_mask = "entities"  # The fields to return in the Document object.

    extractor1 = DocumentAIExtractor(project_id=PROJECT_ID,
                                     location=LOCATION,
                                     processor_id=business_registration_processor_id,
                                     )
    document1 = extractor1.extract_normalized_text(file_path=hoso1_file_path)

    extractor2 = DocumentAIExtractor(project_id=PROJECT_ID,
                                     location=LOCATION,
                                     processor_id=company_character_processor_id,
                                     )
    document2 = extractor2.extract_normalized_text(file_path=hoso2_file_path)

    result = {"business_registration_cert": document1, "company_charter": document2}

    with open("final_result.json", 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
