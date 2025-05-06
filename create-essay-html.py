import os
import re
import csv
import markdown

# Define paths
essays_dir = 'essays'
output_dir = 'essays'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

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
                'url': row.get('URL', ''),
                'category': row.get('Category', ''),
                'secondary_categories': row.get('Secondary Categories', ''),
                'tags': row.get('Tags', '')
            }

# HTML template for essay pages
html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Paul Graham Essays</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css">
    <link rel="stylesheet" href="../css/styles.css">
    <style>
        /* Mobile-friendly adjustments */
        @media (max-width: 640px) {{
            .essay-content {{ font-size: 1rem; padding: 0; }}
            .font-size-controls {{ flex-wrap: wrap; justify-content: center; margin-bottom: 1rem; }}
            .tag-container {{ flex-wrap: wrap; }}
        }}

        /* Tag styles */
        .tag {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
            margin-right: 0.5rem;
            margin-bottom: 0.5rem;
            background-color: #ffedd5;
            color: #9a3412;
        }}

        .dark-mode .tag {{
            background-color: #450a03;
            color: #fdba74;
        }}

        /* Category styles */
        .category-primary {{
            background-color: #f97316;
            color: white;
        }}

        .category-secondary {{
            background-color: #ffedd5;
            color: #9a3412;
        }}

        .dark-mode .category-primary {{
            background-color: #ea580c;
            color: white;
        }}

        .dark-mode .category-secondary {{
            background-color: #450a03;
            color: #fdba74;
        }}

        /* Global search bar */
        .search-container {{
            background-color: #f97316;
            padding: 1rem 0;
        }}

        .search-input {{
            width: 100%;
            padding: 0.75rem 1rem 0.75rem 3rem;
            border-radius: 9999px;
            border: 2px solid #fed7aa;
            background-color: white;
            font-size: 1rem;
        }}

        .search-input:focus {{
            outline: none;
            border-color: #fb923c;
            box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.2);
        }}

        .search-icon {{
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            color: #f97316;
        }}

        .dark-mode .search-container {{
            background-color: #000000;
        }}

        .dark-mode .search-input {{
            background-color: #111111;
            border-color: #ea580c;
            color: white;
        }}
    </style>
