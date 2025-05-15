import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import json
import os
from tqdm import tqdm
import torch

# Cấu hình
FAISS_DB_DIR = "faiss_db"  # Thư mục chứa FAISS index
DATA_DIR = "Data_uet"  # Thư mục chứa file gốc
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"  # Trùng với mô hình tạo FAISS
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Khởi tạo mô hình nhúng
print("Loading embedding model...")
embedding_model = SentenceTransformer(EMBEDDING_MODEL, device=DEVICE)

# Tải FAISS index
index = faiss.read_index(os.path.join(FAISS_DB_DIR, "faiss_index.idx"))

# Tải metadata
with open(os.path.join(FAISS_DB_DIR, "metadata.json"), 'r', encoding='utf-8') as f:
    metadatas = json.load(f)

# Hàm đọc nội dung từ file gốc
def load_content_from_file(file_name):
    file_path = os.path.join(DATA_DIR, file_name)
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        content = " ".join(lines[2:]).strip()  # Nội dung từ dòng thứ 3 trở đi
    return content

# Hàm truy vấn
def query_faiss(query, k=10):
    # Mã hóa câu truy vấn
    query_embedding = embedding_model.encode([query], convert_to_numpy=True, show_progress_bar=False)
    
    # Tìm k tài liệu liên quan nhất
    distances, indices = index.search(query_embedding, k)
    
    # Lấy kết quả
    results = []
    for i, idx in enumerate(indices[0]):
        if idx < len(metadatas):  # Đảm bảo index hợp lệ
            metadata = metadatas[idx]
            content = load_content_from_file(metadata["file"])  # Tải nội dung
            results.append({
                "index": idx,
                "distance": distances[0][i],
                "url": metadata["url"],
                "title": metadata["title"],
                "file": metadata["file"],
                "content": content[:500] + "..." if len(content) > 500 else content  # Cắt ngắn để dễ đọc
            })
    return results

# Thử nghiệm truy vấn
if __name__ == "__main__":
    query = "Lịch sử thành lập trường Đại học Quốc gia Hà Nội"
    print(f"Query: {query}")
    results = query_faiss(query)
    
    print("\nKết quả truy vấn:")
    for result in results:
        print(f"- Index: {result['index']}")
        print(f"  Distance: {result['distance']:.4f}")
        print(f"  URL: {result['url']}")
        print(f"  Title: {result['title']}")
        print(f"  File: {result['file']}")
        print(f"  Content: {result['content']}")
        print("-" * 80)