import os
import random

# Read all questions from the file
with open('output/questions.txt', 'r', encoding='utf-8') as f:
    questions = f.readlines()

# Calculate the split
total_questions = len(questions)
train_size = int(0.8 * total_questions)

# Randomly shuffle the questions
random.seed(42)  # For reproducibility
random.shuffle(questions)

# Split into train and test sets
train_questions = questions[:train_size]
test_questions = questions[train_size:]

# Create directories if they don't exist
os.makedirs('data_train', exist_ok=True)
os.makedirs('data_test', exist_ok=True)

# Write the splits to files
with open('data_train/questions.txt', 'w', encoding='utf-8') as f:
    f.writelines(train_questions)

with open('data_test/questions.txt', 'w', encoding='utf-8') as f:
    f.writelines(test_questions)

print(f"Total questions: {total_questions}")
print(f"Training set size: {len(train_questions)}")
print(f"Test set size: {len(test_questions)}") 