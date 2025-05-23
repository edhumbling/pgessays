// Main JavaScript for Paul Graham Essays website

document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme
    initTheme();

    // Load categories data first
    loadCategoriesData().then(() => {
        // Preload excerpts for faster loading
        preloadExcerpts();

        // Load essays data
        loadEssaysData();
    });

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
    const headers = lines[0].split(',').map(header => header.trim());

    return lines.slice(1).filter(line => line.trim() !== '').map(line => {
        // Handle commas within quoted fields
        const values = [];
        let currentValue = '';
        let inQuotes = false;

        for (let i = 0; i < line.length; i++) {
            const char = line[i];

            if (char === '"') {
                inQuotes = !inQuotes;
            } else if (char === ',' && !inQuotes) {
                values.push(currentValue);
                currentValue = '';
            } else {
                currentValue += char;
            }
        }

        // Add the last value
        values.push(currentValue);

        const essay = {};

        headers.forEach((header, index) => {
            // Remove quotes from values
            let value = values[index] || '';
            if (value.startsWith('"') && value.endsWith('"')) {
                value = value.substring(1, value.length - 1);
            }
            essay[header] = value;
        });

        return essay;
    });
}

// Display featured essays on the home page
function displayFeaturedEssays(essays) {
    const featuredEssaysElement = document.getElementById('featured-essays');
    if (!featuredEssaysElement) return;

    // Get featured essays from categories data and reading metrics
    let featuredEssays = [];

    // Try to get popular essays from reading metrics
    let popularEssayIds = [];
    try {
        // Get popular essays from Supabase or localStorage
        if (typeof getPopularEssays === 'function') {
            // This is an async function, but we'll handle it synchronously for now
            // In a future update, we could make displayFeaturedEssays async
            const localPopularEssays = JSON.parse(localStorage.getItem('pgEssaysPopular') || '{}');

            // Convert to array and sort by count
            const popularEssayEntries = Object.entries(localPopularEssays)
                .map(([id, count]) => ({ id, count }))
                .sort((a, b) => b.count - a.count)
                .slice(0, 5); // Get top 5

            // Extract IDs
            popularEssayEntries.forEach(entry => popularEssayIds.push(entry.id));

            // Try to get from API in the background
            if (window.pgEssaysApi) {
                window.pgEssaysApi.getPopularEssays(5).then(apiPopularEssays => {
                    if (apiPopularEssays && apiPopularEssays.length > 0) {
                        // We'll update the UI next time
                        console.log('Got popular essays from API for next refresh');
                    }
                }).catch(error => {
                    console.error('Error getting popular essays from API:', error);
                });
            }
        }
    } catch (e) {
        console.error('Error getting popular essays:', e);
    }

    // Get latest essays
    const latestEssays = [...essays].sort((a, b) => {
        const dateA = new Date(a['Date'] || '1900-01-01');
        const dateB = new Date(b['Date'] || '1900-01-01');
        return dateB - dateA;
    }).slice(0, 3); // Get 3 latest

    // Combine popular and latest essays
    const combinedEssayIds = new Set([
        ...popularEssayIds,
        ...latestEssays.map(essay => essay['Article no.'])
    ]);

    // If we have combined essays, use them
    if (combinedEssayIds.size > 0) {
        // Map to full essay objects
        featuredEssays = Array.from(combinedEssayIds)
            .slice(0, 3) // Limit to 3 essays
            .map(number => {
                return essays.find(essay => essay['Article no.'] === number.toString());
            })
            .filter(essay => essay); // Remove any undefined entries
    }

    // Fallback to category-based featured essays if needed
    if (featuredEssays.length === 0 && window.categoriesData && window.categoriesData.categories) {
        const featuredCategory = window.categoriesData.categories.find(cat => cat.id === 'featured');
        if (featuredCategory && featuredCategory.essays) {
            // Get the featured essay numbers
            const featuredNumbers = featuredCategory.essays;

            // Get the latest 3 featured essays
            const latestFeatured = featuredNumbers.slice(0, 3);

            // Map to full essay objects
            featuredEssays = latestFeatured.map(number => {
                return essays.find(essay => essay['Article no.'] === number.toString());
            }).filter(essay => essay); // Remove any undefined entries
        }
    }

    // If we couldn't get featured essays from categories, fall back to latest essays
    if (featuredEssays.length === 0) {
        // Sort essays by date (newest first)
        const sortedEssays = [...essays].sort((a, b) => {
            const dateA = new Date(a['Date'] || '1900-01-01');
            const dateB = new Date(b['Date'] || '1900-01-01');
            return dateB - dateA;
        });

        // Get 3 latest essays
        featuredEssays = sortedEssays.slice(0, 3);
    }

    // Check if any essays were added in the last 30 days
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    featuredEssaysElement.innerHTML = featuredEssays.map(essay => {
        const number = essay['Article no.'] || '';
        const title = essay['Title'] || '';
        const date = essay['Date'] || '';
        const url = essay['URL'] || '';

        // Use the essay number to create a more reliable slug
        const essayNumber = essay['Article no.'] || '';
        // Find the corresponding essay file
        const slug = `${essayNumber}_${title.toLowerCase().replace(/[^\w\s]/g, '').replace(/\s+/g, '_')}`;
        // For display purposes, we'll use a simpler slug that matches the create-essay-html.py logic
        let displaySlug = title.toLowerCase();
        // Replace all special characters with hyphens
        displaySlug = displaySlug.replace(/[^a-z0-9]+/g, '-');
        // Remove leading and trailing hyphens
        displaySlug = displaySlug.replace(/^-+|-+$/g, '');
        // Replace multiple hyphens with a single hyphen
        displaySlug = displaySlug.replace(/-+/g, '-');

        // Check if this is a new essay (added in the last 30 days)
        const essayDate = new Date(date || '1900-01-01');
        const isNew = essayDate > thirtyDaysAgo;

        // New tag HTML
        const newTag = isNew ?
            `<span class="ml-2 text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-white bg-orange-500">NEW</span>` : '';

        // Get categories for this essay
        let categoryTags = '';
        if (window.categoriesData) {
            categoryTags = generateCategoryTags(number, window.categoriesData);
        }

        // Check if we have a preloaded excerpt
        let excerptText = 'Loading excerpt...';
        if (window.preloadedExcerpts && window.preloadedExcerpts[number]) {
            excerptText = window.preloadedExcerpts[number];
        }

        return `
            <div class="bg-white rounded-lg shadow-md overflow-hidden">
                <div class="p-6">
                    <div class="flex items-center justify-between mb-2">
                        <div class="flex items-center">
                            <span class="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-orange-600 bg-orange-100">#${number}</span>
                            ${newTag}
                        </div>
                        <span class="text-xs text-gray-500">${date}</span>
                    </div>
                    <h3 class="text-xl font-bold text-gray-900 mb-2">${title}</h3>
                    <p class="text-gray-600 mb-4">${excerptText}</p>
                    <div class="flex flex-wrap items-center mb-3">
                        ${categoryTags}
                    </div>
                    <div class="flex items-center justify-between">
                        <span class="text-sm text-gray-500">Read time: ~10 min</span>
                        <a href="essays/${displaySlug}.html" class="text-orange-600 hover:text-orange-800 font-medium text-sm">Read more →</a>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    // Load excerpts for each essay if they weren't preloaded
    featuredEssays.forEach((essay, index) => {
        const number = essay['Article no.'] || '';
        if (!window.preloadedExcerpts || !window.preloadedExcerpts[number]) {
            getExcerpt(number, index, '#featured-essays');
        }
    });
}

// Load excerpt for an essay (legacy function, use getExcerpt instead)
async function loadEssayExcerpt(essayNumber, index) {
    // Use the new getExcerpt function instead
    getExcerpt(essayNumber, index, '#featured-essays');
}

// Extract an excerpt from the markdown content
function extractExcerpt(markdown, length = 150) {
    // Remove HTML tags first
    let text = markdown
        .replace(/<\/?[^>]+(>|$)/g, '') // Remove HTML tags
        .replace(/<!DOCTYPE.*?>/gi, '') // Remove DOCTYPE
        .replace(/^#.*$/gm, '') // Remove headings
        .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Replace links with just the text
        .replace(/[*_~`]/g, '') // Remove emphasis markers
        .replace(/\n+/g, ' ') // Replace newlines with spaces
        .trim();

    // Skip date paragraphs (like "May 2020")
    const dateRegex = /(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}/;
    if (dateRegex.test(text.substring(0, 20))) {
        text = text.substring(text.indexOf(' ', 20) + 1).trim();
    }

    // Truncate to the specified length
    if (text.length > length) {
        text = text.substring(0, length) + '...';
    }

    return text;
}

