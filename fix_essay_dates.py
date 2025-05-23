#!/usr/bin/env python3
"""
Script to fix the dates in the existing essays.
This script will:
1. Check each essay in the essays.csv file
2. Fetch the original essay from Paul Graham's website
3. Extract the date directly from the essay page
4. Update the date in the essays.csv file
"""

import os
import re
import time
import random
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# Constants
ESSAYS_DIR = "essays"
ESSAYS_CSV = os.path.join(ESSAYS_DIR, "essays.csv")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

def extract_date_from_essay(content):
    """Extract the date from the essay content more accurately."""
    soup = BeautifulSoup(content, 'html.parser')

    # Look for a date pattern in the text
    text = soup.get_text()

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
    first_paragraph = text.split('\n')[0]
    for pattern in date_patterns:
        match = re.search(pattern, first_paragraph)
        if match:
            return standardize_date(match.group(0))

    # If not found in the first paragraph, search the entire text
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            # Verify this isn't a reference to another date in the content
            date_str = match.group(0)
            # Check if the date appears at the beginning of a paragraph or after a newline
            date_pos = text.find(date_str)
            if date_pos > 0:
                prev_char = text[date_pos-1]
                if prev_char in ['\n', '.', '!', '?']:
                    return standardize_date(date_str)
            else:
                return standardize_date(date_str)

    # If still not found, look for any year that might be a publication date
    # This is a fallback and less reliable
    year_match = re.search(r'\b(20\d{2}|19\d{2})\b', text[:500])  # Look only in first 500 chars
    if year_match:
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

def fetch_essay_date(url):
    """Fetch the date of an essay from the given URL."""
    headers = {"User-Agent": USER_AGENT}

    try:
        # Add a small delay to avoid being blocked (reduced from previous version)
        time.sleep(random.uniform(0.2, 0.5))

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Extract the date from the essay content
        date = extract_date_from_essay(response.text)

        return date

    except Exception as e:
        print(f"Error fetching essay date from {url}: {e}")
        return ""

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
    print(f"Starting date fixing at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

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
        url = row['URL']
        current_date = row['Date']
        is_suspicious = (index, row) in suspicious_essays

        print(f"Processing essay {row['Article no.']} - {row['Title']}...")

        # Fetch the date from the essay page
        new_date = fetch_essay_date(url)

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

        # Add a small delay between requests to avoid being blocked
        time.sleep(random.uniform(0.5, 1.0))

    # Save the updated DataFrame to CSV
    df.to_csv(ESSAYS_CSV, index=False)

    print(f"Finished date fixing at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Updated {updated_count} essay dates")

if __name__ == "__main__":
    main()
