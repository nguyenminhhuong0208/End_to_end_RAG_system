import os
import random

# Read all answers from the file
with open('output/reference_answer.txt', 'r', encoding='utf-8') as f:
    answers = f.read().strip().split('\n\n')  # Split by double newlines to separate answers

# Calculate the split
total_answers = len(answers)
train_size = int(0.8 * total_answers)

# Randomly shuffle the answers
random.seed(42)  # For reproducibility
random.shuffle(answers)

# Split into train and test sets
train_answers = answers[:train_size]
test_answers = answers[train_size:]

# Create directories if they don't exist
os.makedirs('data_train', exist_ok=True)
os.makedirs('data_test', exist_ok=True)

# Write the splits to files
with open('data_train/reference_answers.txt', 'w', encoding='utf-8') as f:
    f.write('\n\n'.join(train_answers))

with open('data_test/reference_answers.txt', 'w', encoding='utf-8') as f:
    f.write('\n\n'.join(test_answers))

print(f"Total answers: {total_answers}")
print(f"Training set size: {len(train_answers)}")
print(f"Test set size: {len(test_answers)}") 