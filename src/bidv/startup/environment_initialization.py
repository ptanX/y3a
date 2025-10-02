import csv
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.bidv.db.entity.bidv_entity import Base, CustomerProfile, LegalRepresentative

load_dotenv()
DATABASE_PATH = os.environ['BIDV_DB_PATH']
CUSTOMER_PROFILE_DATA = os.environ['CUSTOMER_PROFILE_DATA']
LEGAL_REPRESENTATIVE_DATA = os.environ['LEGAL_REPRESENTATIVE_DATA']
COLLATERAL_ASSETS_DATAA = os.environ['COLLATERAL_ASSETS_DATA']


def create_database_now():
    db_path = Path(DATABASE_PATH)
    conn = sqlite3.connect(str(db_path))
    conn.commit()
    conn.close()


def create_database_with_schema():
    """Create database with the exact customer profile schema"""

    # Setup database path
    db_path = DATABASE_PATH

    try:
        # Create SQLAlchemy engine
        engine = create_engine(f'sqlite:///{db_path}', echo=False)
        # Create all tables
        Base.metadata.create_all(engine)
        # Show created tables
        tables = list(Base.metadata.tables.keys())
        # Create session factory
        Session = sessionmaker()
        Session.configure(bind=engine)

        return db_path, engine, Session

    except Exception as e:
        print(f"❌ Error creating database: {e}")
        raise


def load_data_from_csv_files(Session, customer_csv_path=CUSTOMER_PROFILE_DATA,
                             legal_csv_path=LEGAL_REPRESENTATIVE_DATA):
    """Load data from CSV files into the database"""
    session = Session()

    try:
        # Load Customer Profile data
        if not os.path.exists(customer_csv_path):
            print(f"❌ File not found: {customer_csv_path}")
            return False

        customer_count = 0
        with open(customer_csv_path, 'r', encoding='utf-8-sig') as file:
            # Use csv.DictReader to handle CSV properly
            reader = csv.DictReader(file)

            for row in reader:
                # Clean up the row data (remove extra whitespace)
                cleaned_row = {k.strip(): (v.strip() if v else '') for k, v in row.items()}
                # print(cleaned_row)
                # Skip empty rows
                if not cleaned_row.get('customer_id'):
                    continue

                # Create CustomerProfile object
                customer = CustomerProfile(
                    customer_id=cleaned_row.get('customer_id', ''),
                    ten_cong_ty_tieng_viet=cleaned_row.get('ten_cong_ty_tieng_viet', ''),
                    ten_cong_ty_tieng_nuoc_ngoai=cleaned_row.get('ten_cong_ty_tieng_nuoc_ngoai', ''),
                    ten_viet_tat=cleaned_row.get('ten_viet_tat', ''),
                    ma_so_doanh_nghiep=cleaned_row.get('ma_so_doanh_nghiep', ''),
                    dang_ky_lan_dau=cleaned_row.get('dang_ky_lan_dau', ''),
                    lan_dang_ky_thay_doi=cleaned_row.get('lan_dang_ky_thay_doi', ''),
                    dang_ky_thay_doi=cleaned_row.get('dang_ky_thay_doi', ''),
                    so_dang_ky_kinh_doanh=cleaned_row.get('so_dang_ky_kinh_doanh', ''),
                    dia_chi_tru_so=cleaned_row.get('dia_chi_tru_so', ''),
                    so_dien_thoai=cleaned_row.get('so_dien_thoai', ''),
                    email=cleaned_row.get('email', ''),
                    von_dieu_le=cleaned_row.get('von_dieu_le', ''),
                    menh_gia_co_phan=cleaned_row.get('menh_gia_co_phan', ''),
                    tong_so_co_phan=cleaned_row.get('tong_so_co_phan', ''),
                    don_vi=cleaned_row.get('don_vi', ''),
                    ten_nganh=cleaned_row.get('ten_nganh', ''),
                    nganh_nghe_kinh_doanh_chinh=cleaned_row.get('nganh_nghe_kinh_doanh_chinh', ''),
                    ma_nganh=cleaned_row.get('ma_nganh', '')
                )

                session.add(customer)
                customer_count += 1

                # Commit in batches for better performance
                if customer_count % 50 == 0:
                    session.commit()
                    print(f"   Processed {customer_count} customers...")

        session.commit()
        print(f"   ✅ Loaded {customer_count} customer profiles")

        # Load Legal Representative data
        print(f"\n2️⃣  Loading Legal Representative data from: {legal_csv_path}")

        if not os.path.exists(legal_csv_path):
            print(f"❌ File not found: {legal_csv_path}")
            return False

        rep_count = 0
        with open(legal_csv_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)

            for row in reader:
                # Clean up the row data
                cleaned_row = {k.strip(): (v.strip() if v else '') for k, v in row.items()}

                # Skip empty rows
                if not cleaned_row.get('rep_id'):
                    continue

                # Create LegalRepresentative object
                rep = LegalRepresentative(
                    rep_id=cleaned_row.get('rep_id', ''),
                    customer_id=cleaned_row.get('customer_id', ''),
                    ho_ten=cleaned_row.get('ho_ten', ''),
                    gioi_tinh=cleaned_row.get('gioi_tinh', ''),
                    ngay_sinh=cleaned_row.get('ngay_sinh', ''),
                    quoc_tich=cleaned_row.get('quoc_tich', ''),
                    dan_toc=cleaned_row.get('dan_toc', ''),
                    loai_giay_to=cleaned_row.get('loai_giay_to', ''),
                    so_giay_to=cleaned_row.get('so_giay_to', ''),
                    ngay_cap=cleaned_row.get('ngay_cap', ''),
                    ngay_het_han=cleaned_row.get('ngay_het_han', ''),
                    noi_cap=cleaned_row.get('noi_cap', ''),
                    dia_chi_thuong_tru=cleaned_row.get('dia_chi_thuong_tru', ''),
                    dia_chi_lien_lac=cleaned_row.get('dia_chi_lien_lac', ''),
                    chuc_danh=cleaned_row.get('chuc_danh', ''),
                )

                session.add(rep)
                rep_count += 1

                # Commit in batches
                if rep_count % 50 == 0:
                    session.commit()
                    print(f"   Processed {rep_count} representatives...")

        session.commit()
        print(f"   ✅ Loaded {rep_count} legal representatives")

        # Final verification
        total_customers = session.query(CustomerProfile).count()
        total_reps = session.query(LegalRepresentative).count()

        print(f"\n🎉 DATA LOADING COMPLETED!")
        print(f"   📊 Total customers in database: {total_customers}")
        print(f"   📊 Total representatives in database: {total_reps}")

        return True

    except Exception as e:
        session.rollback()
        print(f"❌ Error loading CSV data: {e}")
        print(f"Error type: {type(e).__name__}")
        return False
    finally:
        session.close()


if __name__ == '__main__':
    create_database_now()
    db_path, engine, session = create_database_with_schema()
    load_data_from_csv_files(session)
