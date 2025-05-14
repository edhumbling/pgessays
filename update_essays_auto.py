#!/usr/bin/env python3
"""
Automated script to check for new Paul Graham essays and update the repository.
This script will:
1. Check the existing essays in our repository
2. Check the latest essays on Paul Graham's website
3. Download and process any new essays
4. Update the essays.csv file with the new essays

This script is designed to be run by GitHub Actions on a weekly schedule.
"""

import os
import re
import csv
import time
import random
import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import html2text
import pandas as pd
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Constants
PG_ARTICLES_URL = "http://www.paulgraham.com/articles.html"
ESSAYS_DIR = "essays"
ESSAYS_CSV = os.path.join(ESSAYS_DIR, "essays.csv")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

def normalize_url(url):
    """
    Normalize URL for consistent comparison.
    This helps prevent duplicate essays due to URL variations.
    """
    if not url:
        return ""

    # Convert to lowercase
    url = url.lower()

    # Parse the URL
    parsed = urlparse(url)

    # Remove www. prefix from domain
    netloc = parsed.netloc.replace("www.", "")

    # Reconstruct the URL without protocol (http/https)
    normalized = f"{netloc}{parsed.path}"

    # Remove trailing slash if present
    normalized = normalized.rstrip('/')

    return normalized

def setup_directories():
    """Ensure the essays directory exists."""
    os.makedirs(ESSAYS_DIR, exist_ok=True)

def get_existing_essays():
    """Get the list of existing essays from the essays.csv file."""
    existing_essays = {}
    url_to_normalized = {}  # Map original URLs to normalized versions

    if os.path.exists(ESSAYS_CSV):
        try:
            df = pd.read_csv(ESSAYS_CSV)
            for _, row in df.iterrows():
                original_url = row['URL']
                normalized_url = normalize_url(original_url)

                # Store both the normalized URL and the original URL mapping
                existing_essays[normalized_url] = {
                    'article_no': row['Article no.'],
                    'title': row['Title'],
                    'date': row['Date'],
                    'original_url': original_url
                }
                url_to_normalized[original_url] = normalized_url

            logging.info(f"Found {len(existing_essays)} existing essays in {ESSAYS_CSV}")
        except Exception as e:
            logging.error(f"Error reading {ESSAYS_CSV}: {e}")

    return existing_essays, url_to_normalized