// Initialize search functionality
function initSearch() {
    // Handle regular search input
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const query = searchInput.value.trim();
                if (query) {
                    window.location.href = `essays.html?q=${encodeURIComponent(query)}`;
                }
            }
        });
    }

    // Handle global search input
    const globalSearch = document.getElementById('global-search');
    if (globalSearch) {
        globalSearch.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const query = globalSearch.value.trim();
                if (query) {
                    window.location.href = `essays.html?q=${encodeURIComponent(query)}`;
                }
            }
        });

        // Also handle the search button click
        const searchButton = document.querySelector('button[type="button"]');
        if (searchButton) {
            searchButton.addEventListener('click', function() {
                const query = globalSearch.value.trim();
                if (query) {
                    window.location.href = `essays.html?q=${encodeURIComponent(query)}`;
                }
            });
        }
    }

    // If we're on the essays page and there's a query parameter, perform the search
    if (window.location.pathname.includes('essays.html')) {
        const urlParams = new URLSearchParams(window.location.search);
        const query = urlParams.get('q');

        if (query) {
            // Update both search inputs if they exist
            if (searchInput) searchInput.value = query;
            if (globalSearch) globalSearch.value = query;

            performSearch(query);
        }
    }
}

// Perform search on essays
function performSearch(query) {
    if (!window.essaysData) return;

    const searchResults = window.essaysData.filter(essay => {
        // Search in title
        const title = essay['Title'] || '';
        if (title.toLowerCase().includes(query.toLowerCase())) {
            return true;
        }

        // Search in category
        const category = essay['Category'] || '';
        if (category.toLowerCase().includes(query.toLowerCase())) {
            return true;
        }

        // Search in secondary categories
        const secondaryCategories = essay['Secondary Categories'] || '';
        if (secondaryCategories.toLowerCase().includes(query.toLowerCase())) {
            return true;
        }

        // Search in tags
        const tags = essay['Tags'] || '';
        if (tags.toLowerCase().includes(query.toLowerCase())) {
            return true;
        }

        return false;
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
                <a href="essays.html" class="mt-4 inline-block text-orange-500 hover:text-orange-700">View all essays</a>
            </div>
        `;
    }
}

// Display all essays on the essays page
function displayAllEssays(essays) {
    const allEssaysElement = document.getElementById('all-essays');
    if (!allEssaysElement) return;

    // Sort essays by date (newest first)
    const sortedEssays = [...essays].sort((a, b) => {
        const dateA = new Date(a['Date'] || '1900-01-01');
        const dateB = new Date(b['Date'] || '1900-01-01');
        return dateB - dateA;
    });

    // Check if any essays were added in the last 30 days
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    allEssaysElement.innerHTML = sortedEssays.map(essay => {
        const number = essay['Article no.'] || '';
        const title = essay['Title'] || '';
        const date = essay['Date'] || '';
        const url = essay['URL'] || '';

        // Create a slug from the title for the local URL
        let displaySlug = title.toLowerCase();
        // Replace all special characters with hyphens
        displaySlug = displaySlug.replace(/[^a-z0-9]+/g, '-');
        // Remove leading and trailing hyphens
        displaySlug = displaySlug.replace(/^-+|-+$/g, '');
        // Replace multiple hyphens with a single hyphen
        displaySlug = displaySlug.replace(/-+/g, '-');

        // Check if this is a new essay (added in the last 30 days)
        const essayDate = new Date(date || '1900-01-01');
        const isNew = essayDate > thirtyDaysAgo;

        // New tag HTML
        const newTag = isNew ?
            `<span class="ml-2 text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-white bg-orange-500">NEW</span>` : '';

        // Get categories for this essay
        let categoryTags = '';
        if (window.categoriesData) {
            categoryTags = generateCategoryTags(number, window.categoriesData);
        }

        // Check if we have a preloaded excerpt
        let excerptText = 'Loading excerpt...';
        if (window.preloadedExcerpts && window.preloadedExcerpts[number]) {
            excerptText = window.preloadedExcerpts[number];
        }

        return `
            <div class="bg-white rounded-lg shadow-md overflow-hidden">
                <div class="p-6">
                    <div class="flex items-center justify-between mb-2">
                        <div class="flex items-center">
                            <span class="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-orange-600 bg-orange-100">#${number}</span>
                            ${newTag}
                        </div>
                        <span class="text-xs text-gray-500">${date}</span>
                    </div>
                    <h3 class="text-xl font-bold text-gray-900 mb-2">${title}</h3>
                    <p class="text-gray-600 mb-4">${excerptText}</p>
                    <div class="flex flex-wrap items-center mb-3">
                        ${categoryTags}
                    </div>
                    <div class="flex items-center justify-between">
                        <span class="text-sm text-gray-500">Read time: ~10 min</span>
                        <a href="essays/${displaySlug}.html" class="text-orange-500 hover:text-orange-700 font-medium text-sm">Read more →</a>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    // Load excerpts for each essay if they weren't preloaded
    sortedEssays.forEach((essay, index) => {
        const number = essay['Article no.'] || '';
        if (!window.preloadedExcerpts || !window.preloadedExcerpts[number]) {
            getExcerpt(number, index, '#all-essays');
        }
    });
}

// Handle routing for SPA-like behavior
function handleRouting() {
    // Fix all internal links to use the router
    document.querySelectorAll('a').forEach(link => {
        const href = link.getAttribute('href');

        // Only process internal links that aren't already absolute
        if (href && !href.startsWith('http') && !href.startsWith('#') && !href.startsWith('/')) {
            // Keep links relative
            // No need to modify links as they should remain relative
        }
    });

    // Handle 404 errors by redirecting to index
    if (document.title.includes('Page Not Found')) {
        console.log('404 page detected, redirecting to home page...');
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 3000);
    }
}
