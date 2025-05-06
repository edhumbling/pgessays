// Netlify function to handle routing
exports.handler = async (event, context) => {
  const path = event.path;
  
  // Redirect all paths to the index.html file
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'text/html',
      'X-Redirected-By': 'Netlify Function'
    },
    body: `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="utf-8">
          <title>Redirecting...</title>
          <script>
            // Get the current path
            const path = window.location.pathname;
            
            // Redirect to the appropriate page
            if (path.startsWith('/essays/') && path.endsWith('.html')) {
              window.location.href = path;
            } else if (path === '/essays' || path === '/essays/') {
              window.location.href = '/essays.html';
            } else if (path === '/download' || path === '/download/') {
              window.location.href = '/download.html';
            } else if (path === '/about' || path === '/about/') {
              window.location.href = '/about.html';
            } else if (path !== '/' && !path.endsWith('.html')) {
              window.location.href = '/';
            }
          </script>
          <meta http-equiv="refresh" content="0;url=/" />
        </head>
        <body>
          <p>Redirecting to the home page...</p>
        </body>
      </html>
    `
  };
};