def fetch_essay_list():
    """Fetch the list of essays from Paul Graham's website."""
    headers = {"User-Agent": USER_AGENT}

    try:
        logging.info(f"Fetching essays from {PG_ARTICLES_URL}")
        response = requests.get(PG_ARTICLES_URL, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all links in the page
        links = soup.find_all('a')
        logging.info(f"Found {len(links)} links on the page")

        essays = []
        for link in links:
            href = link.get('href')
            title = link.get_text().strip()

            # Skip empty links or non-essay links
            if not href or not title or href.startswith('#') or href.startswith('mailto:'):
                continue

            # Convert relative URLs to absolute
            url = urljoin(PG_ARTICLES_URL, href)
            normalized_url = normalize_url(url)

            # Only include links to paulgraham.com essays
            if 'paulgraham.com' in url and title:
                essays.append({
                    'title': title,
                    'url': url,
                    'normalized_url': normalized_url
                })

        logging.info(f"Found {len(essays)} potential essays")
        return essays

    except Exception as e:
        logging.error(f"Error fetching essay list: {e}")
        return []

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

def is_valid_date(date_str):
    """Check if a date is valid (not in the future, has month and year)."""
    if not date_str:
        return False

    # Standardize the date first
    date_str = standardize_date(date_str)

    # Check for future dates (beyond current year + 1)
    current_year = datetime.now().year
    match = re.search(r'\b(\d{4})\b', date_str)
    if match:
        year = int(match.group(1))
        if year > current_year + 1:
            logging.warning(f"Found future date: {date_str}")
            return False

    # Check for missing month or year
    has_month = any(month in date_str for month in [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ])
    has_year = bool(re.search(r'\b\d{4}\b', date_str))

    return has_month and has_year

def extract_date_from_essay(content):
    """Extract the date from the essay content."""
    soup = BeautifulSoup(content, 'html.parser')

    # Look for a date pattern in the text
    text = soup.get_text()

    # Split into lines for better analysis
    lines = text.split('\n')

    # First, try to find a standalone date line (like "March 2025")
    date_patterns = [
        # Standard month year format
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',
        # Abbreviated month format
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?\s+\d{4}',
        # Date with day format
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}',
    ]

    # First, check the first 10 lines for a standalone date
    for i in range(min(10, len(lines))):
        line = lines[i].strip()
        for pattern in date_patterns:
            match = re.search(pattern, line)
            if match and len(line) < 30:  # Likely a standalone date line
                date_str = standardize_date(match.group(0))
                if is_valid_date(date_str):
                    logging.info(f"Found date in standalone line: {date_str}")
                    return date_str

    # Next, look for dates at the beginning of the text
    first_paragraph = text[:500]  # First 500 chars
    for pattern in date_patterns:
        match = re.search(pattern, first_paragraph)
        if match:
            date_str = standardize_date(match.group(0))
            if is_valid_date(date_str):
                logging.info(f"Found date in first paragraph: {date_str}")
                return date_str

    # If not found in the first paragraph, search the entire text
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            # Verify this isn't a reference to another date in the content
            date_str = standardize_date(match.group(0))
            if is_valid_date(date_str):
                # Check if the date appears at the beginning of a paragraph or after a newline
                date_pos = text.find(match.group(0))
                if date_pos > 0:
                    prev_char = text[date_pos-1]
                    if prev_char in ['\n', '.', '!', '?']:
                        logging.info(f"Found date in text: {date_str}")
                        return date_str
                else:
                    logging.info(f"Found date at start of text: {date_str}")
                    return date_str

    # If still not found, look for any year that might be a publication date
    # This is a fallback and less reliable
    year_match = re.search(r'\b(20\d{2}|19\d{2})\b', text[:500])  # Look only in first 500 chars
    if year_match:
        year = year_match.group(0)
        logging.warning(f"Could only find year: {year}")
        return year

    logging.warning("Could not extract date from essay")
    return ""