</head>
<body class="bg-gray-100 min-h-screen">
    <header class="bg-white shadow">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div class="flex flex-col md:flex-row md:justify-between md:items-center">
                <div class="mb-4 md:mb-0">
                    <h1 class="text-3xl font-bold text-gray-900">Paul Graham Essays</h1>
                    <p class="mt-2 text-gray-600">A collection of essays by Paul Graham, co-founder of Y Combinator</p>
                </div>
                <div>
                    <button id="theme-toggle" class="p-2 rounded-md text-gray-500 hover:text-gray-700 focus:outline-none">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </header>

    <!-- Global Search Bar -->
    <div class="search-container shadow-md">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="relative max-w-3xl mx-auto">
                <input type="text" id="global-search" placeholder="Search all essays..." class="search-input">
                <svg class="h-5 w-5 search-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
                </svg>
            </div>
        </div>
    </div>

    <nav class="bg-white shadow-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex flex-wrap justify-between h-auto md:h-16">
                <div class="flex flex-wrap w-full md:w-auto py-2">
                    <div class="flex-shrink-0 flex items-center w-full md:w-auto mb-2 md:mb-0">
                        <a href="/" class="text-gray-500 hover:text-gray-700">Home</a>
                    </div>
                    <div class="ml-0 md:ml-6 flex flex-wrap md:flex-nowrap space-y-2 md:space-y-0 md:space-x-8 w-full md:w-auto">
                        <a href="/essays.html" class="border-orange-500 text-gray-900 hover:text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                            Essays
                        </a>
                        <a href="/download.html" class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                            Download
                        </a>
                        <a href="/about.html" class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                            About
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </nav>

    <main class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <article>
            <header class="mb-8">
                <div class="flex flex-wrap items-center justify-between mb-2">
                    <span class="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-orange-600 bg-orange-100 mb-2">#{number}</span>
                    <span class="text-sm text-gray-500">{date}</span>
                </div>
                <h1 class="text-3xl font-bold text-gray-900 mb-4">{title}</h1>
                <div class="flex flex-wrap items-center justify-between">
                    <span class="text-sm text-gray-500 mb-2">{reading_time} min read</span>
                    <a href="{original_url}" target="_blank" rel="noopener noreferrer" class="text-sm text-orange-500 hover:text-orange-700">Original Source ↗</a>
                </div>
            </header>

            <div class="font-size-controls mb-6 flex items-center">
                <span class="text-sm text-gray-500 mr-2">Font size:</span>
                <button class="text-sm" data-size="text-sm">Small</button>
                <button class="text-base active" data-size="text-base">Medium</button>
                <button class="text-lg" data-size="text-lg">Large</button>
            </div>

            <div class="essay-content text-base">
                {content}
            </div>

            <!-- Categories Section -->
            <div class="mt-8 pt-6 border-t border-gray-200">
                <h3 class="text-lg font-semibold text-gray-900 mb-3">Categories</h3>
                <div class="tag-container flex flex-wrap">
                    {category_html}
                </div>
            </div>

            <!-- Tags Section -->
            <div class="mt-6">
                <h3 class="text-lg font-semibold text-gray-900 mb-3">Tags</h3>
                <div class="tag-container flex flex-wrap">
                    {tags_html}
                </div>
            </div>

            <div class="mt-12 pt-8 border-t border-gray-200">
                <div class="flex flex-col sm:flex-row sm:justify-between">
                    <a href="{download_url}" download="{slug}.md" class="mb-4 sm:mb-0 inline-flex items-center px-4 py-2 border border-transparent text-base font-medium rounded-md text-white bg-orange-500 hover:bg-orange-600">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                        Download Essay
                    </a>
                    <a href="/essays.html" class="inline-flex items-center px-4 py-2 border border-orange-200 text-base font-medium rounded-md text-orange-700 bg-white hover:bg-orange-50">
                        Browse More Essays
                    </a>
                </div>
            </div>
        </article>
    </main>

    <footer class="bg-white border-t border-gray-200">
        <div class="max-w-7xl mx-auto py-12 px-4 overflow-hidden sm:px-6 lg:px-8">
            <p class="text-center text-base text-gray-500">
                All essays are property of © Paul Graham. This website is not affiliated with Paul Graham.
            </p>
            <p class="text-center text-sm text-gray-500 mt-2">
                Based on the <a href="https://github.com/ofou/graham-essays" class="text-orange-500 hover:text-orange-700">graham-essays</a> repository.
            </p>
        </div>
    </footer>

    <script>
        // Theme and font size controls
        document.addEventListener('DOMContentLoaded', function() {{
            // Theme toggle
            var themeToggle = document.getElementById('theme-toggle');
            var prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');

            var currentTheme = localStorage.getItem('theme') ||
                             (prefersDarkScheme.matches ? 'dark' : 'light');

            if (currentTheme === 'dark') {{
                document.body.classList.add('dark-mode');
                updateThemeIcon(true);
            }} else {{
                document.body.classList.remove('dark-mode');
                updateThemeIcon(false);
            }}

            themeToggle.addEventListener('click', function() {{
                var isDarkMode = document.body.classList.toggle('dark-mode');
                localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
                updateThemeIcon(isDarkMode);
            }});

            // Font size controls
            var fontSizeButtons = document.querySelectorAll('.font-size-controls button');
            var essayContent = document.querySelector('.essay-content');

            fontSizeButtons.forEach(function(button) {{
                button.addEventListener('click', function() {{
                    fontSizeButtons.forEach(function(btn) {{
                        btn.classList.remove('active');
                    }});

                    this.classList.add('active');
                    var fontSize = this.getAttribute('data-size');

                    essayContent.classList.remove('text-sm', 'text-base', 'text-lg');
                    essayContent.classList.add(fontSize);

                    // Save preference
                    localStorage.setItem('essayFontSize', fontSize);
                }});
            }});

            // Apply saved font size preference
            var savedFontSize = localStorage.getItem('essayFontSize');
            if (savedFontSize) {{
                var fontButton = document.querySelector('[data-size="' + savedFontSize + '"]');
                if (fontButton) {{
                    fontButton.click();
                }}
            }}

            // Global search functionality
            var globalSearch = document.getElementById('global-search');
            if (globalSearch) {{
                globalSearch.addEventListener('keypress', function(e) {{
                    if (e.key === 'Enter') {{
                        var query = this.value.trim();
                        if (query) {{
                            window.location.href = '/essays.html?q=' + encodeURIComponent(query);
                        }}
                    }}
                }});
            }}
        }});

        function updateThemeIcon(isDarkMode) {{
            var themeToggle = document.getElementById('theme-toggle');

            if (isDarkMode) {{
                themeToggle.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" /></svg>';
            }} else {{
                themeToggle.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" /></svg>';
            }}
        }}
    </script>
