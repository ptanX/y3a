from abc import ABC, abstractmethod
from pathlib import Path

from src.ocr.ocr_model import EXTENSION_SPLITTER, FILE_NAME_COMPONENT_SPLITTER, DocumentIdentifierMetadata


class IdentifierRetriever(ABC):

    @abstractmethod
    def retrieve(self, path: str) -> DocumentIdentifierMetadata:
        pass


class NameBasedIdentifierRetriever(IdentifierRetriever):

    def retrieve(self, path: str) -> DocumentIdentifierMetadata:
        python_path = Path(path)
        name_components = python_path.name.split(EXTENSION_SPLITTER)[0].split(FILE_NAME_COMPONENT_SPLITTER)
        company = name_components[0]
        category = name_components[1]
        file_type = name_components[2]
        time = None
        if len(name_components) >= 4:
            time = name_components[3]
        note = None
        if len(name_components) >= 5:
            note = time = name_components[4]
        return DocumentIdentifierMetadata(
            company=company,
            category=category,
            file_type=file_type,
            time=time,
            note=note
        )
