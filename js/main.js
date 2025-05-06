// Main JavaScript for Paul Graham Essays website

document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme
    initTheme();

    // Load essays data
    loadEssaysData();

    // Initialize search
    initSearch();

    // Handle routing
    handleRouting();
});

// Theme toggle functionality
function initTheme() {
    const themeToggle = document.getElementById('theme-toggle');
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');

    // Check for saved theme preference or use the system preference
    const currentTheme = localStorage.getItem('theme') ||
                         (prefersDarkScheme.matches ? 'dark' : 'light');

    // Apply the theme
    if (currentTheme === 'dark') {
        document.body.classList.add('dark-mode');
        updateThemeIcon(true);
    } else {
        document.body.classList.remove('dark-mode');
        updateThemeIcon(false);
    }

    // Add event listener to the theme toggle button
    themeToggle.addEventListener('click', function() {
        const isDarkMode = document.body.classList.toggle('dark-mode');
        localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
        updateThemeIcon(isDarkMode);
    });
}

// Update the theme icon based on the current theme
function updateThemeIcon(isDarkMode) {
    const themeToggle = document.getElementById('theme-toggle');

    if (isDarkMode) {
        themeToggle.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
        `;
    } else {
        themeToggle.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
        `;
    }
}

// Load essays data from the CSV file
async function loadEssaysData() {
    try {
        const response = await fetch('/essays/essays.csv');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const csvText = await response.text();
        const essays = parseCSV(csvText);

        // Display featured essays on the home page
        if (document.getElementById('featured-essays')) {
            displayFeaturedEssays(essays);
        }

        // Display all essays on the essays page
        if (document.getElementById('all-essays')) {
            displayAllEssays(essays);
        }

        // Store essays data for search functionality
        window.essaysData = essays;

    } catch (error) {
        console.error('Error loading essays data:', error);
        // Display error message to the user
        const featuredEssaysElement = document.getElementById('featured-essays');
        if (featuredEssaysElement) {
            featuredEssaysElement.innerHTML = `
                <div class="col-span-3 text-center py-8">
                    <p class="text-red-500">Failed to load essays. Please try again later.</p>
                </div>
            `;
        }
    }
}

// Parse CSV data into an array of essay objects
function parseCSV(csvText) {
    const lines = csvText.split('\n');
    const headers = lines[0].split(',');

    return lines.slice(1).filter(line => line.trim() !== '').map(line => {
        const values = line.split(',');
        const essay = {};

        headers.forEach((header, index) => {
            // Remove quotes from values
            let value = values[index] || '';
            if (value.startsWith('"') && value.endsWith('"')) {
                value = value.substring(1, value.length - 1);
            }
            essay[header.trim()] = value;
        });

        return essay;
    });
}

// Display featured essays on the home page
function displayFeaturedEssays(essays) {
    const featuredEssaysElement = document.getElementById('featured-essays');
    if (!featuredEssaysElement) return;

    // Get 3 featured essays (you can customize this selection)
    const featuredEssays = essays.slice(0, 3);

    featuredEssaysElement.innerHTML = featuredEssays.map(essay => {
        const number = essay['Article no.'] || '';
        const title = essay['Title'] || '';
        const date = essay['Date'] || '';
        const url = essay['URL'] || '';

        // Create a slug from the title for the local URL
        const slug = title.toLowerCase().replace(/[^\w\s]/g, '').replace(/\s+/g, '-');

        return `
            <div class="bg-white rounded-lg shadow-md overflow-hidden">
                <div class="p-6">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-indigo-600 bg-indigo-200">#${number}</span>
                        <span class="text-xs text-gray-500">${date}</span>
                    </div>
                    <h3 class="text-xl font-bold text-gray-900 mb-2">${title}</h3>
                    <p class="text-gray-600 mb-4">Loading excerpt...</p>
                    <div class="flex items-center justify-between">
                        <span class="text-sm text-gray-500">Read time: ~10 min</span>
                        <a href="/essays/${slug}.html" class="text-indigo-600 hover:text-indigo-800 font-medium text-sm">Read more →</a>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    // Load excerpts for each essay
    featuredEssays.forEach((essay, index) => {
        const number = essay['Article no.'] || '';
        loadEssayExcerpt(number, index);
    });
}

// Load excerpt for an essay
async function loadEssayExcerpt(essayNumber, index) {
    try {
        const response = await fetch(`/essays/${essayNumber}.md`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const markdown = await response.text();
        const excerpt = extractExcerpt(markdown, 150);

        const excerptElements = document.querySelectorAll('#featured-essays p.text-gray-600');
        if (excerptElements[index]) {
            excerptElements[index].textContent = excerpt;
        }

    } catch (error) {
        console.error(`Error loading excerpt for essay ${essayNumber}:`, error);
    }
}

// Extract an excerpt from the markdown content
function extractExcerpt(markdown, length = 150) {
    // Remove markdown formatting
    let text = markdown
        .replace(/^#.*$/gm, '') // Remove headings
        .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Replace links with just the text
        .replace(/[*_~`]/g, '') // Remove emphasis markers
        .replace(/\n+/g, ' ') // Replace newlines with spaces
        .trim();

    // Truncate to the specified length
    if (text.length > length) {
        text = text.substring(0, length) + '...';
    }

    return text;
}

// Initialize search functionality
function initSearch() {
    const searchInput = document.getElementById('search-input');
    if (!searchInput) return;

    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const query = searchInput.value.trim();
            if (query) {
                window.location.href = `/essays.html?q=${encodeURIComponent(query)}`;
            }
        }
    });

    // If we're on the essays page and there's a query parameter, perform the search
    if (window.location.pathname.includes('essays.html')) {
        const urlParams = new URLSearchParams(window.location.search);
        const query = urlParams.get('q');

        if (query) {
            searchInput.value = query;
            performSearch(query);
        }
    }
}

// Perform search on essays
function performSearch(query) {
    if (!window.essaysData) return;

    const searchResults = window.essaysData.filter(essay => {
        const title = essay['Title'] || '';
        return title.toLowerCase().includes(query.toLowerCase());
    });

    const allEssaysElement = document.getElementById('all-essays');
    if (!allEssaysElement) return;

    if (searchResults.length > 0) {
        displayAllEssays(searchResults);

        // Update the heading to show search results
        const heading = document.querySelector('h2.text-2xl');
        if (heading) {
            heading.textContent = `Search Results for "${query}"`;
        }
    } else {
        allEssaysElement.innerHTML = `
            <div class="col-span-3 text-center py-8">
                <p class="text-gray-500">No essays found matching "${query}".</p>
                <a href="/essays.html" class="mt-4 inline-block text-indigo-600 hover:text-indigo-800">View all essays</a>
            </div>
        `;
    }
}

// Handle routing for SPA-like behavior
function handleRouting() {
    // Fix all internal links to use the router
    document.querySelectorAll('a').forEach(link => {
        const href = link.getAttribute('href');

        // Only process internal links that aren't already absolute
        if (href && !href.startsWith('http') && !href.startsWith('#') && !href.startsWith('/')) {
            // Convert relative links to absolute
            if (href.startsWith('essays/')) {
                link.setAttribute('href', '/' + href);
            } else {
                link.setAttribute('href', '/' + href);
            }
        }
    });

    // Handle 404 errors by redirecting to index
    if (document.title.includes('Page Not Found')) {
        console.log('404 page detected, redirecting to home page...');
        setTimeout(() => {
            window.location.href = '/';
        }, 3000);
    }
}
