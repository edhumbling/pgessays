# Paul Graham Essays Website

A modern, responsive website showcasing Paul Graham's essays with online reading and high-quality PDF/EPUB download capabilities.

## Features

- **Complete Collection**: Access to all of Paul Graham's essays (200+)
- **Online Reading**: Clean, distraction-free reading experience
- **High-Quality Downloads**: Download essays in beautifully formatted PDF and EPUB formats
- **LaTeX Integration**: Uses LaTeX for professional-quality PDF output
- **Search & Filter**: Find essays by keyword or topic
- **Responsive Design**: Optimized for all devices
- **Dark Mode**: Toggle between light and dark themes
- **Automatic Updates**: Weekly checks for new essays on Paul Graham's website using GitHub Actions

## How It Works

This website is built on top of the [graham-essays](https://github.com/ofou/graham-essays) repository, which provides a collection of Paul Graham's essays in various formats. The website uses Python scripts to generate HTML, PDF, and EPUB versions of the essays.

### Automatic Updates

This repository is set up with GitHub Actions to automatically check for new essays on Paul Graham's website every week:

1. A GitHub Actions workflow runs every Monday at 00:00 UTC
2. The workflow checks Paul Graham's website for new essays
3. If new essays are found, they are downloaded, processed, and added to the repository
4. The changes are automatically committed and pushed to the repository
5. Netlify automatically deploys the updated website

You can also manually trigger the update workflow by going to the "Actions" tab in the GitHub repository and selecting "Weekly Essay Update" from the list of workflows. Then click the "Run workflow" button.

### Technical Details

- **Frontend**: HTML, CSS, and JavaScript
- **Styling**: Tailwind CSS
- **Backend**: Python scripts for processing essays and generating formatted outputs
- **PDF Generation**: LaTeX via Pandoc for professional-quality typesetting
- **EPUB Generation**: Pandoc for well-structured e-books
- **Deployment**: Netlify

## Local Development

### Prerequisites

- Python 3.9 or higher
- Git
- Pandoc (will be automatically installed by the scripts if not present)

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/edhumbling/pgessays.git
   cd pgessays
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the setup script to initialize the project:
   ```bash
   python setup_project.py
   ```

4. Generate the HTML files:
   ```bash
   python create-essay-html.py
   ```

5. Generate PDF and EPUB files:
   ```bash
   python generate_pdf_epub.py
   ```

6. Start a local server:
   ```bash
   python -m http.server 8000
   ```

7. Open your browser and navigate to `http://localhost:8000`

## Deployment

This website is configured for deployment on Netlify. The `netlify.toml` file contains the configuration for the build process.

### Deploying to the existing site (paulgramessays.netlify.app)

This repository is already connected to the Netlify site at [paulgramessays.netlify.app](https://paulgramessays.netlify.app). When you push changes to the main branch, Netlify will automatically build and deploy the site.

### Deploying to a new Netlify site

If you want to deploy to your own Netlify site:

1. Fork this repository
2. Connect your GitHub repository to Netlify
3. Configure the build settings:
   - Build command: `python setup_project.py && python create-essay-html.py && python generate_pdf_epub.py`
   - Publish directory: `.`
4. Click "Deploy site"

## Project Structure

```
pgessays/
├── css/                  # CSS stylesheets
├── js/                   # JavaScript files
├── essays/               # Markdown essays
├── downloads/            # Generated download files
│   ├── pdf/              # Individual PDF files
│   ├── epub/             # Individual EPUB files
│   └── combined/         # Combined PDF and EPUB files
├── create-essay-html.py  # Script to generate HTML files
├── generate_pdf_epub.py  # Script to generate PDF and EPUB files
├── setup_project.py      # Script to set up the project
├── netlify.toml          # Netlify configuration
└── requirements.txt      # Python dependencies
```

## Credits

- All essays are property of © Paul Graham
- Essay collection based on [ofou/graham-essays](https://github.com/ofou/graham-essays)
- PDF and EPUB generation using [Pandoc](https://pandoc.org/) and LaTeX

## License

This project is open source and available under the MIT License.
