import os
import re
import csv
import pypandoc
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Ensure pandoc is installed
try:
    pypandoc.get_pandoc_version()
except OSError:
    print("Pandoc not found. Downloading...")
    pypandoc.download_pandoc()
    print("Pandoc installed successfully.")

# Define paths
essays_dir = 'essays'
output_dir = 'downloads'
pdf_dir = os.path.join(output_dir, 'pdf')
epub_dir = os.path.join(output_dir, 'epub')
combined_dir = os.path.join(output_dir, 'combined')

# Create output directories if they don't exist
os.makedirs(pdf_dir, exist_ok=True)
os.makedirs(epub_dir, exist_ok=True)
os.makedirs(combined_dir, exist_ok=True)

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

# LaTeX template for better PDF formatting
latex_template = r"""
\documentclass[12pt, letterpaper]{article}
\usepackage[utf8]{inputenc}
\usepackage{geometry}
\geometry{letterpaper, margin=1in}
\usepackage{hyperref}
\usepackage{fontspec}
\usepackage{setspace}
\usepackage{titlesec}
\usepackage{fancyhdr}
\usepackage{graphicx}
\usepackage{xcolor}

\setmainfont{Georgia}
\onehalfspacing

\titleformat{\section}
  {\normalfont\Large\bfseries}{\thesection}{1em}{}
\titleformat{\subsection}
  {\normalfont\large\bfseries}{\thesubsection}{1em}{}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{Paul Graham Essays}
\fancyhead[R]{\thepage}
\fancyfoot[C]{© Paul Graham}

\title{$title$}
\author{Paul Graham}
\date{$date$}

\begin{document}

\maketitle

\begin{abstract}
Essay \#$number$ from Paul Graham's collection.
\end{abstract}

$body$

\vspace{1cm}
\begin{center}
\textit{Original source: \url{$url$}}
\end{center}

\end{document}
"""

# Save the LaTeX template
with open('template.tex', 'w', encoding='utf-8') as f:
    f.write(latex_template)

# Function to convert a single essay to PDF and EPUB
def convert_essay(filename):
    if not filename.endswith('.md'):
        return
    
    # Extract essay number and slug from filename
    match = re.match(r'(\d+)_(.+)\.md', filename)
    if match:
        essay_number = match.group(1)
        essay_slug = match.group(2)
    else:
        # Try to extract just the name without number
        essay_slug = filename.replace('.md', '')
        # Find the essay number in the CSV based on the title
        essay_number = "000"
        for num, meta in essays_metadata.items():
            if meta.get('title', '').lower().replace(' ', '_') in essay_slug.lower():
                essay_number = num
                break
    
    # Get metadata from CSV
    metadata = essays_metadata.get(essay_number, {})
    title = metadata.get('title', essay_slug.replace('_', ' ').title())
    date = metadata.get('date', 'Unknown date')
    url = metadata.get('url', 'http://www.paulgraham.com/articles.html')
    
    input_file = os.path.join(essays_dir, filename)
    pdf_output = os.path.join(pdf_dir, f"{essay_slug}.pdf")
    epub_output = os.path.join(epub_dir, f"{essay_slug}.epub")
    
    print(f"Converting {filename} to PDF and EPUB...")
    
    try:
        # Convert to PDF with LaTeX
        pypandoc.convert_file(
            input_file,
            'pdf',
            outputfile=pdf_output,
            extra_args=[
                '--pdf-engine=xelatex',
                f'--metadata=title:{title}',
                f'--metadata=author:Paul Graham',
                f'--metadata=date:{date}',
                f'--metadata=number:{essay_number}',
                f'--metadata=url:{url}',
                '--toc',
                '--template=template.tex'
            ]
        )
        
        # Convert to EPUB
        pypandoc.convert_file(
            input_file,
            'epub',
            outputfile=epub_output,
            extra_args=[
                f'--metadata=title:{title}',
                f'--metadata=author:Paul Graham',
                f'--metadata=date:{date}',
                '--toc',
                '--epub-cover-image=cover.jpg' if os.path.exists('cover.jpg') else ''
            ]
        )
        
        print(f"Successfully converted {filename}")
        return {
            'number': essay_number,
            'title': title,
            'slug': essay_slug,
            'pdf_path': pdf_output,
            'epub_path': epub_output
        }
    except Exception as e:
        print(f"Error converting {filename}: {e}")
        return None

