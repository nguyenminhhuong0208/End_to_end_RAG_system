import os
from process_answers import clean_text, is_good_answer

def load_questions(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def generate_answer(question):
    # Clean the question first
    cleaned_q = clean_text(question)
    
    # If the question starts with common question words, remove them
    question_starters = ['là gì', 'là ai', 'là', 'có phải', 'bao gồm', 'gồm', 'có', 'được']
    for starter in question_starters:
        if cleaned_q.lower().startswith(starter + ' '):
            cleaned_q = cleaned_q[len(starter):].strip()
    
    # If the question ends with question marks or other punctuation, remove them
    cleaned_q = cleaned_q.rstrip('?.,!: ')
    
    # Check if the cleaned question makes a good answer
    if is_good_answer(cleaned_q):
        return cleaned_q
    return None

def main():
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Input and output file paths
    input_file = 'output/unique_questions.txt'
    output_file = 'output/reference_answers.txt'
    
    # Load questions
    print(f"Loading questions from {input_file}...")
    questions = load_questions(input_file)
    print(f"Found {len(questions)} questions")
    
    # Generate answers
    answers = []
    for question in questions:
        answer = generate_answer(question)
        if answer:
            answers.append(answer)
    
    # Remove duplicates from answers
    unique_answers = list(set(answers))
    
    # Sort answers by length
    unique_answers.sort(key=len)
    
    # Save answers
    with open(output_file, 'w', encoding='utf-8') as f:
        for answer in unique_answers:
            f.write(answer + '\n')
    
    print(f"Generated {len(unique_answers)} answers in {output_file}")

if __name__ == "__main__":
    main() 