#!/usr/bin/env python3
"""
Improved script to automatically scrape Paul Graham's website for new essays.
This script will:
1. Check the existing essays in our repository
2. Only fetch new essays from Paul Graham's website
3. Extract dates directly from the essay pages for accuracy
4. Add new essays to the essays directory
5. Update the essays.csv file with the new essay metadata
"""

import os
import re
import csv
import time
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import html2text
import pandas as pd
from datetime import datetime

# Constants
PG_ARTICLES_URL = "http://www.paulgraham.com/articles.html"
ESSAYS_DIR = "essays"
ESSAYS_CSV = os.path.join(ESSAYS_DIR, "essays.csv")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

def setup_directories():
    """Ensure the essays directory exists."""
    os.makedirs(ESSAYS_DIR, exist_ok=True)

def get_existing_essays():
    """Get the list of existing essays from the essays.csv file."""
    existing_essays = {}

    if os.path.exists(ESSAYS_CSV):
        try:
            df = pd.read_csv(ESSAYS_CSV)
            for _, row in df.iterrows():
                existing_essays[row['URL']] = {
                    'article_no': row['Article no.'],
                    'title': row['Title'],
                    'date': row['Date']
                }
            print(f"Found {len(existing_essays)} existing essays in {ESSAYS_CSV}")
        except Exception as e:
            print(f"Error reading {ESSAYS_CSV}: {e}")

    return existing_essays

def fetch_essay_list():
    """Fetch the list of essays from Paul Graham's website."""
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(PG_ARTICLES_URL, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all links in the page
        links = soup.find_all('a')

        essays = []
        for link in links:
            href = link.get('href')
            title = link.get_text().strip()

            # Skip empty links or non-essay links
            if not href or not title or href.startswith('#') or href.startswith('mailto:'):
                continue

            # Convert relative URLs to absolute
            url = urljoin(PG_ARTICLES_URL, href)

            # Only include links to paulgraham.com essays
            if 'paulgraham.com' in url and title:
                essays.append({
                    'title': title,
                    'url': url
                })

        return essays

    except Exception as e:
        print(f"Error fetching essay list: {e}")
        return []

def extract_date_from_essay(content):
    """Extract the date from the essay content more accurately."""
    soup = BeautifulSoup(content, 'html.parser')

    # Look for a date pattern in the text
    text = soup.get_text()

    # First, try to find a standalone date line (like "March 2025")
    date_patterns = [
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',
    ]

    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)

    return ""

def fetch_essay_content(url):
    """Fetch the content of an essay from the given URL."""
    headers = {"User-Agent": USER_AGENT}

    try:
        # Add a small delay to avoid being blocked (reduced from previous version)
        time.sleep(random.uniform(0.2, 0.5))

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

        return {
            'content': markdown_content,
            'date': date
        }

    except Exception as e:
        print(f"Error fetching essay content from {url}: {e}")
        return {'content': '', 'date': ''}

def save_essay(title, url, content, date, article_no):
    """Save an essay to a file."""
    # Create a filename from the title
    filename = title.lower()
    filename = re.sub(r'[^\w\s]', '', filename)  # Remove punctuation
    filename = re.sub(r'\s+', '_', filename)     # Replace spaces with underscores

    # Add the article number as a prefix
    filename = f"{article_no}_{filename}.md"

    # Save the essay
    filepath = os.path.join(ESSAYS_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {article_no} {title}\n\n")
        if date:
            f.write(f"{date}\n\n")
        f.write(content)

    print(f"Saved essay to {filepath}")

def update_essays_csv(new_essays, existing_essays):
    """Update the essays.csv file with new essays."""
    # Read existing CSV if it exists
    if os.path.exists(ESSAYS_CSV):
        df = pd.read_csv(ESSAYS_CSV)
    else:
        # Create a new DataFrame with the required columns
        df = pd.DataFrame(columns=['Article no.', 'Title', 'Date', 'URL'])

    # Add new essays to the DataFrame
    for essay in new_essays:
        # Check if the essay already exists in the DataFrame
        if not df['URL'].str.contains(essay['url']).any():
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

    # Save the updated DataFrame to CSV
    df.to_csv(ESSAYS_CSV, index=False)

    print(f"Updated {ESSAYS_CSV} with {len(new_essays)} new essays")

def main():
    """Main function to scrape new essays."""
    print(f"Starting essay scraping at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Ensure the essays directory exists
    setup_directories()

    # Get existing essays
    existing_essays = get_existing_essays()

    # Fetch the list of essays from Paul Graham's website
    essays = fetch_essay_list()
    print(f"Found {len(essays)} essays on Paul Graham's website")

    # Paul Graham's essays are listed with the newest first
    # So we can stop as soon as we find an essay we already have
    new_essays = []
    for essay in essays:
        if essay['url'] in existing_essays:
            print(f"Found existing essay: {essay['title']} - stopping search")
            break

        print(f"Found new essay: {essay['title']} ({essay['url']})")

        # Fetch the content of the new essay
        content_data = fetch_essay_content(essay['url'])

        if content_data['content']:
            new_essays.append({
                'title': essay['title'],
                'url': essay['url'],
                'content': content_data['content'],
                'date': content_data['date']
            })

    print(f"Found {len(new_essays)} new essays")

    # Update the essays.csv file with new essays
    if new_essays:
        update_essays_csv(new_essays, existing_essays)
        print(f"Added {len(new_essays)} new essays")
    else:
        print("No new essays found")

    print(f"Finished essay scraping at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
