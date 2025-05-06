// Reading metrics tracking for Paul Graham Essays website

// Global variables for tracking
let readingStartTime = null;
let readingProgress = 0;
let essayId = null;
let essayTitle = null;
let progressBar = null;
let isEssayPage = false;

// Initialize reading metrics tracking
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on an essay page
    const essayContent = document.querySelector('.essay-content');
    if (!essayContent) return;

    isEssayPage = true;

    // Get essay ID and title
    const titleElement = document.querySelector('h1');
    if (titleElement) {
        const titleText = titleElement.textContent || '';
        const match = titleText.match(/^(\d+)\s+(.+)$/);
        if (match) {
            essayId = match[1];
            essayTitle = match[2];
        } else {
            essayId = 'unknown';
            essayTitle = titleText;
        }
    }

    // Create progress bar
    createProgressBar();

    // Start tracking reading
    startReadingTracking();

    // Track scroll position
    window.addEventListener('scroll', updateReadingProgress);

    // Track when user leaves the page
    window.addEventListener('beforeunload', saveReadingMetrics);
});

// Create the glass effect progress bar
function createProgressBar() {
    // Create container
    progressBar = document.createElement('div');
    progressBar.className = 'reading-progress-bar';
    progressBar.innerHTML = `
        <div class="progress-fill"></div>
        <div class="progress-text">0% Read</div>
    `;

    // Add styles
    const style = document.createElement('style');
    style.textContent = `
        .reading-progress-bar {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            width: 80%;
            max-width: 600px;
            height: 40px;
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            padding: 0 15px;
            z-index: 1000;
            transition: opacity 0.3s ease;
            opacity: 0.8;
        }

        .reading-progress-bar:hover {
            opacity: 1;
        }

        .progress-fill {
            position: absolute;
            left: 0;
            top: 0;
            height: 100%;
            background: linear-gradient(90deg, rgba(249, 115, 22, 0.2) 0%, rgba(249, 115, 22, 0.4) 100%);
            border-radius: 20px;
            width: 0%;
            transition: width 0.3s ease;
        }

        .progress-text {
            position: relative;
            z-index: 1;
            color: #333;
            font-weight: 500;
            font-size: 14px;
            margin-left: auto;
            margin-right: auto;
        }

        .dark-mode .reading-progress-bar {
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .dark-mode .progress-fill {
            background: linear-gradient(90deg, rgba(249, 115, 22, 0.4) 0%, rgba(249, 115, 22, 0.6) 100%);
        }

        .dark-mode .progress-text {
            color: #fff;
        }

        @media (max-width: 768px) {
            .reading-progress-bar {
                width: 90%;
                bottom: 10px;
                height: 30px;
            }

            .progress-text {
                font-size: 12px;
            }
        }
    `;

    document.head.appendChild(style);
    document.body.appendChild(progressBar);

    // Hide initially and fade in after 2 seconds
    progressBar.style.opacity = '0';
    setTimeout(() => {
        progressBar.style.opacity = '0.8';
    }, 2000);
}

// Start tracking reading time
function startReadingTracking() {
    readingStartTime = new Date();

    // Track in API if available
    if (window.pgEssaysApi && essayId && essayTitle) {
        window.pgEssaysApi.startReadingTracking(essayId, essayTitle);
    }
}

// Update reading progress based on scroll position
function updateReadingProgress() {
    if (!isEssayPage || !progressBar) return;

    const windowHeight = window.innerHeight;
    const documentHeight = Math.max(
        document.body.scrollHeight,
        document.body.offsetHeight,
        document.documentElement.clientHeight,
        document.documentElement.scrollHeight,
        document.documentElement.offsetHeight
    );
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

    // Calculate progress (accounting for window height)
    const scrollableHeight = documentHeight - windowHeight;
    readingProgress = Math.min(Math.round((scrollTop / scrollableHeight) * 100), 100);

    // Update progress bar
    const progressFill = progressBar.querySelector('.progress-fill');
    const progressText = progressBar.querySelector('.progress-text');

    if (progressFill && progressText) {
        progressFill.style.width = `${readingProgress}%`;
        progressText.textContent = `${readingProgress}% Read`;
    }

    // Update progress in API every 5% change
    if (window.pgEssaysApi && essayId && readingProgress % 5 === 0) {
        window.pgEssaysApi.updateReadingProgress(essayId, readingProgress);
    }

    // If reached the end (95% or more), mark as completed
    if (readingProgress >= 95) {
        markEssayAsCompleted();
    }
}

