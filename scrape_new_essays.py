#!/usr/bin/env python3
"""
Script to automatically scrape Paul Graham's website for new essays.
This script will:
1. Fetch the list of essays from Paul Graham's website
2. Compare it with the existing essays in our repository
3. Download any new essays and convert them to markdown format
4. Add them to the essays directory
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
    """Get a list of existing essays from the essays.csv file."""
    existing_essays = {}
    
    if os.path.exists(ESSAYS_CSV):
        try:
            df = pd.read_csv(ESSAYS_CSV)
            for _, row in df.iterrows():
                url = row.get('URL', '')
                if url:
                    existing_essays[url] = {
                        'Article no.': row.get('Article no.', ''),
                        'Title': row.get('Title', ''),
                        'Date': row.get('Date', '')
                    }
        except Exception as e:
            print(f"Error reading existing essays CSV: {e}")
    
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

def fetch_essay_content(url):
    """Fetch the content of an essay from the given URL."""
    headers = {"User-Agent": USER_AGENT}
    
    try:
        # Add a random delay to avoid being blocked
        time.sleep(random.uniform(1, 3))
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to find the date
        date = ""
        text = soup.get_text()
        date_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}', text)
        if date_match:
            date = date_match.group(0)
        
        # Extract the main content
        # This is a bit tricky as Paul Graham's site doesn't have consistent structure
        # We'll try to get the main content by finding the largest text block
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
    """Save an essay to the essays directory and update the CSV."""
    # Create a filename from the article number and title
    safe_title = re.sub(r'[^\w\s]', '', title).replace(' ', '_').lower()
    filename = f"{article_no}_{safe_title}.md"
    filepath = os.path.join(ESSAYS_DIR, filename)
    
    # Add title and metadata to the markdown content
    full_content = f"# {article_no} {title}\n\n{content}"
    
    # Save the markdown file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_content)
    
    print(f"Saved essay: {title} to {filepath}")
    
    return filename

def update_essays_csv(new_essays):
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
                
            # Format the article number with leading zeros
            article_no = f"{next_article_no:03d}"
            
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
    print(f"Found {len(existing_essays)} existing essays")
    
    # Fetch the list of essays from Paul Graham's website
    essays = fetch_essay_list()
    print(f"Found {len(essays)} essays on Paul Graham's website")
    
    # Find new essays
    new_essays = []
    for essay in essays:
        if essay['url'] not in existing_essays:
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
        update_essays_csv(new_essays)
        print(f"Added {len(new_essays)} new essays")
    else:
        print("No new essays found")
    
    print(f"Finished essay scraping at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
