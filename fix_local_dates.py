#!/usr/bin/env python3
"""
Script to fix dates in essays.csv by reading local markdown files.
This script will:
1. Read the essays.csv file
2. For each essay, read the corresponding markdown file
3. Extract the date from the markdown content
4. Update the date in the essays.csv file
"""

import os
import re
import pandas as pd
from datetime import datetime

# Constants
ESSAYS_DIR = "essays"
ESSAYS_CSV = os.path.join(ESSAYS_DIR, "essays.csv")

def extract_date_from_markdown(markdown_content):
    """Extract the date from the markdown content."""
    # First, try to find a standalone date line (like "March 2025")
    date_patterns = [
        # Standard month year format
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',
        # Abbreviated month format
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?\s+\d{4}',
        # Date with day format
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}',
    ]
    
    # First, look for dates at the beginning of the text (more likely to be the publication date)
    lines = markdown_content.split('\n')
    for i in range(min(10, len(lines))):  # Check first 10 lines
        line = lines[i].strip()
        for pattern in date_patterns:
            match = re.search(pattern, line)
            if match and len(line) < 30:  # Likely a standalone date line
                return standardize_date(match.group(0))
    
    # If not found in the first few lines, search the entire text
    for pattern in date_patterns:
        match = re.search(pattern, markdown_content)
        if match:
            # Verify this isn't a reference to another date in the content
            date_str = match.group(0)
            # Check if the date appears at the beginning of a line
            for line in lines:
                line = line.strip()
                if line.startswith(date_str) and len(line) < 30:
                    return standardize_date(date_str)
    
    # If still not found, look for any year that might be a publication date
    # This is a fallback and less reliable
    for i in range(min(10, len(lines))):
        line = lines[i].strip()
        year_match = re.search(r'\b(20\d{2}|19\d{2})\b', line)
        if year_match and len(line) < 30:
            return year_match.group(0)
    
    return ""

def standardize_date(date_str):
    """Standardize date format to 'Month Year'."""
    if not date_str:
        return ""
    
    # Handle abbreviated months
    month_map = {
        'Jan': 'January',
        'Feb': 'February',
        'Mar': 'March',
        'Apr': 'April',
        'Jun': 'June',
        'Jul': 'July',
        'Aug': 'August',
        'Sep': 'September',
        'Sept': 'September',
        'Oct': 'October',
        'Nov': 'November',
        'Dec': 'December'
    }
    
    # Replace abbreviated months
    for abbr, full in month_map.items():
        date_str = re.sub(r'\b' + abbr + r'\.?\b', full, date_str)
    
    # Remove day from "Month Day, Year" format
    date_str = re.sub(r'(\w+)\s+\d{1,2},\s+(\d{4})', r'\1 \2', date_str)
    
    # If only year, leave as is
    if re.match(r'^\d{4}$', date_str):
        return date_str
    
    return date_str

def is_suspicious_date(date_str):
    """Check if a date looks suspicious (e.g., future dates or missing month/year)."""
    if not date_str:
        return True
        
    # Standardize the date first
    date_str = standardize_date(date_str)

    # Check for future dates (beyond current year + 1)
    current_year = datetime.now().year
    match = re.search(r'\b(\d{4})\b', date_str)
    if match:
        year = int(match.group(1))
        if year > current_year + 1:
            return True

    # Check for missing month or year
    has_month = any(month in date_str for month in [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ])
    has_year = bool(re.search(r'\b\d{4}\b', date_str))
    
    # Check for "What to Do" essay with incorrect date (known issue)
    if "What to Do" in date_str and "May 2024" in date_str:
        return True

    return not (has_month and has_year)

def main():
    """Main function to fix essay dates."""
    print(f"Starting local date fixing at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check if the essays.csv file exists
    if not os.path.exists(ESSAYS_CSV):
        print(f"Error: {ESSAYS_CSV} does not exist")
        return

    # Read the essays.csv file
    df = pd.read_csv(ESSAYS_CSV)

    # Keep track of how many dates were updated
    updated_count = 0

    # First, identify essays with suspicious dates
    suspicious_essays = []
    for index, row in df.iterrows():
        current_date = row['Date']
        if is_suspicious_date(current_date):
            suspicious_essays.append((index, row))

    print(f"Found {len(suspicious_essays)} essays with suspicious dates")
    
    # Process all essays, but prioritize suspicious ones
    essays_to_process = suspicious_essays + [(i, row) for i, row in df.iterrows() if (i, row) not in suspicious_essays]
    
    for index, row in essays_to_process:
        article_no = row['Article no.']
        title = row['Title']
        current_date = row['Date']
        is_suspicious = (index, row) in suspicious_essays

        print(f"Processing essay {article_no} - {title}...")

        # Find the corresponding markdown file
        markdown_files = [f for f in os.listdir(ESSAYS_DIR) if f.startswith(f"{article_no}_") and f.endswith(".md")]
        
        if not markdown_files:
            print(f"  Warning: No markdown file found for essay {article_no}")
            continue
        
        markdown_file = os.path.join(ESSAYS_DIR, markdown_files[0])
        
        # Read the markdown file
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Extract the date
        new_date = extract_date_from_markdown(markdown_content)

        # Update the date if it's different and valid
        if new_date and new_date != current_date and not is_suspicious_date(new_date):
            print(f"  Updating date from '{current_date}' to '{new_date}'")
            df.at[index, 'Date'] = new_date
            updated_count += 1
        else:
            if not new_date:
                print(f"  Could not extract date from essay")
            elif is_suspicious_date(new_date):
                print(f"  Extracted date '{new_date}' is still suspicious")
            else:
                print(f"  Date unchanged: '{current_date}'")

    # Save the updated DataFrame to CSV
    df.to_csv(ESSAYS_CSV, index=False)

    print(f"Finished local date fixing at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Updated {updated_count} essay dates")

if __name__ == "__main__":
    main()