// Mark essay as completed
function markEssayAsCompleted() {
    if (!essayId) return;

    // Get existing completed essays from localStorage (for backward compatibility)
    const completedEssays = JSON.parse(localStorage.getItem('pgEssaysCompleted') || '{}');

    // Only mark as completed once in localStorage
    if (completedEssays[essayId]) return;

    // Add to completed essays with timestamp
    completedEssays[essayId] = {
        title: essayTitle,
        completedAt: new Date().toISOString()
    };

    // Save to localStorage for backward compatibility
    localStorage.setItem('pgEssaysCompleted', JSON.stringify(completedEssays));

    // Save to API if available
    if (window.pgEssaysApi) {
        window.pgEssaysApi.markEssayAsCompleted(essayId);
    }
}

// Save reading metrics when leaving the page
function saveReadingMetrics() {
    if (!essayId || !readingStartTime) return;

    // Calculate reading time in seconds
    const readingTime = Math.round((new Date() - readingStartTime) / 1000);

    // Get existing reading metrics from localStorage (for backward compatibility)
    const readingMetrics = JSON.parse(localStorage.getItem('pgEssaysMetrics') || '{}');

    // Update metrics for this essay in localStorage
    if (!readingMetrics[essayId]) {
        readingMetrics[essayId] = {
            title: essayTitle,
            views: 0,
            totalReadingTime: 0,
            maxProgress: 0,
            lastRead: null
        };
    }

    readingMetrics[essayId].views += 1;
    readingMetrics[essayId].totalReadingTime += readingTime;
    readingMetrics[essayId].maxProgress = Math.max(readingMetrics[essayId].maxProgress, readingProgress);
    readingMetrics[essayId].lastRead = new Date().toISOString();

    // Save to localStorage for backward compatibility
    localStorage.setItem('pgEssaysMetrics', JSON.stringify(readingMetrics));

    // Save to API if available
    if (window.pgEssaysApi) {
        window.pgEssaysApi.saveReadingMetrics(essayId, readingTime);
    }
}

// Update popular essays count (legacy method)
function updatePopularEssaysCount(essayId) {
    if (!essayId) return;

    // Get existing popular essays from localStorage (for backward compatibility)
    const popularEssays = JSON.parse(localStorage.getItem('pgEssaysPopular') || '{}');

    // Increment count
    popularEssays[essayId] = (popularEssays[essayId] || 0) + 1;

    // Save to localStorage for backward compatibility
    localStorage.setItem('pgEssaysPopular', JSON.stringify(popularEssays));

    // Note: We don't need to update Supabase here as it's handled by the markEssayAsCompleted function
}

// Get popular essays (for use in other scripts)
async function getPopularEssays(limit = 10) {
    // Try to get from API first
    if (window.pgEssaysApi) {
        try {
            const popularEssays = await window.pgEssaysApi.getPopularEssays(limit);
            if (popularEssays && popularEssays.length > 0) {
                return popularEssays.map(essay => essay.essay_id);
            }
        } catch (error) {
            console.error('Error getting popular essays from API:', error);
        }
    }

    // Fall back to localStorage if Supabase fails or is not available
    const popularEssays = JSON.parse(localStorage.getItem('pgEssaysPopular') || '{}');

    // Convert to array and sort by count
    return Object.entries(popularEssays)
        .map(([id, count]) => ({ id, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, limit)
        .map(item => item.id);
}
