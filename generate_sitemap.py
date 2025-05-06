import os
import csv
from datetime import datetime

# Define paths
essays_dir = 'essays'
output_file = 'sitemap.xml'

# Get the current date in YYYY-MM-DD format
current_date = datetime.now().strftime('%Y-%m-%d')

# Read the CSV file to get essay metadata
essays_metadata = {}
csv_file = os.path.join(essays_dir, 'essays.csv')
if os.path.exists(csv_file):
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            essay_number = row.get('Article no.', '')
            essays_metadata[essay_number] = {
                'title': row.get('Title', ''),
                'date': row.get('Date', ''),
                'url': row.get('URL', '')
            }

# Create the sitemap XML
sitemap_header = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://paulgramessays.netlify.app/</loc>
    <lastmod>{date}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://paulgramessays.netlify.app/essays.html</loc>
    <lastmod>{date}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://paulgramessays.netlify.app/download.html</loc>
    <lastmod>{date}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://paulgramessays.netlify.app/about.html</loc>
    <lastmod>{date}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>'''.format(date=current_date)

sitemap_footer = '''</urlset>'''

# Process each essay file
essay_urls = []
for filename in os.listdir(essays_dir):
    if filename.endswith('.md') and not filename == 'essays.csv':
        # Extract essay number and slug from filename
        parts = filename.split('_', 1)
        if len(parts) == 2:
            essay_number = parts[0]
            essay_slug = parts[1].replace('.md', '')
            
            # Create the URL entry
            essay_url = f'''  <url>
    <loc>https://paulgramessays.netlify.app/essays/{essay_slug}.html</loc>
    <lastmod>{current_date}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>'''
            
            essay_urls.append(essay_url)

# Write the sitemap file
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(sitemap_header)
    for url in essay_urls:
        f.write('\n' + url)
    f.write('\n' + sitemap_footer)

print(f"Generated sitemap with {len(essay_urls)} essay URLs")
