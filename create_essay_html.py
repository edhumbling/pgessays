#!/usr/bin/env python3
"""
Script to create HTML files for each essay using the template.
This script will:
1. Read the essays.csv file
2. For each essay, read the corresponding markdown file
3. Convert the markdown to HTML
4. Insert the HTML into the template
5. Save the HTML file
"""

import os
import re
import csv
import json
import markdown
import pandas as pd
from datetime import datetime, timedelta
from jinja2 import Template

# Constants
ESSAYS_DIR = "essays"
ESSAYS_CSV = os.path.join(ESSAYS_DIR, "essays.csv")
TEMPLATE_FILE = os.path.join("templates", "essay_template.html")
OUTPUT_DIR = "."
CATEGORIES_FILE = os.path.join(ESSAYS_DIR, "categories.json")

def read_template():
    """Read the template file."""
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def read_categories():
    """Read the categories file."""
    try:
        with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading categories file: {e}")
        return {"categories": [], "essayTags": {}}

def convert_markdown_to_html(markdown_content):
    """Convert markdown to HTML."""
    # Use Python-Markdown to convert markdown to HTML
    html = markdown.markdown(markdown_content, extensions=['extra'])
    return html

def create_slug(title):
    """Create a slug from the title."""
    # Convert to lowercase
    slug = title.lower()
    # Replace all special characters with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    # Remove leading and trailing hyphens
    slug = slug.strip('-')
    # Replace multiple hyphens with a single hyphen
    slug = re.sub(r'-+', '-', slug)
    return slug

def get_essay_categories(essay_id, categories_data):
    """Get categories for an essay."""
    essay_tags = categories_data.get("essayTags", {})
    return essay_tags.get(str(essay_id), [])

def get_category_name(category_id, categories_data):
    """Get category name from ID."""
    for category in categories_data.get("categories", []):
        if category.get("id") == category_id:
            return category.get("name")
    return category_id.replace("-", " ").title()

def main():
    """Main function to create HTML files."""
    print(f"Starting HTML creation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Read the template
    template_content = read_template()
    template = Template(template_content)
    
    # Read categories
    categories_data = read_categories()
    
    # Check if the essays.csv file exists
    if not os.path.exists(ESSAYS_CSV):
        print(f"Error: {ESSAYS_CSV} does not exist")
        return
    
    # Read the essays.csv file
    df = pd.read_csv(ESSAYS_CSV)
    
    # Sort essays by article number
    df = df.sort_values(by='Article no.', ascending=True)
    
    # Calculate which essays are new (added in the last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    # Process each essay
    for i, row in df.iterrows():
        article_no = row['Article no.']
        title = row['Title']
        date = row['Date']
        url = row['URL']
        
        print(f"Processing essay {article_no}: {title}")
        
        # Find the corresponding markdown file
        markdown_files = [f for f in os.listdir(ESSAYS_DIR) if f.startswith(f"{article_no}_") and f.endswith(".md")]
        
        if not markdown_files:
            print(f"  Warning: No markdown file found for essay {article_no}")
            continue
        
        markdown_file = os.path.join(ESSAYS_DIR, markdown_files[0])
        
        # Read the markdown file
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Convert markdown to HTML
        html_content = convert_markdown_to_html(markdown_content)
        
        # Create slug for the output file
        slug = create_slug(title)
        output_file = os.path.join(OUTPUT_DIR, f"{slug}.html")
        
        # Check if this is a new essay
        is_new = False
        try:
            essay_date = datetime.strptime(date, "%B %Y")
            is_new = essay_date > thirty_days_ago
        except:
            pass
        
        # Get previous and next essays
        prev_essay = None
        next_essay = None
        
        current_index = df[df['Article no.'] == article_no].index[0]
        
        if current_index > 0:
            prev_row = df.iloc[current_index - 1]
            prev_essay = {
                'title': prev_row['Title'],
                'url': f"/{create_slug(prev_row['Title'])}.html"
            }
        
        if current_index < len(df) - 1:
            next_row = df.iloc[current_index + 1]
            next_essay = {
                'title': next_row['Title'],
                'url': f"/{create_slug(next_row['Title'])}.html"
            }
        
        # Get categories for this essay
        category_ids = get_essay_categories(article_no, categories_data)
        categories = [get_category_name(cat_id, categories_data) for cat_id in category_ids]
        
        # Render the template
        html_output = template.render(
            article_no=article_no,
            title=title,
            date=date,
            content=html_content,
            is_new=is_new,
            prev_essay=prev_essay,
            next_essay=next_essay,
            categories=categories,
            tags=category_ids
        )
        
        # Save the HTML file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_output)
        
        print(f"  Created {output_file}")
    
    print(f"Finished HTML creation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
