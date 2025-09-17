import json
import os

import requests
import streamlit as st
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter


# Pure Ollama embedding setup - NO HuggingFace
# def initialize_embedding_model():
#     """Initialize Ollama embedding model with fallbacks."""
#     embedding = OllamaEmbeddings(
#         model="nomic-embed-text",
#         base_url="http://localhost:11434"
#     )
#     # Test the model
#     print(embedding.embed_query("test connection"))
#     print("✅ Successfully loaded nomic-embed-text embedding model")
#     return embedding
#
#
# # Initialize the embedding model
# embedding_model = initialize_embedding_model()
#
# # Initialize ChromaDB with the embedding model
# db = Chroma(
#     collection_name="rawiq_database",
#     embedding_function=embedding_model,
#     persist_directory='./rawiq_db'
# )


# def format_docs(docs):
#     """Formats a list of document objects into a single string."""
#     return "\n\n".join(doc.page_content for doc in docs)


# def add_to_db(uploaded_files):
#     """Processes and adds uploaded PDF files to the database."""
#     if not uploaded_files:
#         st.error("No files uploaded!")
#         return
#
#     for uploaded_file in uploaded_files:
#         # Save the uploaded file to a temporary path
#         temp_file_path = os.path.join("./temp", uploaded_file.name)
#         os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
#
#         with open(temp_file_path, "wb") as temp_file:
#             temp_file.write(uploaded_file.getbuffer())
#
#         # Load the PDF file
#         loader = PyPDFLoader(temp_file_path)
#         data = loader.load()
#
#         # Extract metadata and content
#         doc_metadata = [data[i].metadata for i in range(len(data))]
#         doc_content = [data[i].page_content for i in range(len(data))]
#
#         # Split documents using RecursiveCharacterTextSplitter (NO HuggingFace)
#         text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=1000,
#             chunk_overlap=100,
#             length_function=len,
#             separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
#         )
#
#         chunks = text_splitter.create_documents(doc_content, doc_metadata)
#
#         # Add chunks to database
#         db.add_documents(chunks)
#
#         # Clean up temporary file
#         os.remove(temp_file_path)


# def run_rag_chain(query, model_name="llama3.1"):
#     """Processes a query using RAG with pure Ollama setup."""
#
#     # Create retriever
#     retriever = db.as_retriever(search_type="similarity", search_kwargs={'k': 5})
#
#     # Prompt template
#     PROMPT_TEMPLATE = """
#     You are a highly knowledgeable assistant specializing in pharmaceutical sciences.
#     Answer the question based only on the following context:
#     {context}
#
#     Question: {question}
#
#     Provide a clear, accurate, and concise answer based on the context above.
#     Don't justify your answers or mention the context explicitly.
#     If the context doesn't contain relevant information, say "I don't have enough information to answer this question."
#     """
#
#     prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
#
#     # Initialize Ollama LLM
#     try:
#         chat_model = Ollama(
#             model=model_name,
#             base_url="http://localhost:11434",
#             temperature=0.1
#         )
#     except Exception as e:
#         st.error(f"❌ Error connecting to Ollama model '{model_name}': {e}")
#         st.error("Make sure Ollama is running and the model is installed.")
#         return f"Error: Could not connect to model {model_name}"
#
#     # Output parser
#     output_parser = StrOutputParser()
#
#     # Build RAG chain
#     rag_chain = (
#             {"context": retriever | format_docs, "question": RunnablePassthrough()}
#             | prompt_template
#             | chat_model
#             | output_parser
#     )
#
#     # Execute the chain
#     try:
#         response = rag_chain.invoke(query)
#         return response
#     except Exception as e:
#         st.error(f"❌ Error generating response: {e}")
#         return "Error: Could not generate response. Please check your Ollama setup."


def submit(question):
    # Prompt template
    message = {
        "inputs": {
            "messages": [
                {
                    "role": "user",
                    "content": question
                }
            ]
        }
    }
    url = "http://127.0.0.1:8080/invocations"
    headers = {
        'Content-Type': 'application/json'
    }

    # Explain: just the curl sample
    # TODO:
    #  - Impl the chain and the parser
    try:
        response = requests.request("POST", url, headers=headers, data=json.dumps(message), timeout=300)
        print(response.text)
        return response.json().get("predictions").get("messages")[0].get("content")
    except Exception as e:
        print(e)
        return "Error: Could not submit message. Please check your setup."

