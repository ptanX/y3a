import os

import nltk
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from nltk import sent_tokenize

nltk.download('punkt_tab')

os.environ["GOOGLE_API_KEY"] = "MAY_THANG_HACKER_NGHI_TAO_NGU_MA_POST_TOKEN_AH"


def semantic_chunking(text, max_tokens=1024):
    sentences = sent_tokenize(text)
    chunks, current_chunk, current_length = [], [], 0

    for sentence in sentences:
        length = len(sentence.split())
        if current_length + length > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk, current_length = [sentence], length
        else:
            current_chunk.append(sentence)
            current_length += length

    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks


def split_documents_semantically(documents):
    chunks = []
    for i, doc in enumerate(documents):
        semantic_chunks = semantic_chunking(doc.page_content)
        for j, chunk_text in enumerate(semantic_chunks):
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "source": doc.metadata.get("source", ""),
                    "page": doc.metadata.get("page", i + 1),
                    "chunk_id": f"{i + 1}_{j}"
                }
            })
    return chunks


def store_chunks(db, chunks):
    documents = [
        Document(
            page_content=chunk["text"],
            metadata={
                "page": chunk["metadata"]["page"],
                "chunk_id": chunk["metadata"]["chunk_id"]
            }
        )
        for chunk in chunks
    ]
    db.add_documents(documents=documents)


def init_predefined_docs_to_db():
    """Processes and adds uploaded PDF files to the database."""
    embedding = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    # embedding = OllamaEmbeddings(
    #     model="nomic-embed-text",
    #     base_url="http://localhost:11434"
    # )
    # Test the model
    print(embedding.embed_query("test connection"))
    print("✅ Successfully loaded nomic-embed-text embedding model")
    db = Chroma(collection_name="rawiq_database",
                embedding_function=embedding,
                persist_directory='./rawiq_db')
    documentations_path = "./documentations"

    for filename in os.listdir(documentations_path):
        file_path = os.path.join(documentations_path, filename)
        # Check if it's a file (not a subfolder)
        if os.path.isfile(file_path):
            print(f'######### File Path: {file_path} ############')
            loader = PyPDFLoader(file_path)
            chunks = split_documents_semantically(loader.load())
            store_chunks(db, chunks)


init_predefined_docs_to_db()
