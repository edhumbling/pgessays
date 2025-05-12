// Secure API client for Paul Graham Essays website

// API configuration
const API_BASE_URL = 'api/metrics';

// Session ID for anonymous users
let sessionId = null;

// Initialize API client
async function initApiClient() {
    // Generate or retrieve session ID
    sessionId = getOrCreateSessionId();

    console.log('API client initialized');
    return true;
}

// Generate or retrieve session ID
function getOrCreateSessionId() {
    let id = localStorage.getItem('pgEssaysSessionId');

    if (!id) {
        id = generateUUID();
        localStorage.setItem('pgEssaysSessionId', id);
    }

    return id;
}

// Generate a UUID
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// Start tracking essay reading
async function startReadingTracking(essayId, essayTitle) {
    try {
        await initApiClient();

        const response = await fetch(`${API_BASE_URL}/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                essay_id: essayId,
                essay_title: essayTitle,
                session_id: sessionId
            })
        });

        const data = await response.json();

        if (data.error) {
            console.error('Error tracking reading start:', data.error);
        }
    } catch (error) {
        console.error('Error tracking reading start:', error);
    }
}

// Update reading progress
async function updateReadingProgress(essayId, progress) {
    try {
        await initApiClient();

        const response = await fetch(`${API_BASE_URL}/progress`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                essay_id: essayId,
                progress: progress,
                session_id: sessionId
            })
        });

        const data = await response.json();

        if (data.error) {
            console.error('Error updating reading progress:', data.error);
        }
    } catch (error) {
        console.error('Error updating reading progress:', error);
    }
}

// Mark essay as completed
async function markEssayAsCompleted(essayId) {
    try {
        await initApiClient();

        const response = await fetch(`${API_BASE_URL}/complete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                essay_id: essayId,
                session_id: sessionId
            })
        });

        const data = await response.json();

        if (data.error) {
            console.error('Error marking essay as completed:', data.error);
        }
    } catch (error) {
        console.error('Error marking essay as completed:', error);
    }
}

// Save reading metrics
async function saveReadingMetrics(essayId, readingTime) {
    try {
        await initApiClient();

        const response = await fetch(`${API_BASE_URL}/save`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                essay_id: essayId,
                reading_time: readingTime,
                session_id: sessionId
            })
        });

        const data = await response.json();

        if (data.error) {
            console.error('Error saving reading metrics:', data.error);
        }
    } catch (error) {
        console.error('Error saving reading metrics:', error);
    }
}

// Get popular essays
async function getPopularEssays(limit = 10) {
    try {
        await initApiClient();

        const response = await fetch(`${API_BASE_URL}/popular?limit=${limit}`);
        const data = await response.json();

        if (data.error) {
            console.error('Error fetching popular essays:', data.error);
            return [];
        }

        return data || [];
    } catch (error) {
        console.error('Error getting popular essays:', error);
        return [];
    }
}

// Export functions
window.pgEssaysApi = {
    initApiClient,
    startReadingTracking,
    updateReadingProgress,
    markEssayAsCompleted,
    saveReadingMetrics,
    getPopularEssays
};
