import json
import os
from dataclasses import dataclass
from typing import Dict, List, Any, Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.bidv.db.bidv_entity import CustomerProfile, LegalRepresentative


@dataclass
class OriginDoc:
    name: str
    value: Any


@dataclass
class ValidationResult:
    is_consistent_across_doc: bool
    is_match_database: bool


@dataclass
class FieldValidationResult:
    field_name: str
    origin_docs: List[OriginDoc]
    database_value: Optional[Any]
    validation_result: ValidationResult


@dataclass
class InconsistentField:
    key_name: str
    contained_documents: List[str]
    values: Dict[str, Any]


class DataValidatorService:
    """
    Enhanced service to validate data consistency across documents and database records using ORM.
    """

    def __init__(self, session_factory=None):
        self.key_value_map: Dict[str, Dict[str, Any]] = {}
        self.Session = session_factory

    def validate_with_database(self, data: Dict[str, Any]) -> List[FieldValidationResult]:
        """
        Validate data consistency across documents and database records.
        Extracts business_code and id_number from unified data.

        Args:
            data: The nested dictionary to validate

        Returns:
            List of FieldValidationResult objects
        """
        if not self.Session:
            raise ValueError("Database connection not configured")

        # Get unified data and document consistency info
        unified_data = self.unify_to_schema(data)

        # Extract business_code and id_number from unified data
        business_code = unified_data.get('business_info', {}).get('business_code')
        id_number = unified_data.get('legal_rep_info', {}).get('id_number')

        if not business_code:
            raise ValueError("business_code not found in unified data")
        if not id_number:
            print("id_number not found in unified data")

        doc_consistency = self._get_document_consistency(data)

        # Get database records
        customer_record = self._get_customer_profile(business_code)
        legal_rep_record = self._get_legal_representative(business_code, id_number)

        # Create field mapping between unified schema and database fields
        field_mappings = self._create_field_mappings()

        validation_results = []

        # Validate business_info fields
        for unified_field, db_info in field_mappings['business_info'].items():
            if unified_field in unified_data['business_info']:
                result = self._validate_field(
                    field_name=unified_field,
                    unified_value=unified_data['business_info'][unified_field],
                    db_record=customer_record,
                    db_field=db_info['db_field'],
                    doc_consistency=doc_consistency,
                    data=data
                )
                validation_results.append(result)

        # Validate legal_rep_info fields
        for unified_field, db_info in field_mappings['legal_rep_info'].items():
            if unified_field in unified_data['legal_rep_info']:
                result = self._validate_field(
                    field_name=unified_field,
                    unified_value=unified_data['legal_rep_info'][unified_field],
                    db_record=legal_rep_record,
                    db_field=db_info['db_field'],
                    doc_consistency=doc_consistency,
                    data=data
                )
                validation_results.append(result)

        return validation_results

    def _create_field_mappings(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """Create mappings between unified schema fields and database fields."""
        return {
            'business_info': {
                'company_name_vn': {'db_field': 'ten_cong_ty_tieng_viet'},
                'company_name_en': {'db_field': 'ten_cong_ty_tieng_nuoc_ngoai'},
                'company_abbr': {'db_field': 'ten_viet_tat'},
                'office_address': {'db_field': 'dia_chi_tru_so'},
                'phone': {'db_field': 'so_dien_thoai'},
                'email': {'db_field': 'email'},
                'charter_capital': {'db_field': 'von_dieu_le'},
                'par_value': {'db_field': 'menh_gia_co_phan'},
                'total_shares': {'db_field': 'tong_so_co_phan'},
                'business_code': {'db_field': 'ma_so_doanh_nghiep'}
            },
            'legal_rep_info': {
                'legal_rep': {'db_field': 'ho_ten'},
                'full_name': {'db_field': 'ho_ten'},
                'gender': {'db_field': 'gioi_tinh'},
                'position': {'db_field': 'chuc_danh'},
                'birth_date': {'db_field': 'ngay_sinh'},
                'ethnicity': {'db_field': 'dan_toc'},
                'nationality': {'db_field': 'quoc_tich'},
                'id_type': {'db_field': 'loai_giay_to'},
                'id_number': {'db_field': 'so_giay_to'},
                'issue_date': {'db_field': 'ngay_cap'},
                'issue_place': {'db_field': 'noi_cap'},
                'expiry_date': {'db_field': 'ngay_het_han'},
                'permanent_address': {'db_field': 'dia_chi_thuong_tru'},
                'contact_address': {'db_field': 'dia_chi_lien_lac'}
            }
        }

    def _get_customer_profile(self, business_code: str) -> Optional[CustomerProfile]:
        """Get customer profile from database using ORM."""
        session = self.Session()
        try:
            customer = session.query(CustomerProfile).filter(
                CustomerProfile.ma_so_doanh_nghiep == business_code
            ).first()
            return customer
        finally:
            session.close()

    def _get_legal_representative(self, business_code: str, id_number: str) -> Optional[
        LegalRepresentative]:
        """Get legal representative from database using ORM."""
        session = self.Session()
        try:
            legal_rep = session.query(LegalRepresentative).join(
                CustomerProfile, LegalRepresentative.customer_id == CustomerProfile.customer_id
            ).filter(
                CustomerProfile.ma_so_doanh_nghiep == business_code,
                LegalRepresentative.so_giay_to == id_number
            ).first()
            return legal_rep
        finally:
            session.close()

    def _validate_field(self, field_name: str, unified_value: Any, db_record: Optional[Any],
                        db_field: str, doc_consistency: Dict[str, Any], data: Dict[str, Any]) -> FieldValidationResult:
        """Validate a single field against document consistency and database value."""

        # Get origin documents info
        origin_docs = self._get_field_origin_docs(field_name, data)

        # Check document consistency
        is_consistent_across_doc = doc_consistency.get(field_name, {}).get('is_consistent', True)

        # Get database value using ORM
        database_value = None
        is_match_database = False

        if db_record:
            # Get value from ORM object using getattr
            database_value = getattr(db_record, db_field, None)
            # Compare values (handle different data types and formats)
            is_match_database = self._compare_values(unified_value, database_value)

        return FieldValidationResult(
            field_name=field_name,
            origin_docs=origin_docs,
            database_value=database_value,
            validation_result=ValidationResult(
                is_consistent_across_doc=is_consistent_across_doc,
                is_match_database=is_match_database
            )
        )

    def _get_field_origin_docs(self, field_name: str, data: Dict[str, Any]) -> List[OriginDoc]:
        """Get origin documents information for a field."""
        origin_docs = []

        # Collect values from original data structure
        self.key_value_map = {}
        self._collect_key_values(data)

        if field_name in self.key_value_map:
            for path, value in self.key_value_map[field_name].items():
                # Extract document name from path (first part before '.')
                doc_name = path.split('.')[0]
                origin_docs.append(OriginDoc(name=doc_name, value=value))

        return origin_docs

    def _get_document_consistency(self, data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Get document consistency information for all fields."""
        inconsistent_fields = self.get_inconsistent_fields(data)

        consistency_info = {}

        # Mark inconsistent fields
        for field in inconsistent_fields:
            consistency_info[field.key_name] = {
                'is_consistent': False,
                'values': field.values
            }

        # All other fields that appear in multiple docs are consistent
        self.key_value_map = {}
        self._collect_key_values(data)

        for key, path_value_map in self.key_value_map.items():
            if len(path_value_map) > 1 and key not in consistency_info:
                consistency_info[key] = {
                    'is_consistent': True,
                    'values': path_value_map
                }

        return consistency_info

    def _compare_values(self, value1: Any, value2: Any) -> bool:
        """Compare two values handling different formats and types."""
        if value1 is None and value2 is None:
            return True
        if value1 is None or value2 is None:
            return False

        # Convert both to strings and strip whitespace for comparison
        str1 = str(value1).strip().upper()
        str2 = str(value2).strip().upper()

        return str1 == str2

    # Include previous methods for basic functionality
    def get_inconsistent_fields(self, data: Dict[str, Any]) -> List[InconsistentField]:
        """Find all fields that have inconsistent values across the data structure."""
        self.key_value_map = {}
        self._collect_key_values(data)

        inconsistent_fields = []

        for key, path_value_map in self.key_value_map.items():
            if len(path_value_map) > 1:
                values = list(path_value_map.values())
                unique_values = list(set(values))

                if len(unique_values) > 1:
                    contained_documents = list(set(path.split('.')[0] for path in path_value_map.keys()))

                    inconsistent_field = InconsistentField(
                        key_name=key,
                        contained_documents=contained_documents,
                        values=path_value_map
                    )
                    inconsistent_fields.append(inconsistent_field)

        return inconsistent_fields

    def unify_to_schema(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Unify the data into the standard schema format."""
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
                "total_shares": "",
                "business_code": ""
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

        self.key_value_map = {}
        self._collect_key_values(data)

        for key, path_value_map in self.key_value_map.items():
            value = self._get_best_value(path_value_map)

            if key in unified_schema["business_info"]:
                unified_schema["business_info"][key] = value
            elif key in unified_schema["legal_rep_info"]:
                unified_schema["legal_rep_info"][key] = value

        return unified_schema

    def _get_best_value(self, path_value_map: Dict[str, Any]) -> Any:
        """Get the best value from multiple occurrences."""
        non_empty_values = {path: value for path, value in path_value_map.items()
                            if value and str(value).strip()}

        if non_empty_values:
            return list(non_empty_values.values())[0]
        else:
            return list(path_value_map.values())[0] if path_value_map else ""

    def _collect_key_values(self, data: Any, current_path: str = "") -> None:
        """Recursively collect all key-value pairs and their JSON paths."""
        if isinstance(data, dict):
            for key, value in data.items():
                full_path = f"{current_path}.{key}" if current_path else key

                if not isinstance(value, (dict, list)):
                    if key not in self.key_value_map:
                        self.key_value_map[key] = {}
                    self.key_value_map[key][full_path] = value

                self._collect_key_values(value, full_path)

        elif isinstance(data, list):
            for index, item in enumerate(data):
                indexed_path = f"{current_path}[{index}]"
                self._collect_key_values(item, indexed_path)


# Example usage
# if __name__ == "__main__":
#     # Sample data
#     sample_data = {
#         "business_registration_cert": {
#             "business_info": {
#                 "company_name_vn": "CÔNG TY CỔ PHẦN CHỨNG KHOÁN DNSE",
#                 "business_code": "0102459106",
#                 "company_name_en": "DNSE SECURITIES JOINT STOCK",
#                 "company_abbr": "DNSE JSC",
#                 "hq_address": "Tầng 6 tòa nhà Pax Sky, 63-65 Ngô Thì Nhậm, Phường Phạm Đình Hổ, Quận Hai Bà Trưng, Thành phố Hà Nội, Việt Nam",
#                 "phone": "024.7108.9234",
#                 "email": "info@dnse.com.vn",
#                 "charter_capital": "3300000000000",
#                 "par_value": "10000",
#                 "total_shares": "330000000"
#             },
#             "legal_rep_info": {
#                 "legal_rep": "PHẠM THỊ THANH HOA",
#                 "full_name": "PHẠM THỊ THANH HOA",
#                 "gender": "Nữ",
#                 "position": "Tổng giám đốc",
#                 "birth_date": "1985-11-17",
#                 "ethnicity": "Kinh",
#                 "nationality": "Việt Nam",
#                 "id_type": "Thẻ căn cước công dân",
#                 "id_number": "12345678901",
#                 "issue_date": "2014-11-19",
#                 "issue_place": "CỤC CẢNH SÁT DKQL CƯ TRÚ VÀ DLQG VỀ DÂN CƯ",
#                 "expiry_date": "2029-11-19",
#                 "permanent_address": "văn bản",
#                 "contact_address": "văn bản"
#             }
#         },
#         "company_charter": {
#             "business_info": {
#                 "company_name_vn": "CÔNG TY CỔ PHẦN CHỨNG KHOÁN DNSE",
#                 "company_name_en": "DNSE SECURITIES JOINT STOCK",
#                 "business_code": "0102459106",
#                 "company_abbr": "DNSE JSC",
#                 "office_address": "Tầng 6 tòa nhà Pax Sky, 63-65 Ngô Thì Nhậm, Phường Phạm Đình Hổ, Quận Hai Bà Trưng, Thành phố Hà Nội, Việt Nam",
#                 "phone": "024.7108.9234",
#                 "email": "info@dnse.com.vn",
#                 "charter_capital": "3300000000000",
#                 "par_value": "10000",
#                 "total_shares": "330000000"
#             },
#             "legal_rep_info": {
#                 "legal_rep": "PHẠM THỊ THANH HOA",
#                 "position": "Tổng giám đốc",
#                 "birth_date": "1985-11-17",
#                 "ethnicity": "Kinh",
#                 "nationality": "Việt Nam",
#                 "id_type": "Thẻ căn cước công dân",
#                 "id_number": "12345678901",
#                 "issue_date": "2014-11-19",
#                 "issue_place": "CỤC CẢNH SÁT DKQL CƯ TRÚ VÀ DLQG VỀ DÂN CƯ",
#                 "expiry_date": "2029-11-19",
#                 "permanent_address": "văn bản",
#                 "contact_address": "văn bản"
#             }
#         }
#     }
#
#     # Initialize with ORM session factory
#     load_dotenv()
#     DATABASE_PATH = os.environ['BIDV_DB_PATH']
#     engine = create_engine(f"sqlite:///{DATABASE_PATH}")
#     Session = sessionmaker(bind=engine)
#     validator = DataValidatorService(Session)
#
#     # For demo without database
#     # validator = DataValidatorService()
#
#     # Basic validation without database
#     # inconsistent_fields = validator.get_inconsistent_fields(sample_data)
#     # print(f"Found {len(inconsistent_fields)} inconsistent fields")
#
#     # With database (uncomment when you have DB connection)
#     results = validator.validate_with_database(sample_data)
#     #
#     print(results)
#     for result in results:
#         print(f"Field: {result.field_name}")
#         print(f"Origin docs: {[(doc.name, doc.value) for doc in result.origin_docs]}")
#         print(f"DB value: {result.database_value}")
#         print(f"Consistent across docs: {result.validation_result.is_consistent_across_doc}")
#         print(f"Matches database: {result.validation_result.is_match_database}")
#         print("---")