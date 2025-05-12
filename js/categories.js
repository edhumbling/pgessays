// Categories and excerpts handling for Paul Graham Essays website

// Load categories data
async function loadCategoriesData() {
    try {
        const response = await fetch('essays/categories.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const categoriesData = await response.json();
        window.categoriesData = categoriesData;
        return categoriesData;
    } catch (error) {
        console.error('Error loading categories data:', error);
        return null;
    }
}

// Get categories for an essay
function getEssayCategories(essayNumber, categoriesData) {
    if (!categoriesData || !categoriesData.essayTags || !essayNumber) {
        return [];
    }

    return categoriesData.essayTags[essayNumber] || [];
}

// Get category name from ID
function getCategoryName(categoryId, categoriesData) {
    if (!categoriesData || !categoriesData.categories) {
        return categoryId;
    }

    const category = categoriesData.categories.find(cat => cat.id === categoryId);
    return category ? category.name : categoryId;
}

// Generate HTML for category tags
function generateCategoryTags(essayNumber, categoriesData) {
    if (!categoriesData || !essayNumber) {
        return '';
    }

    const categoryIds = getEssayCategories(essayNumber, categoriesData);
    if (!categoryIds || categoryIds.length === 0) {
        return '';
    }

    return categoryIds.map(categoryId => {
        const categoryName = getCategoryName(categoryId, categoriesData);
        const isPrimary = categoryId === categoryIds[0];
        const tagClass = isPrimary ? 'category-primary' : 'category-secondary';

        return `<span class="tag ${tagClass}" data-category="${categoryId}">${categoryName}</span>`;
    }).join('');
}

// Preload excerpts for featured essays
async function preloadExcerpts() {
    try {
        // Get the latest essays
        const response = await fetch('essays/categories.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const categoriesData = await response.json();
        const featuredEssays = categoriesData.categories.find(cat => cat.id === 'featured');
        const latestEssays = categoriesData.categories.find(cat => cat.id === 'latest');

        if (!featuredEssays || !latestEssays) {
            return;
        }

        // Combine featured and latest essays, remove duplicates
        const essaysToPreload = [...new Set([...featuredEssays.essays, ...latestEssays.essays])];

        // Preload excerpts for these essays
        const excerpts = {};

        await Promise.all(essaysToPreload.map(async (essayNumber) => {
            try {
                const response = await fetch(`essays/${essayNumber}.md`);
                if (!response.ok) {
                    return;
                }

                const markdown = await response.text();
                excerpts[essayNumber] = extractExcerpt(markdown, 150);
            } catch (error) {
                console.error(`Error preloading excerpt for essay ${essayNumber}:`, error);
            }
        }));

        // Store excerpts in window object for quick access
        window.preloadedExcerpts = excerpts;

    } catch (error) {
        console.error('Error preloading excerpts:', error);
    }
}

// Get preloaded excerpt or load it if not available
async function getExcerpt(essayNumber, index, containerSelector) {
    // Check if we have a preloaded excerpt
    if (window.preloadedExcerpts && window.preloadedExcerpts[essayNumber]) {
        const excerptElements = document.querySelectorAll(`${containerSelector} p.text-gray-600`);
        if (excerptElements[index]) {
            excerptElements[index].textContent = window.preloadedExcerpts[essayNumber];
        }
        return;
    }

    // Otherwise load it
    try {
        const response = await fetch(`essays/${essayNumber}.md`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const markdown = await response.text();
        const excerpt = extractExcerpt(markdown, 150);

        const excerptElements = document.querySelectorAll(`${containerSelector} p.text-gray-600`);
        if (excerptElements[index]) {
            excerptElements[index].textContent = excerpt;
        }

    } catch (error) {
        console.error(`Error loading excerpt for essay ${essayNumber}:`, error);
    }
}

// Filter essays by category
function filterEssaysByCategory(essays, categoryId, categoriesData) {
    if (categoryId === 'all') {
        return essays;
    }

    if (!categoriesData || !categoriesData.essayTags) {
        return essays;
    }

    return essays.filter(essay => {
        const essayNumber = essay['Article no.'];
        const categories = getEssayCategories(essayNumber, categoriesData);
        return categories.includes(categoryId);
    });
}

// Initialize categories on page load
document.addEventListener('DOMContentLoaded', function() {
    // Preload excerpts for faster loading
    preloadExcerpts();

    // Load categories data
    loadCategoriesData();
});
