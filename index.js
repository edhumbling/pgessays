// Server-side routing for Netlify
// This file is used by Netlify to handle server-side routing

// Import required modules
const fs = require('fs');
const path = require('path');

// Define the routes
const routes = [
  { path: '/', file: 'index.html' },
  { path: '/essays', file: 'essays.html' },
  { path: '/download', file: 'download.html' },
  { path: '/about', file: 'about.html' },
  { path: '/404', file: '404.html' }
];

// Function to handle routing
exports.handler = async (event, context) => {
  const { path: requestPath } = event;
  
  // Check if the path matches any of our defined routes
  const route = routes.find(r => r.path === requestPath);
  
  if (route) {
    // If we have a defined route, serve the corresponding file
    const filePath = path.join(__dirname, route.file);
    const content = fs.readFileSync(filePath, 'utf8');
    
    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'text/html',
      },
      body: content,
    };
  }
  
  // Check if the path is for an essay
  if (requestPath.startsWith('/essays/') && requestPath.endsWith('.html')) {
    const essaySlug = requestPath.replace('/essays/', '').replace('.html', '');
    const filePath = path.join(__dirname, 'essays', `${essaySlug}.html`);
    
    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, 'utf8');
      
      return {
        statusCode: 200,
        headers: {
          'Content-Type': 'text/html',
        },
        body: content,
      };
    }
  }
  
  // If no route matches, serve the 404 page
  const notFoundPath = path.join(__dirname, '404.html');
  const notFoundContent = fs.readFileSync(notFoundPath, 'utf8');
  
  return {
    statusCode: 404,
    headers: {
      'Content-Type': 'text/html',
    },
    body: notFoundContent,
  };
};
