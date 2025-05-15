import os
import glob
import re

def load_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def clean_sentence(sentence):
    # Remove special characters and extra spaces
    sentence = re.sub(r'[^\w\s\.,]', ' ', sentence)
    sentence = ' '.join(sentence.split())
    # Remove leading punctuation
    sentence = re.sub(r'^[\s\.,]+', '', sentence)
    return sentence

def is_good_sentence(sentence):
    # Check if sentence is meaningful
    if len(sentence.split()) < 3:  # Too few words
        return False
    if len(sentence) < 20 or len(sentence) > 200:  # Too short or too long
        return False
    if re.search(r'\d{4}', sentence):  # Contains year
        return True
    if any(word in sentence.lower() for word in ['là', 'được', 'bao gồm', 'gồm', 'cách', 'phương pháp', 'quy trình', 'tại sao', 'lý do', 'nguyên nhân']):
        return True
    return False

def generate_basic_questions(text):
    # Split text into paragraphs
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    
    questions = []
    for paragraph in paragraphs:
        if len(paragraph) < 10:  # Skip very short paragraphs
            continue
            
        # Basic question patterns
        if paragraph.startswith('Title:'):
            title = paragraph.replace('Title:', '').strip()
            if title and len(title) > 10:
                questions.append(f"Nội dung chính của {title} là gì?")
        elif 'URL:' in paragraph:
            continue  # Skip URL questions
        elif 'Table' in paragraph or 'Row' in paragraph:
            continue  # Skip table questions as they're too generic
        else:
            # Generate questions from content
            sentences = [s.strip() for s in re.split('[.!?]', paragraph) if s.strip()]
            for sentence in sentences:
                sentence = clean_sentence(sentence)
                if not is_good_sentence(sentence):
                    continue
                    
                # Generate different types of questions based on content
                if re.search(r'\d{4}', sentence):  # Contains year - likely an event
                    questions.append(f"Điều gì đã xảy ra trong {sentence}?")
                elif any(keyword in sentence.lower() for keyword in ['là', 'được', 'bao gồm', 'gồm']):
                    questions.append(f"Hãy giải thích: {sentence}?")
                elif any(keyword in sentence.lower() for keyword in ['cách', 'phương pháp', 'quy trình']):
                    questions.append(f"Làm thế nào để {sentence}?")
                elif any(keyword in sentence.lower() for keyword in ['tại sao', 'lý do', 'nguyên nhân']):
                    questions.append(f"Tại sao {sentence}?")
                else:
                    # Create a more natural question
                    sentence = re.sub(r'^(Các|Những|Theo|Về|Đối với)\s+', '', sentence)
                    questions.append(f"Cho biết {sentence.lower()}?")
    
    # Remove duplicates and sort
    questions = list(set(questions))
    questions.sort()
    return questions

def main():
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Get all text files in data directory
    text_files = glob.glob('data/*.txt')
    
    all_questions = []
    
    # Process each file
    for file_path in text_files:
        print(f"Processing {file_path}...")
        text = load_text_file(file_path)
        questions = generate_basic_questions(text)
        all_questions.extend(questions)
    
    # Remove duplicates and sort all questions
    all_questions = list(set(all_questions))
    all_questions.sort()
    
    # Write all questions to a single file
    output_path = 'output/questions.txt'
    with open(output_path, 'w', encoding='utf-8') as f:
        for question in all_questions:
            f.write(question + '\n')
    
    print(f"Generated {len(all_questions)} questions in {output_path}")

if __name__ == "__main__":
    main() 