from sqlalchemy import Column, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Modern SQLAlchemy 2.0+ declarative base class"""

    pass


class CustomerProfile(Base):
    """Customer Profile table with exact schema - all STRING columns"""

    __tablename__ = "customer_profile"

    # Primary key (using customer_id as primary key)
    customer_id = Column(String(50), primary_key=True, nullable=False)

    # Company names
    ten_cong_ty_tieng_viet = Column(String(500))  # Vietnamese company name
    ten_cong_ty_tieng_nuoc_ngoai = Column(String(500))  # Foreign language company name
    ten_viet_tat = Column(String(100))  # Company abbreviation

    # Business registration info
    ma_so_doanh_nghiep = Column(String(50))  # Business registration number
    dang_ky_lan_dau = Column(String(20))  # First registration date
    lan_dang_ky_thay_doi = Column(String(10))  # Number of modifications
    dang_ky_thay_doi = Column(String(20))  # Last modification date
    so_dang_ky_kinh_doanh = Column(String(50))  # Business license number

    # Contact information
    dia_chi_tru_so = Column(String(1000))  # Head office address
    so_dien_thoai = Column(String(50))  # Phone number
    email = Column(String(200))  # Email address

    # Financial information
    von_dieu_le = Column(String(50))  # Charter capital
    menh_gia_co_phan = Column(String(50))  # Share par value
    tong_so_co_phan = Column(String(50))  # Total shares
    don_vi = Column(String(20))  # Unit

    # Business sector information
    ten_nganh = Column(String(500))  # Sector name
    nganh_nghe_kinh_doanh_chinh = Column(String(1000))  # Main business activity
    ma_nganh = Column(String(50))  # Sector code

    def __repr__(self):
        return f"<CustomerProfile(customer_id='{self.customer_id}', company='{self.ten_viet_tat}')>"


class LegalRepresentative(Base):
    """Legal Representative table with exact schema - all STRING columns"""

    __tablename__ = "legal_representative"

    # Primary key
    rep_id = Column(String(50), primary_key=True, nullable=False)

    # Foreign key to customer
    customer_id = Column(String(50), nullable=False)  # Foreign key as string

    # Personal information
    ho_ten = Column(String(200))  # Full name
    gioi_tinh = Column(String(10))  # Gender
    ngay_sinh = Column(String(20))  # Date of birth
    quoc_tich = Column(String(100))  # Nationality
    dan_toc = Column(String(50))  # Ethnicity

    # ID document information
    loai_giay_to = Column(String(100))  # ID document type
    so_giay_to = Column(String(50))  # ID document number
    ngay_cap = Column(String(20))  # Issue date
    ngay_het_han = Column(String(20))  # Expiry date
    noi_cap = Column(String(500))  # Issuing authority

    # Address information
    dia_chi_thuong_tru = Column(String(1000))  # Permanent address
    dia_chi_lien_lac = Column(String(1000))  # Contact address

    # Position
    chuc_danh = Column(String(200))  # Position/Title

    def __repr__(self):
        return f"<LegalRepresentative(rep_id='{self.rep_id}', name='{self.ho_ten}')>"


class DocumentationInformation(Base):
    """Documentation Information table with exact schema - all STRING columns"""

    __tablename__ = "documentation_information"

    # Primary key
    id = Column(String(50), primary_key=True, nullable=False)
    data = Column(Text, nullable=False)