</body>
</html>
'''

# Function to estimate reading time
def estimate_reading_time(text):
    words = len(re.findall(r'\w+', text))
    minutes = max(1, round(words / 200))  # Assuming 200 words per minute
    return minutes

# Process each essay file
for filename in os.listdir(essays_dir):
    if filename.endswith('.md') and not filename == 'essays.csv':
        # Extract essay number from filename
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
        original_url = metadata.get('url', 'http://www.paulgraham.com/articles.html')

        # Read the markdown content
        with open(os.path.join(essays_dir, filename), 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        # Convert markdown to HTML
        try:
            # Clean up the markdown content to remove any HTML tags that might be causing issues
            cleaned_markdown = markdown_content.replace('<!DOCTYPE html>', '').replace('<html', '&lt;html').replace('</html>', '&lt;/html&gt;')
            html_content = markdown.markdown(cleaned_markdown, extensions=['extra'])
        except Exception as e:
            print(f"Error converting {filename} to HTML: {e}")
            html_content = f"<p>{markdown_content.replace('<', '&lt;').replace('>', '&gt;')}</p>"

        # Estimate reading time
        reading_time = estimate_reading_time(markdown_content)

        # Create the HTML file
        # Create a display-friendly slug for the URL - handle all special characters
        display_slug = title.lower()
        # Replace all special characters with hyphens
        display_slug = re.sub(r'[^a-z0-9]+', '-', display_slug)
        # Remove leading and trailing hyphens
        display_slug = display_slug.strip('-')
        # Replace multiple hyphens with a single hyphen
        display_slug = re.sub(r'-+', '-', display_slug)

        output_filename = f"{display_slug}.html"
        output_path = os.path.join(output_dir, output_filename)

        # Get category and tags from metadata
        category = ""
        secondary_categories = ""
        tags = ""

        if essay_number in essays_metadata:
            category = essays_metadata[essay_number].get('category', '')
            secondary_categories = essays_metadata[essay_number].get('secondary_categories', '')
            tags = essays_metadata[essay_number].get('tags', '')

        # Generate category HTML
        category_html = ""
        if category:
            category_html += f'<span class="tag category-primary">{category}</span>'

        if secondary_categories:
            secondary_list = [cat.strip() for cat in secondary_categories.split(',') if cat.strip()]
            for sec_cat in secondary_list:
                category_html += f'<span class="tag category-secondary">{sec_cat}</span>'

        if not category and not secondary_categories:
            category_html = '<span class="tag category-primary">Uncategorized</span>'

        # Generate tags HTML
        tags_html = ""
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            for tag in tag_list:
                tags_html += f'<span class="tag">{tag}</span>'
        else:
            # Generate some default tags based on the title
            default_tags = [word.lower() for word in title.split() if len(word) > 3][:5]
            for tag in default_tags:
                tags_html += f'<span class="tag">{tag}</span>'

        # Fill in the template
        html_output = html_template.format(
            title=title,
            number=essay_number,
            date=date,
            reading_time=reading_time,
            original_url=original_url,
            content=html_content,
            download_url=f"/essays/{filename}",
            slug=essay_slug,
            category_html=category_html,
            tags_html=tags_html
        )

        # Write the HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_output)

        print(f"Generated {output_path}")

print("Essay page generation complete!")
