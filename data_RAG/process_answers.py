import os
import glob
import re

def load_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def clean_text(text):
    # Remove course codes and English translations
    text = re.sub(r'[A-Z]{2,}[0-9]{4}.*?(?=[A-Z]{2,}[0-9]{4}|$)', '', text)
    text = re.sub(r'\s+[A-Z][a-z]+.*?(?=[A-Z]|$)', '', text)
    text = re.sub(r'[VIX]+\.[0-9.]+\s*[A-Za-z].*?(?=[VIX]+\.|$)', '', text)
    text = re.sub(r'\s*\([^)]*\)', '', text)  # Remove content in parentheses
    
    # Remove special characters except Vietnamese diacritics
    text = re.sub(r'[^\w\s\.,áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴĐ]', ' ', text)
    
    # Fix Vietnamese typos
    text = re.sub(r'(?<=\s)va\s', 'và ', text)
    text = re.sub(r'(?<=\s)cac\s', 'các ', text)
    text = re.sub(r'(?<=\s)vê\s', 'về ', text)
    text = re.sub(r'(?<=\s)vơ i\s', 'với ', text)
    text = re.sub(r'(?<=\s)co\s', 'có ', text)
    text = re.sub(r'(?<=\s)ca c\s', 'các ', text)
    text = re.sub(r'(?<=\s)sa n\s', 'sản ', text)
    text = re.sub(r'(?<=\s)phâ m\s', 'phẩm ', text)
    text = re.sub(r'(?<=\s)công nghê\s', 'công nghệ ', text)
    text = re.sub(r'(?<=\s)kiê n\s', 'kiến ', text)
    text = re.sub(r'(?<=\s)thư c\s', 'thực ', text)
    text = re.sub(r'(?<=\s)vâ t\s', 'vật ', text)
    text = re.sub(r'(?<=\s)nă m\s', 'nắm ', text)
    text = re.sub(r'(?<=\s)vư ng\s', 'vững ', text)
    text = re.sub(r'(?<=\s)đê n\s', 'đến ', text)
    text = re.sub(r'(?<=\s)hơ p\s', 'hợp ', text)
    text = re.sub(r'(?<=\s)ti c\s', 'tích ', text)
    text = re.sub(r'(?<=\s)truyê n\s', 'truyền ', text)
    text = re.sub(r'(?<=\s)thô ng\s', 'thông ', text)
    text = re.sub(r'(?<=\s)nhu ng\s', 'nhúng ', text)
    text = re.sub(r'(?<=\s)lươ ng\s', 'lường ', text)
    text = re.sub(r'(?<=\s)tư vâ n\s', 'tư vấn ', text)
    text = re.sub(r'(?<=\s)thiê t\s', 'thiết ', text)
    text = re.sub(r'(?<=\s)kê\s', 'kế ', text)
    text = re.sub(r'\s+', ' ', text)  # Normalize spaces
    
    # Remove leading/trailing punctuation and spaces
    text = re.sub(r'^[\s\.,]+|[\s\.,]+$', '', text)
    
    return text

def is_good_answer(text):
    # Check if text is meaningful
    if len(text.split()) < 5:  # Too few words
        return False
    if len(text) < 30 or len(text) > 200:  # Too short or too long
        return False
    if text.count('(') != text.count(')'):  # Unmatched parentheses
        return False
    if any(char in text for char in ['*', '#', '@', '$', '^', '&', '/']):  # Contains special characters
        return False
    if re.match(r'^\d+\s*(tín chỉ|TC)$', text):  # Just credit numbers
        return False
    if text.count(',') > 5:  # Too many commas - likely a list
        return False
    if re.search(r'[A-Z]{2,}', text):  # Contains uppercase English words
        return False
    if re.search(r'\d+\s*\d+\s*\d+', text):  # Contains sequences of numbers
        return False
    if re.search(r'[VIX]+\.[0-9.]+', text):  # Contains section numbers
        return False
    if re.search(r'x\s*x\s*x', text):  # Contains x x x patterns
        return False
    if text.count('.') > 3:  # Too many periods - likely multiple sentences
        return False
    if re.search(r'[A-Za-z]{3,}', text):  # Contains English words
        return False
    if re.search(r'^\d+\s+\w+', text):  # Starts with number
        return False
    if len(re.findall(r'\d+', text)) > 2:  # Contains too many numbers
        return False
    return True

def extract_key_info(text):
    # List to store extracted information
    info = []
    
    # Split text into paragraphs
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    
    for paragraph in paragraphs:
        # Skip very short paragraphs
        if len(paragraph) < 30:
            continue
            
        # Extract information after ":" if present
        if ':' in paragraph and not re.search(r'https?://', paragraph):
            parts = paragraph.split(':', 1)
            if len(parts) == 2 and len(parts[1].strip()) > 0:
                cleaned = clean_text(parts[1])
                if is_good_answer(cleaned):
                    info.append(cleaned)
            continue
            
        # Split into sentences
        sentences = [s.strip() for s in re.split('[.!?]', paragraph) if s.strip()]
        
        for sentence in sentences:
            sentence = clean_text(sentence)
            if not is_good_answer(sentence):
                continue
                
            # Extract key information
            if re.search(r'\d{4}', sentence) and len(sentence) < 150:  # Contains year
                info.append(sentence)
            elif re.search(r'\d+([,.]\d+)?%', sentence) and len(sentence) < 150:  # Contains percentage
                info.append(sentence)
            else:
                # Extract information after key words
                key_words = ['là', 'được', 'bao gồm', 'gồm', 'có', 'nhằm', 'giúp', 'phải', 'cần', 'để']
                for word in key_words:
                    if ' ' + word + ' ' in sentence.lower():
                        parts = sentence.lower().split(' ' + word + ' ', 1)
                        if len(parts) == 2 and len(parts[1].strip()) > 0:
                            cleaned = clean_text(parts[1])
                            if is_good_answer(cleaned):
                                info.append(cleaned)
                        break
    
    # Clean up the extracted information
    cleaned_info = []
    for item in info:
        # Remove common prefixes
        item = re.sub(r'^(các|những|theo|về|đối với|trong đó|nhằm|để|phải|cần|có thể|sẽ)\s+', '', item, flags=re.IGNORECASE)
        # Only keep if item is meaningful
        if is_good_answer(item):
            cleaned_info.append(item)
    
    return list(set(cleaned_info))  # Remove duplicates

def main():
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Get all text files in data directory
    text_files = glob.glob('data/*.txt')
    
    all_info = []
    
    # Process each file
    for file_path in text_files:
        print(f"Processing {file_path}...")
        text = load_text_file(file_path)
        info = extract_key_info(text)
        all_info.extend(info)
    
    # Remove duplicates and sort
    all_info = list(set(all_info))
    # Sort by length to prioritize shorter answers
    all_info.sort(key=len)
    
    # Write all information to a single file
    output_path = 'output/reference_answers.txt'
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in all_info:
            f.write(item + '\n')
    
    print(f"Generated {len(all_info)} answers in {output_path}")

if __name__ == "__main__":
    main() 