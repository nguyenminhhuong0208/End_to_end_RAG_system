import os
import faiss
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

class Retrieval:
    def __init__(self,
                 faiss_vector_path: str = "./faiss_data",
                 embeddings_model_name: str = "AITeamVN/Vietnamese_Embedding_v2",
                 top_k: int = 5
                 ):
        self.faiss_vector_path = faiss_vector_path
        self.embeddings_model_name = embeddings_model_name
        self.top_k = top_k
        self.vectorstore = self.load_vector_local()
        
    
    def load_vector_local(self):
        """Function load vector store from local"""
        
        if os.path.exists(self.faiss_vector_path):
            
            embeddings = HuggingFaceEmbeddings(model_name=self.embeddings_model_name,
                                               model_kwargs={"device": "cpu"})
            vectorstore = FAISS.load_local(
                self.faiss_vector_path, embeddings, allow_dangerous_deserialization=True)
            print("Vector store was loaded.")
            return vectorstore
        else:
            print("The vector store does not exist at:", self.faiss_vector_path)
            return None
        
    def top_retrieval(self, question):
        """Top k relevant chunks based on query
        Args:
            question: Query to retrieval.
        Return: Context to input Generator."""

        if self.vectorstore == None:
            raise ValueError("Vectorstore has not been loaded.")
        retrievel_instance = self.vectorstore.as_retriever(search_kwargs={"k": self.top_k})
        relevant_docs = retrievel_instance.invoke(question)
        context = "\n\n".join([doc.page_content for doc in relevant_docs])

        return context