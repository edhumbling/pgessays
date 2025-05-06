#!/usr/bin/env python3
"""
Script to automatically categorize Paul Graham essays based on content analysis.
This script will:
1. Read all essays from the essays directory
2. Analyze the content to determine categories
3. Update the essays.csv file with category information
4. Generate tags for each essay
"""

import os
import re
import csv
import pandas as pd
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

# Constants
ESSAYS_DIR = "essays"
ESSAYS_CSV = os.path.join(ESSAYS_DIR, "essays.csv")

# Categories with their associated keywords
CATEGORIES = {
    "Startups": [
        "startup", "founder", "vc", "venture", "capital", "investor", "funding", 
        "company", "business", "entrepreneur", "silicon", "valley", "y combinator",
        "yc", "incubator", "seed", "round", "series", "growth", "scale", "product",
        "market", "customer", "revenue", "profit", "exit", "acquisition", "ipo"
    ],
    "Programming": [
        "programming", "code", "software", "developer", "engineer", "language", 
        "lisp", "python", "java", "javascript", "web", "algorithm", "data", 
        "structure", "function", "object", "class", "method", "api", "framework",
        "library", "bug", "debug", "compiler", "interpreter", "syntax", "semantic"
    ],
    "Life & Philosophy": [
        "life", "philosophy", "meaning", "purpose", "happiness", "wisdom", "truth",
        "knowledge", "belief", "mind", "consciousness", "ethics", "moral", "value",
        "virtue", "good", "evil", "right", "wrong", "justice", "freedom", "society",
        "culture", "art", "beauty", "love", "friendship", "family", "education"
    ],
    "Work & Productivity": [
        "work", "productivity", "career", "job", "profession", "skill", "talent",
        "expertise", "mastery", "practice", "habit", "discipline", "focus", 
        "attention", "distraction", "procrastination", "efficiency", "effectiveness",
        "goal", "achievement", "success", "failure", "learning", "improvement"
    ],
    "Writing & Communication": [
        "writing", "essay", "book", "author", "reader", "audience", "communication",
        "language", "word", "sentence", "paragraph", "grammar", "style", "rhetoric",
        "persuasion", "argument", "idea", "concept", "metaphor", "analogy", "story",
        "narrative", "dialogue", "conversation", "speech", "presentation"
    ]
}

def setup_nltk():
    """Download necessary NLTK data."""
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('punkt')
        nltk.download('stopwords')

def read_essay_content(file_path):
    """Read the content of an essay file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def preprocess_text(text):
    """Preprocess text for analysis."""
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words and len(word) > 2]
    
    return tokens

def categorize_essay(content):
    """Determine the category of an essay based on its content."""
    tokens = preprocess_text(content)
    
    # Count occurrences of category keywords
    category_scores = {}
    for category, keywords in CATEGORIES.items():
        score = sum(1 for token in tokens if token in keywords)
        # Normalize by the number of keywords in the category
        category_scores[category] = score / len(keywords) if keywords else 0
    
    # Get the category with the highest score
    if category_scores:
        primary_category = max(category_scores.items(), key=lambda x: x[1])[0]
        
        # Get secondary categories (at least 50% of the primary category's score)
        primary_score = category_scores[primary_category]
        secondary_categories = [
            cat for cat, score in category_scores.items()
            if cat != primary_category and score >= 0.5 * primary_score
        ]
        
        return primary_category, secondary_categories
    
    return "Uncategorized", []

def generate_tags(content, primary_category, secondary_categories):
    """Generate tags for an essay based on its content and categories."""
    tokens = preprocess_text(content)
    
    # Get the most common words (excluding very common words)
    word_counts = Counter(tokens)
    common_words = [word for word, count in word_counts.most_common(20) if count > 1]
    
    # Add category keywords that appear in the content
    category_keywords = set()
    for category in [primary_category] + secondary_categories:
        if category in CATEGORIES:
            for keyword in CATEGORIES[category]:
                if keyword in content.lower() and keyword not in category_keywords:
                    category_keywords.add(keyword)
    
    # Combine and limit to 10 tags
    tags = list(set(common_words + list(category_keywords)))[:10]
    
    return tags

def update_essays_csv(essays_data):
    """Update the essays.csv file with category and tag information."""
    try:
        df = pd.read_csv(ESSAYS_CSV)
        
        # Add or update category and tags columns
        for essay_number, data in essays_data.items():
            idx = df[df['Article no.'] == essay_number].index
            if not idx.empty:
                df.loc[idx, 'Category'] = data['category']
                df.loc[idx, 'Secondary Categories'] = data['secondary_categories']
                df.loc[idx, 'Tags'] = data['tags']
        
        # Save the updated DataFrame
        df.to_csv(ESSAYS_CSV, index=False)
        print(f"Updated {ESSAYS_CSV} with categories and tags")
        
    except Exception as e:
        print(f"Error updating CSV: {e}")

def main():
    """Main function to categorize essays and update the CSV."""
    print("Starting essay categorization...")
    
    # Setup NLTK
    setup_nltk()
    
    # Ensure the essays directory exists
    if not os.path.exists(ESSAYS_DIR):
        print(f"Error: {ESSAYS_DIR} directory not found")
        return
    
    # Process each essay file
    essays_data = {}
    for filename in os.listdir(ESSAYS_DIR):
        if filename.endswith('.md') and not filename == 'essays.csv':
            file_path = os.path.join(ESSAYS_DIR, filename)
            
            # Extract essay number from filename
            match = re.match(r'(\d+)_', filename)
            if match:
                essay_number = match.group(1)
                
                print(f"Processing essay {essay_number}: {filename}")
                
                # Read and analyze the content
                content = read_essay_content(file_path)
                if content:
                    primary_category, secondary_categories = categorize_essay(content)
                    tags = generate_tags(content, primary_category, secondary_categories)
                    
                    essays_data[essay_number] = {
                        'category': primary_category,
                        'secondary_categories': ', '.join(secondary_categories),
                        'tags': ', '.join(tags)
                    }
                    
                    print(f"  Category: {primary_category}")
                    print(f"  Secondary: {secondary_categories}")
                    print(f"  Tags: {tags}")
    
    # Update the CSV file
    if essays_data:
        update_essays_csv(essays_data)
    
    print("Essay categorization complete!")

if __name__ == "__main__":
    main()
