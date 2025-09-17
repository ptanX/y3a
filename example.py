import os
from nltk import sent_tokenize, download
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langgraph.graph import StateGraph

# 🔐 Set your Google API key
os.environ["GOOGLE_API_KEY"] = "your-google-api-key"  # Replace with your actual key

# 📥 Download NLTK tokenizer
download('punkt')

# 📄 Semantic Chunking
def semantic_chunking(text, max_tokens=500):
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

# 📄 Split Documents
def split_documents_semantically(documents):
    chunks = []
    for i, doc in enumerate(documents):
        semantic_chunks = semantic_chunking(doc.page_content)
        for j, chunk_text in enumerate(semantic_chunks):
            chunks.append(Document(
                page_content=chunk_text,
                metadata={"source": doc.metadata.get("source", ""), "page": i + 1, "chunk_id": f"{i + 1}_{j}"}
            ))
    return chunks

# 🧠 Load All Bank PDFs
def load_all_banks(documentations_path="./documentations"):
    embedding = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    bank_dbs = {}

    for filename in os.listdir(documentations_path):
        if filename.endswith(".pdf"):
            bank_name = filename.replace(".pdf", "").lower()
            print(f"📄 Loading: {bank_name}")
            loader = PyPDFLoader(os.path.join(documentations_path, filename))
            docs = loader.load()
            chunks = split_documents_semantically(docs)
            db = Chroma(persist_directory=f"./db_{bank_name}", embedding_function=embedding)
            db.add_documents(chunks)
            bank_dbs[bank_name] = db
    return bank_dbs

# 🧠 Extract Bank Names from Question
def extract_bank_names(question, known_banks):
    prompt = f"""
    Extract bank names from the question below. Return only names that match this list:
    {', '.join(known_banks)}
    Question: "{question}"
    Return as a comma-separated list.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    response = llm.invoke(prompt).content
    return [name.strip().lower() for name in response.split(",") if name.strip().lower() in known_banks]

# 🔍 Router Node
def route_question(state):
    question = state["question"]
    bank_names = extract_bank_names(question, list(state["bank_dbs"].keys()))

    if len(bank_names) == 1:
        return {"question": question, "intent": "query_single_bank", "banks": bank_names, "bank_dbs": state["bank_dbs"]}
    elif len(bank_names) == 2:
        return {"question": question, "intent": "compare_banks", "banks": bank_names, "bank_dbs": state["bank_dbs"]}
    else:
        return {"question": question, "intent": "fallback", "banks": [], "bank_dbs": state["bank_dbs"]}

# 📌 Query Node
def query_single_bank(state):
    bank = state["banks"][0]
    db = state["bank_dbs"][bank]
    docs = db.similarity_search(state["question"])
    context = "\n".join([doc.page_content for doc in docs])
    prompt = f"""Answer the question using the context below:
    Context: {context}
    Question: {state["question"]}"""
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    return {"answer": llm.invoke(prompt).content}

# ⚖️ Compare Node
def compare_banks(state):
    bank1, bank2 = state["banks"]
    db1 = state["bank_dbs"][bank1]
    db2 = state["bank_dbs"][bank2]

    docs1 = db1.similarity_search(state["question"])
    docs2 = db2.similarity_search(state["question"])

    context1 = "\n".join([doc.page_content for doc in docs1])
    context2 = "\n".join([doc.page_content for doc in docs2])

    prompt = f"""Compare the following data:
    {bank1.upper()}: {context1}
    {bank2.upper()}: {context2}
    Question: {state["question"]}"""
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    return {"answer": llm.invoke(prompt).content}

# ❓ Fallback Node
def fallback(state):
    question = state["question"]
    prompt = f"""I couldn't understand your intent clearly. Can you clarify this question?
    Question: {question}"""
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    return {"answer": llm.invoke(prompt).content}

# 🚀 Build LangGraph
def build_graph():
    graph = StateGraph()
    graph.add_node("router", route_question)
    graph.add_node("query_single_bank", query_single_bank)
    graph.add_node("compare_banks", compare_banks)
    graph.add_node("fallback", fallback)

    graph.set_entry_point("router")
    graph.add_conditional_edges("router", {
        "query_single_bank": "query_single_bank",
        "compare_banks": "compare_banks",
        "fallback": "fallback"
    })

    graph.set_finish_point("query_single_bank")
    graph.set_finish_point("compare_banks")
    graph.set_finish_point("fallback")

    return graph.compile()

# 🟢 Run the App
if __name__ == "__main__":
    print("🔄 Loading all bank databases...")
    bank_dbs = load_all_banks("./documentations")

    app = build_graph()

    while True:
        user_input = input("\n💬 Ask a financial question: ")
        result = app.invoke({"question": user_input, "bank_dbs": bank_dbs})
        print(f"\n🧠 Answer:\n{result['answer']}")
