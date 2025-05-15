import os

def load_questions(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        questions = [line.strip() for line in f.readlines() if line.strip()]
    return questions

def remove_duplicates(questions):
    # Create a set to store unique questions
    seen = set()
    unique_questions = []
    
    for q in questions:
        # Remove leading/trailing punctuation and spaces
        cleaned_q = q.strip('.,?! ')
        if cleaned_q not in seen:
            seen.add(cleaned_q)
            unique_questions.append(q)
    
    return unique_questions

def save_questions(questions, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for q in questions:
            f.write(q + '\n')

def main():
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Input and output file paths
    input_file = 'output/questions.txt'
    output_file = 'output/unique_questions.txt'
    
    # Load questions
    print(f"Loading questions from {input_file}...")
    questions = load_questions(input_file)
    print(f"Found {len(questions)} questions")
    
    # Remove duplicates
    unique_questions = remove_duplicates(questions)
    print(f"Reduced to {len(unique_questions)} unique questions")
    
    # Save unique questions
    save_questions(unique_questions, output_file)
    print(f"Saved unique questions to {output_file}")

if __name__ == "__main__":
    main() 