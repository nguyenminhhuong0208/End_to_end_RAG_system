import os
import faiss

from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

def load_documents(file_path: str):
    """Load documents from the specified path. The documents include .txt file.
    Args:
        file_path: path to the documents
    Return:
        documents: list of texts 
        """
    # print(file_path)
    loader = DirectoryLoader(file_path, glob="*.txt", show_progress=True)
    documents = loader.load()
    return documents

def split_and_create_vectorstore(documents, 
                                 embedding_model_name: str,
                                 chunk_size: int = 600, 
                                 chunk_overlap: int = 200,
                                 save_vector: bool = True,
                                 path_save_vector: str = "vector_embedding/faiss_data"
                                 ):
    """Split documents and create vectorspace to use input RAG
    Args:
        documents: List of texts which are the content of file .txt.
        chunk_size: size of chunk
        chunk_overlap: số lượng từ giữ lại từ chunk trước để giữ mạch ngữ nghĩa
        embedding_model_name: name of model to embedding vector database.
    Return:
        
        """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap
    )
    all_split = text_splitter.split_documents(documents)
    print(f"Splitter into {len(all_split)} chunks")
    
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
    embedding_dim = len(embeddings.embed_query("Hello world"))
    index = faiss.IndexFlatL2(embedding_dim)
        
    vectorstore = FAISS.from_documents(all_split, embeddings)

    _ = vectorstore.add_documents(documents=all_split)
    #Save to local
    if save_vector:
        path = path_save_vector + f"_{chunk_size}_{chunk_overlap}"
        vectorstore.save_local(path)
    
    return vectorstore

def load_vectorstore_local(path, embeddings_model_name):
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)
    new_vector_store = FAISS.load_local(
    path, embeddings, allow_dangerous_deserialization=True
    )
    return new_vector_store