def fetch_essay_content(url):
    """Fetch the content of an essay from the given URL."""
    headers = {"User-Agent": USER_AGENT}

    try:
        # Add a small delay to avoid being blocked
        time.sleep(random.uniform(0.2, 0.5))

        logging.info(f"Fetching essay content from {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Extract the date from the essay content
        date = extract_date_from_essay(response.text)

        # Extract the main content
        soup = BeautifulSoup(response.text, 'html.parser')
        main_content = soup.find('body')

        # Convert HTML to markdown
        h2t = html2text.HTML2Text()
        h2t.ignore_links = False
        h2t.ignore_images = False
        h2t.ignore_tables = False
        markdown_content = h2t.handle(str(main_content))

        # Log success or warning based on date extraction
        if date:
            logging.info(f"Successfully extracted date: {date}")
        else:
            logging.warning(f"Could not extract date from {url}")

        return {
            'content': markdown_content,
            'date': date
        }

    except Exception as e:
        logging.error(f"Error fetching essay content from {url}: {e}")
        return {'content': '', 'date': ''}

def save_essay(title, url, content, date, article_no):
    """Save an essay to a file."""
    # Create a filename from the title
    filename = title.lower()
    filename = re.sub(r'[^\w\s]', '', filename)  # Remove punctuation
    filename = re.sub(r'\s+', '_', filename)     # Replace spaces with underscores

    # Add the article number as a prefix
    markdown_filename = f"{article_no}_{filename}.md"

    # Save the markdown version
    markdown_filepath = os.path.join(ESSAYS_DIR, markdown_filename)

    try:
        with open(markdown_filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {article_no} {title}\n\n")
            if date:
                f.write(f"{date}\n\n")
            f.write(content)

        logging.info(f"Successfully saved essay to {markdown_filepath}")
        return True
    except Exception as e:
        logging.error(f"Error saving essay to {markdown_filepath}: {e}")
        return False

def update_essays_csv(new_essays, existing_essays, url_to_normalized):
    """Update the essays.csv file with new essays."""
    # Read existing CSV if it exists
    if os.path.exists(ESSAYS_CSV):
        df = pd.read_csv(ESSAYS_CSV)
    else:
        # Create a new DataFrame with the required columns
        df = pd.DataFrame(columns=['Article no.', 'Title', 'Date', 'URL'])

    # Track how many essays were added
    added_count = 0

    # Add new essays to the DataFrame
    for essay in new_essays:
        normalized_url = essay['normalized_url']

        # Check if the essay already exists using normalized URL
        if normalized_url in existing_essays:
            logging.info(f"Essay already exists: {essay['title']} ({essay['url']})")
            continue

        # Double-check using the DataFrame to be extra safe
        if any(normalize_url(url) == normalized_url for url in df['URL']):
            logging.info(f"Essay already exists in DataFrame: {essay['title']} ({essay['url']})")
            continue

        # Get the next article number
        if len(df) > 0:
            next_article_no = int(df['Article no.'].max()) + 1
        else:
            next_article_no = 1

        # Format the article number
        article_no = str(next_article_no)

        # Add the essay to the DataFrame
        new_row = {
            'Article no.': article_no,
            'Title': essay['title'],
            'Date': essay['date'],
            'URL': essay['url']
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        # Save the essay content
        save_essay(essay['title'], essay['url'], essay['content'], essay['date'], article_no)

        logging.info(f"Added new essay: {essay['title']} ({essay['url']})")
        added_count += 1

    # Save the updated DataFrame to CSV
    df.to_csv(ESSAYS_CSV, index=False)

    logging.info(f"Updated {ESSAYS_CSV} with {added_count} new essays")

def main():
    """Main function to check for new essays."""
    logging.info(f"Starting essay check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Ensure the essays directory exists
    setup_directories()

    # Get existing essays
    existing_essays, url_to_normalized = get_existing_essays()

    # Fetch the list of essays from Paul Graham's website
    essays = fetch_essay_list()

    if not essays:
        logging.error("Error: Could not fetch essays from Paul Graham's website")
        return

    # Paul Graham's essays are listed with the newest first
    # We'll check a reasonable number of essays before stopping
    # This helps catch any essays that might have been missed in previous runs
    new_essays = []
    found_existing_count = 0
    max_existing_to_check = 5  # Check up to 5 existing essays before stopping

    for essay in essays:
        normalized_url = essay['normalized_url']

        # Check if this essay already exists
        if normalized_url in existing_essays:
            found_existing_count += 1
            logging.info(f"Found existing essay: {essay['title']} ({essay['url']})")

            # If we've found several existing essays in a row, we can stop
            if found_existing_count >= max_existing_to_check:
                logging.info(f"Found {found_existing_count} existing essays in a row - stopping search")
                break

            # Continue to the next essay
            continue

        logging.info(f"Found potential new essay: {essay['title']} ({essay['url']})")

        # Reset the counter since we found a new essay
        found_existing_count = 0

        # Fetch the content of the new essay
        content_data = fetch_essay_content(essay['url'])

        if content_data['content']:
            new_essays.append({
                'title': essay['title'],
                'url': essay['url'],
                'normalized_url': normalized_url,
                'content': content_data['content'],
                'date': content_data['date']
            })
        else:
            logging.warning(f"Could not fetch content for essay: {essay['title']} ({essay['url']})")

    # Update the essays.csv file with new essays
    if new_essays:
        update_essays_csv(new_essays, existing_essays, url_to_normalized)
        logging.info(f"Added {len(new_essays)} new essays")
    else:
        logging.info("No new essays found")

    logging.info(f"Finished essay check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
