import os
from typing import Any

import mlflow
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.constants import START, END
from langgraph.graph.state import CompiledStateGraph, StateGraph
from mlflow.pyfunc import ChatAgent
from mlflow.types.agent import ChatAgentMessage, ChatContext, ChatAgentResponse

from agent.agent_application import AgentApplication
from graph.graph_provider import GraphProvider
from state.mapper import DefaultStateMapper
from state.type import DefaultState


def format_docs(docs):
    """Formats a list of document objects into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)


class Demo0GraphProvider(GraphProvider[DefaultState]):

    def add_to_db(self):
        documentations_path = "./documentations"
        for filename in os.listdir(documentations_path):
            file_path = os.path.join(documentations_path, filename)
            if os.path.isfile(file_path):
                print(f"######################### starting import file: {file_path} to vector search db")
                # Load the PDF file
                loader = PyPDFLoader(file_path)
                data = loader.load()

                # Extract metadata and content
                doc_metadata = [data[i].metadata for i in range(len(data))]
                doc_content = [data[i].page_content for i in range(len(data))]

                # Split documents using RecursiveCharacterTextSplitter (NO HuggingFace)
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=100,
                    length_function=len,
                    separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
                )

                chunks = text_splitter.create_documents(doc_content, doc_metadata)

                # Add chunks to database
                self.db.add_documents(chunks)

    def __init__(self):
        embedding = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url="http://localhost:11434"
        )
        # Test the model
        print(embedding.embed_query("test connection"))
        print("✅ Successfully loaded nomic-embed-text embedding model")
        self.embedding = embedding
        self.db = Chroma(collection_name="rawiq_database",
                         embedding_function=self.embedding,
                         persist_directory='./rawiq_db')

    def provide(self) -> CompiledStateGraph:
        # self.add_to_db()
        graph_builder = StateGraph(DefaultState)
        graph_builder.add_node("chatbot", self.chatbot)
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_edge("chatbot", END)
        return graph_builder.compile()

    def chatbot(self, state: DefaultState):
        retriever = self.db.as_retriever(search_type="similarity", search_kwargs={'k': 5})
        # Prompt template
        PROMPT_TEMPLATE = """
            You are a highly knowledgeable assistant specializing in financial report reading. 
            Answer the question based only on the following context:
            {context}

            Question: {question}

            Provide a clear, accurate, and concise answer based on the context above.
            Don't justify your answers or mention the context explicitly.
            If the context doesn't contain relevant information, say "I don't have enough information to answer this question."
            """

        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        llm = ChatOllama(
            model="llama3.1:8b",
            temperature=0
        )
        output_parser = StrOutputParser()

        # Build RAG chain
        rag_chain = (
                {"context": retriever | format_docs, "question": RunnablePassthrough()}
                | prompt_template
                | llm
                | output_parser
        )
        messages = state.get("messages", [])
        current_question = messages[-1].content if messages else ""
        response = rag_chain.invoke(current_question)
        return {"messages": response}


class Demo0ChatAgent(ChatAgent):

    def __init__(self, graph: GraphProvider):
        self.graph = graph
        self.mapper = DefaultStateMapper()

    def predict(self, messages: list[ChatAgentMessage], context: ChatContext | None = None,
                custom_inputs: dict[str, Any] | None = None) -> ChatAgentResponse:
        input_state = self.mapper.map_from_message_to_state(messages)
        state = self.graph.provide().invoke(input_state)
        result = self.mapper.map_from_state_to_message(state)
        return ChatAgentResponse(messages=result)


mlflow.langchain.autolog()
chat_agent = Demo0ChatAgent(graph=Demo0GraphProvider())
mlflow.models.set_model(chat_agent)