# Function to combine all essays into a single PDF and EPUB
def combine_essays(essays_info):
    print("Combining all essays into a single PDF and EPUB...")
    
    # Sort essays by number
    sorted_essays = sorted(essays_info, key=lambda x: int(x['number']) if x['number'].isdigit() else 999999)
    
    # Create a combined markdown file
    combined_md = os.path.join(combined_dir, 'all_essays.md')
    with open(combined_md, 'w', encoding='utf-8') as f:
        f.write("# Paul Graham Essays\n\n")
        f.write("A collection of essays by Paul Graham, co-founder of Y Combinator.\n\n")
        
        for essay in sorted_essays:
            # Read the original markdown file
            with open(os.path.join(essays_dir, f"{essay['number']}_{essay['slug']}.md"), 'r', encoding='utf-8') as essay_file:
                content = essay_file.read()
                
                # Add essay title and metadata
                f.write(f"# {essay['title']}\n\n")
                f.write(f"*Essay #{essay['number']}*\n\n")
                
                # Add the content
                f.write(content)
                f.write("\n\n---\n\n")
    
    # Convert combined markdown to PDF and EPUB
    try:
        pypandoc.convert_file(
            combined_md,
            'pdf',
            outputfile=os.path.join(combined_dir, 'paul_graham_essays.pdf'),
            extra_args=[
                '--pdf-engine=xelatex',
                '--metadata=title:Paul Graham Essays',
                '--metadata=author:Paul Graham',
                '--toc',
                '--template=template.tex'
            ]
        )
        
        pypandoc.convert_file(
            combined_md,
            'epub',
            outputfile=os.path.join(combined_dir, 'paul_graham_essays.epub'),
            extra_args=[
                '--metadata=title:Paul Graham Essays',
                '--metadata=author:Paul Graham',
                '--toc',
                '--epub-cover-image=cover.jpg' if os.path.exists('cover.jpg') else ''
            ]
        )
        
        print("Successfully created combined PDF and EPUB")
    except Exception as e:
        print(f"Error creating combined files: {e}")

# Create a simple cover image for EPUB
def create_cover_image():
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a blank image
        img = Image.new('RGB', (1200, 1800), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        
        # Try to use a nice font, fall back to default if not available
        try:
            title_font = ImageFont.truetype("Georgia", 80)
            author_font = ImageFont.truetype("Georgia", 60)
        except:
            title_font = ImageFont.load_default()
            author_font = ImageFont.load_default()
        
        # Add title and author
        d.text((600, 800), "Paul Graham Essays", fill=(0, 0, 0), font=title_font, anchor="mm")
        d.text((600, 900), "A Complete Collection", fill=(0, 0, 0), font=author_font, anchor="mm")
        
        # Save the image
        img.save('cover.jpg')
        print("Created cover image")
    except Exception as e:
        print(f"Error creating cover image: {e}")
        # Create a simple colored rectangle as fallback
        try:
            img = Image.new('RGB', (1200, 1800), color=(240, 240, 255))
            img.save('cover.jpg')
            print("Created fallback cover image")
        except:
            print("Could not create cover image")

# Main function
def main():
    # Create a cover image for EPUB
    create_cover_image()
    
    # Get all markdown files
    md_files = [f for f in os.listdir(essays_dir) if f.endswith('.md') and f != 'essays.csv']
    
    # Convert essays in parallel
    essays_info = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(convert_essay, md_files))
        essays_info = [r for r in results if r is not None]
    
    # Combine all essays
    combine_essays(essays_info)
    
    print("All conversions completed!")
    print(f"PDF files are in: {pdf_dir}")
    print(f"EPUB files are in: {epub_dir}")
    print(f"Combined files are in: {combined_dir}")

if __name__ == "__main__":
    main()
