from typing import Dict, Any, Optional
import json
from google.cloud import documentai
from google.api_core.client_options import ClientOptions
from google.cloud.documentai_v1 import Document


class DocumentAIExtractor:
    """
    Extracts and normalizes text from PDFs using Google Cloud Document AI.
    """

    def __init__(
            self,
            project_id: str,
            location: str,
            processor_id: str,
            processor_version: Optional[str] = None,
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
                self.processor_version,
            )
        return self._client.processor_path(
            self.project_id, self.location, self.processor_id
        )

    def extract_raw_document(
            self,
            file_content: bytes,
            mime_type: str = "application/pdf",
            field_mask: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process document and return raw Document AI response.

        Args:
            file_content: Document file content as bytes
            mime_type: MIME type of the document
            field_mask: Optional field mask to limit response fields

        Returns:
            Raw Document AI response as dictionary
        """
        raw_document = documentai.RawDocument(content=file_content, mime_type=mime_type)
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

    def extract_normalized_text(self, file_content: bytes) -> Dict[str, Any]:
        """
        Extract entities from document and structure by type.

        Args:
            file_content: Document file content as bytes

        Returns:
            Dictionary with entity types as keys and properties as values
        """
        raw_document = self.extract_raw_document(file_content, field_mask="entities")
        return self._structure_entities(raw_document)

    @staticmethod
    def _get_mention_text(property_obj: Dict[str, Any]) -> Optional[str]:
        """Extract mention text from property object."""
        return property_obj.get("mentionText") or property_obj.get("mention_text")

    def _structure_entities(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Document AI entity format to structured JSON.

        Args:
            document_data: Raw Document AI response with entities array

        Returns:
            Dictionary with entity types as keys and properties as values
        """
        result = {}
        entities = document_data.get("entities", [])

        for entity in entities:
            entity_type = entity.get("type")
            if not entity_type:
                continue

            text = self._get_mention_text(entity)
            result[entity_type] = text

        return result