def main():
    """Main Streamlit application - 100% HuggingFace-free."""

    st.set_page_config(
        page_title="Rawiq",
        page_icon="🧬",
        layout="wide"
    )

    st.header("🧬 Rawiq Insight Retrieval System")

    # Main query interface
    query = st.text_area(
        "💡 Enter your  question:",
        placeholder="e.g., What are the latest AI applications in drug discovery?",
        height=100
    )

    col1, col2 = st.columns([1, 4])

    with col1:
        submit_button = st.button("🚀 Submit Query", type="primary")

    with col2:
        if submit_button:
            if not query.strip():
                st.warning("⚠️ Please enter a question")
            else:
                selected_model = st.session_state.get("selected_model", "Rawiq")

                with st.spinner(f"🤔 Processing with {selected_model}..."):
                    # result = run_rag_chain(query, model_name=selected_model)
                    result = submit(query)

                st.success("✅ Response generated!")
                st.markdown("### 📋 Answer:")
                st.write(result)

    # Sidebar configuration
    # with st.sidebar:
        # st.title("⚙️ Local AI Settings")
        #
        # # Model selection
        # st.subheader("🤖 Language Model")
        # llm_models = [
        #     "llama3.1", "llama3.1:8b", "llama3.1:70b", "llama3.1:405b",
        #     "llama3.2", "llama3.2:3b", "llama3.2:1b",
        #     "codellama", "codellama:13b",
        #     "mistral", "mistral:7b",
        #     "phi3", "phi3:mini",
        #     "gemma2", "gemma2:9b"
        # ]

        # selected_model = st.selectbox(
        #     "Choose your model:",
        #     llm_models,
        #     index=0
        # )
        #
        # if st.button("💾 Set Model"):
        #     st.session_state.selected_model = selected_model
        #     st.success(f"✅ Model set to: {selected_model}")
        #
        # st.markdown("---")
        #
        # # Embedding model info
        # st.subheader("🔤 Embedding Model")
        # st.info("Currently using Ollama embeddings")
        #
        # embedding_options = [
        #     "nomic-embed-text (Recommended)",
        #     "mxbai-embed-large (High Quality)",
        #     "all-minilm (Fast)",
        #     "simple-text (Fallback)"
        # ]
        #
        # st.selectbox("Embedding model:", embedding_options, disabled=True)
        #
        # st.markdown("---")
        #
        # # Connection status
        # st.subheader("🔍 System Status")
        # if st.button("🔧 Test Connection"):
        #     with st.spinner("Testing..."):
        #         try:
        #             # Test LLM
        #             test_llm = Ollama(model=selected_model)
        #             llm_response = test_llm.invoke("Say 'OK' if you're working")
        #             st.success("✅ LLM: Connected")
        #
        #             # Test embeddings
        #             # test_embed = embedding_model.embed_query("test")
        #             st.success("✅ Embeddings: Working")
        #
        #             st.balloons()
        #
        #         except Exception as e:
        #             st.error(f"❌ Connection failed: {e}")
        #
        #             with st.expander("🛠️ Setup Instructions"):
        #                 st.markdown("""
        #                 **Install Ollama:**
        #                 ```bash
        #                 curl -fsSL https://ollama.ai/install.sh | sh
        #                 ```
        #
        #                 **Start Ollama:**
        #                 ```bash
        #                 ollama serve
        #                 ```
        #
        #                 **Install Models:**
        #                 ```bash
        #                 ollama pull llama3.1
        #                 ollama pull nomic-embed-text
        #                 ```
        #                 """)
        #
        # st.markdown("---")
        #
        # # Document upload
        # st.subheader("📄 Document Management")
        # uploaded_files = st.file_uploader(
        #     "Upload PDFs:",
        #     type=["pdf"],
        #     accept_multiple_files=True,
        #     help="Add documents to improve query responses"
        # )
        #
        # if st.button("📚 Process Documents"):
        #     if not uploaded_files:
        #         st.warning("⚠️ Please upload PDF files first")
        #     else:
        #         with st.spinner("🔄 Processing documents..."):
        #             try:
        #                 # add_to_db(uploaded_files)
        #                 st.success(f"✅ Successfully processed {len(uploaded_files)} document(s)!")
        #             except Exception as e:
        #                 st.error(f"❌ Error processing documents: {e}")

    # # Footer
    st.markdown("---")
    # col1, col2, col3 = st.columns(3)
    #
    # with col1:
    #     st.info("🚀 **100% Local AI**\nNo internet required")
    #
    # with col2:
    #     st.info("🔒 **Privacy First**\nYour data stays local")
    #
    # with col3:
    #     st.info("⚡ **Low API Costs**\nRun unlimited queries")

    st.markdown(
        "<div style='text-align: center; color: #666; margin-top: 2rem;'>"
        "Built with ❤️ using AI"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
