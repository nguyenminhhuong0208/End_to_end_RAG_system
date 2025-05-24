import os
import csv
from glob import glob

def create_test_data(input_folder="./data_RAG/QA_final", output_folder="test-data"):
    os.makedirs(output_folder, exist_ok=True)

    question_path = os.path.join(output_folder, "question.txt")
    answer_path = os.path.join(output_folder, "reference_answer.txt")

    with open(question_path, "w", encoding="utf-8") as fq, \
         open(answer_path, "w", encoding="utf-8") as fa:
        
        csv_files = glob(os.path.join(input_folder, "*.csv"))
        for csv_file in csv_files:
            with open(csv_file, "r", encoding="utf-8-sig") as f: 
                reader = csv.DictReader(f)
                
                for row in reader:
                    question = row.get("question", "").strip()
                    answer = row.get("answer", "").strip()
                    if question and answer:
                        fq.write(question + "\n")
                        fa.write(answer + "\n")

if __name__ == "__main__":
    create_test_data()
