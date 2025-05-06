import os
import shutil
import sys

def copy_directory(src, dst):
    """Copy a directory recursively."""
    if not os.path.exists(dst):
        os.makedirs(dst)

    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copy_directory(s, d)
        else:
            if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                shutil.copy2(s, d)

def setup_project():
    """Set up the project structure."""
    # Define source and destination directories
    source_dir = '../pg-essays-website'
    dest_dir = '.'

    # Create necessary directories
    directories = ['css', 'js', 'essays', 'downloads', 'downloads/pdf', 'downloads/epub', 'downloads/combined', 'netlify/functions']
    for directory in directories:
        os.makedirs(os.path.join(dest_dir, directory), exist_ok=True)

    # Copy files from the existing project
    files_to_copy = [
        ('index.html', 'index.html'),
        ('essays.html', 'essays.html'),
        ('download.html', 'download.html'),
        ('about.html', 'about.html'),
        ('404.html', '404.html'),
        ('css/styles.css', 'css/styles.css'),
        ('js/main.js', 'js/main.js'),
        ('create-essay-html.py', 'create-essay-html.py'),
        ('generate_sitemap.py', 'generate_sitemap.py'),
        ('index.js', 'index.js'),
        ('package.json', 'package.json'),
        ('robots.txt', 'robots.txt'),
        ('sitemap.xml', 'sitemap.xml'),
        ('essays/essays.csv', 'essays/essays.csv'),
        ('_redirects', '_redirects'),
        ('netlify.toml', 'netlify.toml'),
        ('netlify/functions/index.js', 'netlify/functions/index.js')
    ]

    for src, dst in files_to_copy:
        src_path = os.path.join(source_dir, src)
        dst_path = os.path.join(dest_dir, dst)

        if os.path.exists(src_path):
            # Ensure the directory exists
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            # Copy the file
            shutil.copy2(src_path, dst_path)
            print(f"Copied {src} to {dst}")
        else:
            print(f"Warning: {src_path} does not exist")

    # Copy all essay markdown files
    essays_src = os.path.join(source_dir, 'essays')
    essays_dst = os.path.join(dest_dir, 'essays')

    if os.path.exists(essays_src):
        for file in os.listdir(essays_src):
            if file.endswith('.md') and file != 'essays.csv':
                src_path = os.path.join(essays_src, file)
                dst_path = os.path.join(essays_dst, file)
                shutil.copy2(src_path, dst_path)
                print(f"Copied essay {file}")
    else:
        print(f"Warning: {essays_src} does not exist")

    # Create a modified download.html that includes links to PDF and EPUB files
    update_download_page()

    print("Project setup complete!")

def update_download_page():
    """Update the download page to include links to PDF and EPUB files."""
    download_html_path = 'download.html'

    if not os.path.exists(download_html_path):
        print(f"Warning: {download_html_path} does not exist")
        return

    with open(download_html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the section to modify
    download_section = '''<div class="bg-white overflow-hidden shadow rounded-lg border border-gray-200">
                            <div class="px-4 py-5 sm:p-6 text-center">
                                <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                                </svg>
                                <h4 class="mt-2 text-lg font-medium text-gray-900">EPUB</h4>
                                <p class="mt-1 text-sm text-gray-500">Best for e-readers</p>
                                <a href="https://github.com/ofou/graham-essays/releases/download/latest/graham.epub" class="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                                    Download EPUB
                                </a>
                            </div>
                        </div>'''

    # Create the new download section with local files
    new_download_section = '''<div class="bg-white overflow-hidden shadow rounded-lg border border-gray-200">
                            <div class="px-4 py-5 sm:p-6 text-center">
                                <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                                </svg>
                                <h4 class="mt-2 text-lg font-medium text-gray-900">EPUB</h4>
                                <p class="mt-1 text-sm text-gray-500">Best for e-readers</p>
                                <a href="downloads/combined/paul_graham_essays.epub" class="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                                    Download EPUB
                                </a>
                            </div>
                        </div>'''

    # Replace the section
    updated_content = content.replace(download_section, new_download_section)

    # Update the PDF section
    pdf_section = '''<div class="bg-white overflow-hidden shadow rounded-lg border border-gray-200">
                            <div class="px-4 py-5 sm:p-6 text-center">
                                <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                                </svg>
                                <h4 class="mt-2 text-lg font-medium text-gray-900">PDF</h4>
                                <p class="mt-1 text-sm text-gray-500">Best for printing</p>
                                <a href="https://github.com/ofou/graham-essays/releases/download/latest/graham.pdf" class="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                                    Download PDF
                                </a>
                            </div>
                        </div>'''

    new_pdf_section = '''<div class="bg-white overflow-hidden shadow rounded-lg border border-gray-200">
                            <div class="px-4 py-5 sm:p-6 text-center">
                                <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                                </svg>
                                <h4 class="mt-2 text-lg font-medium text-gray-900">PDF</h4>
                                <p class="mt-1 text-sm text-gray-500">Best for printing</p>
                                <a href="downloads/combined/paul_graham_essays.pdf" class="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                                    Download PDF
                                </a>
                            </div>
                        </div>'''

    updated_content = updated_content.replace(pdf_section, new_pdf_section)

    # Write the updated content back to the file
    with open(download_html_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    print("Updated download.html with local file links")

if __name__ == "__main__":
    setup_project()
