import os
import glob
import csv
import time
# import pandas as pd

""" Create a QA pair using Google Gemini API """
from google import genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Please set the GOOGLE_API_KEY environment variable.")

client = genai.Client(api_key= GEMINI_API_KEY)
     
def create_prompt(text):
    prompt = f"""
   Bạn là một chuyên gia trong lĩnh vực giáo dục và tuyển sinh, đang tạo dữ liệu hỏi–đáp (QA) về Trường Đại học Công nghệ, Đại học Quốc gia Hà Nội.

Cho văn bản sau, nội dung xoay quanh thông tin của Trường Đại học Công nghệ – ĐHQGHN, bao gồm: tên trường, địa chỉ, số điện thoại, email, website, các ngành học, và thông tin tuyển sinh.

### Yêu cầu:

- Đọc kỹ nội dung văn bản bên dưới.
- Tạo tối đa 15 cặp câu hỏi – câu trả lời ngắn gọn dựa vào thông tin bổ sung của văn bản.
- Mỗi câu hỏi bắt đầu bằng "Q:", mỗi câu trả lời bắt đầu bằng "A:".
- Câu hỏi và câu trả lời phải ngắn gọn, rõ ràng, dễ hiểu.
- Câu hỏi phải **chỉ rõ chủ ngữ**, không được sử dụng các đại từ như “trường”, “ngành”, “trường này”, “ngành đó” nếu gây mơ hồ.
- Đảm bảo định dạng đồng nhất, mỗi dòng một câu hỏi hoặc một câu trả lời.

### Ví dụ định dạng mong muốn:
Q: Văn bằng tốt nghiệp ngành Công nghệ Thông tin là gì?  
A: Cử nhân

Q: Thời gian đào tạo ngành Công nghệ Thông tin là bao lâu?  
A: 4 năm

Q: Trường Đại học Công nghệ có địa chỉ ở đâu?  
A: 144 Xuân Thủy, Cầu Giấy, Hà Nội

---
Văn bản đầu vào:  
{text}

"""
    # print("Prompt: ", prompt)
    return prompt

def generate_qa_pair(text, model="gemini-2.0-flash"):
    prompt = create_prompt(text)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )
    return response



def save_qa_to_csv(text_response: str, output_file: str = "qa_output.csv"):
    """
    Lưu các cặp Q&A từ response dạng văn bản vào file CSV với hai cột: question, answer.
    Tự động tạo thư mục nếu chưa tồn tại.

    Args:
        text_response (str): Chuỗi chứa các cặp Q: [...] và A: [...]
        output_file (str): Đường dẫn file CSV để lưu, ví dụ: 'output/qa_output.csv'
    """
    # Tạo thư mục nếu chưa tồn tại
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Parse Q&A
    qa_pairs = []
    lines = text_response.strip().split('\n')
    current_q = ""

    for line in lines:
        line = line.strip()
        if line.startswith("Q:"):
            current_q = line[2:].strip()
        elif line.startswith("A:") and current_q:
            answer = line[2:].strip()
            qa_pairs.append((current_q, answer))
            current_q = ""

    # Ghi ra CSV
    with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['question', 'answer'])
        writer.writerows(qa_pairs)

    print(f"✅ Đã lưu {len(qa_pairs)} cặp Q&A vào file '{output_file}'.")


if __name__ == "__main__":
    # with open("data_RAG\data\doc1.txt", "r", encoding="utf-8") as f:

    #     text = f.read()
    #     # print("Text: ", text)

    # response = generate_qa_pair(text)
    # print(response.text)

    # # Lưu kết quả vào file CSV
    # save_qa_to_csv(response.text, output_file="QA_answer/ans_doc1.csv")
    cnt = 0
    for file in glob.glob("data_RAG/data/*.txt"):
        
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()
            # print("Text: ", text)

        response = generate_qa_pair(text)
        # print(response.text)

        # Lưu kết quả vào file CSV
        dir_path = os.path.dirname(file)
        # Xoá đuôi .txt
        file_name = os.path.basename(file).replace(".txt", "")
        save_qa_to_csv(response.text, output_file=f"data_RAG/QA Final/QA_{file_name}.csv")

        # Đợi 20s để tránh bị giới hạn API
        cnt +=1
        if cnt == 5:
            time.sleep(20)
            cnt = 0

