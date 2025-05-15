import os
import glob
from process_answers import clean_text, is_good_answer

def load_questions(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def load_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_key_terms(text):
    # Get important words from text (length > 2 characters)
    words = clean_text(text.lower()).split()
    return set(word for word in words if len(word) > 2)

def find_answer_in_text(question, text, max_answers=2):
    # Clean the text and split into paragraphs
    cleaned_text = clean_text(text)
    paragraphs = [p.strip() for p in cleaned_text.split('\n') if len(p.strip()) >= 30]
    
    # Get key terms from question
    question_terms = extract_key_terms(question)
    
    potential_answers = []
    patterns = ['là', 'được', 'bao gồm', 'gồm', 'có']  # Reduced pattern list
    
    for paragraph in paragraphs:
        # Quick check if paragraph might be relevant
        para_terms = extract_key_terms(paragraph)
        matching_terms = len(question_terms.intersection(para_terms))
        
        if matching_terms >= min(2, len(question_terms)):
            paragraph_lower = paragraph.lower()
            
            # Try to find answer after patterns
            for pattern in patterns:
                if len(potential_answers) >= max_answers:
                    break
                    
                if ' ' + pattern + ' ' in paragraph_lower:
                    parts = paragraph.split(' ' + pattern + ' ', 1)
                    if len(parts) == 2:
                        answer = clean_text(parts[1])
                        if is_good_answer(answer) and answer not in potential_answers:
                            potential_answers.append(answer)
                            break
            
            # If no pattern found but paragraph is good
            if not potential_answers and is_good_answer(paragraph):
                potential_answers.append(paragraph)
                
            if len(potential_answers) >= max_answers:
                break
    
    return potential_answers

def main():
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Load questions
    questions = load_questions('output/questions.txt')
    print(f"Loaded {len(questions)} questions")
    
    # Get all text files in data directory
    text_files = glob.glob('data/*.txt')
    print(f"Found {len(text_files)} text files in data directory")
    
    all_answers = set()
    processed_files = 0
    
    # Process each text file
    for file_path in text_files:
        processed_files += 1
        if processed_files % 10 == 0:
            print(f"Processing file {processed_files}/{len(text_files)}...")
            
        text_content = load_text_file(file_path)
        
        # For each question, try to find answers in the text
        for question in questions:
            answers = find_answer_in_text(question, text_content)
            all_answers.update(answers)
    
    # Convert to list and sort by length
    all_answers = sorted(list(all_answers), key=len)
    
    # Save answers
    output_file = 'output/reference_answers.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        for answer in all_answers:
            f.write(answer + '\n')
    
    print(f"Generated {len(all_answers)} answers in {output_file}")

if __name__ == "__main__":
    main() 