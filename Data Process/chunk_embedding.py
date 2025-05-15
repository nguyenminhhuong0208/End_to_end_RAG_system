import os
import torch
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm

# Cấu hình
DATA_DIR = "Data_uet"  
CHUNK_SIZE = 512  
CHUNK_OVERLAP = 100  
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"  
OUTPUT_DIR = "faiss_db" 
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Khởi tạo mô hình nhúng
print("Loading embedding model...")
embedding_model = SentenceTransformer(EMBEDDING_MODEL, device=DEVICE)

# Hàm đọc file và tách thông tin
def load_document(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        url = lines[0].strip()  # Dòng 1 là URL
        title = lines[1].strip()  # Dòng 2 là title
        content = " ".join(lines[2:]).strip()  # Các dòng sau là nội dung
    return url, title, content

# Hàm chia nhỏ và nhúng văn bản
def process_documents(data_dir):
    texts = []
    metadatas = []
    for file_name in tqdm(os.listdir(data_dir)):
        if file_name.endswith(".txt"):
            file_path = os.path.join(data_dir, file_name)
            url, title, content = load_document(file_path)
            
            # Chia nhỏ nội dung
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE, 
                chunk_overlap=CHUNK_OVERLAP
            )
            chunks = text_splitter.split_text(content)
            
            # Thêm metadata và text
            for chunk in chunks:
                texts.append(chunk)
                metadatas.append({"url": url, "title": title, "file": file_name})
    
    # Tạo embedding
    embeddings = embedding_model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    return texts, embeddings, metadatas

# Hàm lưu vào FAISS
def save_to_faiss(embeddings, metadatas, output_dir):
    dimension = embeddings.shape[1]  # Kích thước vector nhúng
    index = faiss.IndexFlatL2(dimension)  # Sử dụng L2 distance
    index.add(embeddings)  # Thêm vector vào index
    
    # Lưu index và metadata
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    faiss.write_index(index, os.path.join(output_dir, "faiss_index.idx"))
    
    # Lưu metadata
    import json
    with open(os.path.join(output_dir, "metadata.json"), 'w', encoding='utf-8') as f:
        json.dump(metadatas, f, ensure_ascii=False, indent=4)

# Thực thi
if __name__ == "__main__":
    print("Processing documents...")
    texts, embeddings, metadatas = process_documents(DATA_DIR)
    print(f"Total chunks: {len(texts)}")
    print(f"Embedding shape: {embeddings.shape}")
    
    print("Saving to FAISS...")
    save_to_faiss(embeddings, metadatas, OUTPUT_DIR)
    print("FAISS database created successfully!")