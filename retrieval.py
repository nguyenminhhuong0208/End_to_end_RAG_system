import os
import faiss


from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.embeddings import OpenAIEmbeddings
from sentence_transformers import SentenceTransformer

class Retrieval:
    def __init__(self, 
                embedding_model: str = "AITeamVN/Vietnamese_Embedding_v2", # trùng với embedding_model trong chunk_embedding.py  
                path: str = "data_RAG/data", 
                chunk_size: int = 1000,
                chunk_overlap: int = 200,
                is_huggingface: bool = True,

            ):
        
        self.embedding_model = embedding_model
        self.path = path
        self.vectorstore = None
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap  
        if is_huggingface:
            self.embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)
    def load_document(self):
        """Load documents from the specified path.
        Returns: 
            documents (list): List of loaded documents."""
        # Load documents from the specified path
        loader = DirectoryLoader(
            self.path,
            glob="*.txt",
            show_progress=True,
        )
        documents = loader.load()
        return documents
    

    def split_document(self, documents):
        """Split documents into chunks using RecursiveCharacterTextSplitter.
        Args:
            documents (list): List of documents to be split."""
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
        texts = text_splitter.split_documents(documents)
        print(f"Split into {len(texts)} chunks")
        return texts
    

    def create_vectorstore(self, all_split):
        """Create a FAISS vectorstore from the loaded documents.
        Args:
            all_split (list): List of split documents."""
        # embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)
        
        # all_split = self.split_document(documents)
        embedding_dim = len(self.embeddings.embed_query("hello world"))

        index = faiss.IndexFlatL2(embedding_dim)
        
        self.vectorstore = FAISS.from_documents(all_split, self.embeddings)

        _ = self.vectorstore.add_documents(documents=all_split)

        return self.vectorstore
            
    def retrieve(self, query: str, top_k: int = 5):
        if self.vectorstore is None:
            self.create_vectorstore()

        return self.vectorstore.similarity_search(query, top_k)
    
def main():
    # Example usage
    retriever = Retrieval()
    documents = retriever.load_document()
    split_docs = retriever.split_document(documents)
    retriever.create_vectorstore(split_docs)
    
    query = "Trường Đại Học Công Nghệ ở đâu?"
    results = retriever.retrieve(query)
    
    for result in results:
        print(result)

if __name__ == "__main__":
    main()