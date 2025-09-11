# Rawiq

## Overview
Rawiq is an advanced Rawiq Insight Retrieval System designed to help users gain meaningful insights from research papers and documents in the pharmaceutical domain.

## Demo
https://github.com/user-attachments/assets/c12ee305-86fe-4f71-9219-57c7f438f291

## Features
- **Natural Language Querying**: Ask complex questions about the pharmaceutical industry and get concise, accurate answers.
- **Custom Database**: Upload your own research documents to enhance the retrieval system's knowledge base.
- **Similarity Search**: Retrieves the most relevant documents for your query using AI embeddings.
- **Streamlit Interface**: User-friendly interface for queries and document uploads.


## Requirements
1. **Install Ollama then install these model **'
    ```bash
    ollama pull llama3.1:8b
    ollama pull nomic-embed-text
    ```
   Run the llama3.1:8b
    ```bash
    ollama run llama3.1:8b
    ```
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   streamlit run rawiq_app.py
   ```

3. **Use the Application**:
   - Enter your query in the main interface.
   - Optionally, upload research papers in the sidebar to enhance the database.
