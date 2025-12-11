from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.lending.db.bidv_entity import DocumentationInformation
from src.lending.startup.environment_initialization import DATABASE_PATH


def query_document_information_by_id(doc_id):
    engine = create_engine(f"sqlite:///{DATABASE_PATH}")
    session = sessionmaker(bind=engine)()
    entity = session.get(DocumentationInformation, doc_id)
    return entity
