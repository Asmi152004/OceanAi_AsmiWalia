import os
import shutil
from typing import List, Dict
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document

# Persistence directory for Chroma
CHROMA_PATH = "data/chroma"

class RAGPipeline:
    def __init__(self):
        # Initialize Embeddings (Local HF model)
        self.embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_db = None
        self._load_db()

    def _load_db(self):
        if os.path.exists(CHROMA_PATH):
            self.vector_db = Chroma(persist_directory=CHROMA_PATH, embedding_function=self.embedding_function)
        else:
            self.vector_db = Chroma(persist_directory=CHROMA_PATH, embedding_function=self.embedding_function)

    def ingest_documents(self, documents: List[Dict[str, str]]):
        """
        Ingest a list of documents.
        documents: List of dicts with 'content' and 'source' keys.
        """
        docs = []
        for doc in documents:
            docs.append(Document(page_content=doc['content'], metadata={"source": doc['source']}))

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            add_start_index=True,
        )
        chunks = text_splitter.split_documents(docs)
        
        if chunks:
            if self.vector_db:
                self.vector_db.add_documents(chunks)
            else:
                self.vector_db = Chroma.from_documents(
                    chunks, self.embedding_function, persist_directory=CHROMA_PATH
                )
            self.vector_db.persist()
            return len(chunks)
        return 0

    def retrieve_context(self, query: str, k: int = 3) -> List[Document]:
        if not self.vector_db:
            return []
        
        results = self.vector_db.similarity_search(query, k=k)
        return results

    def clear_db(self):
        if os.path.exists(CHROMA_PATH):
            shutil.rmtree(CHROMA_PATH)
        self.vector_db = None
        self._load_db()
