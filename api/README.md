# Paul Graham Essays API Server

This API server provides a secure way to track reading metrics for the Paul Graham Essays website. It acts as a middleware between the client-side JavaScript and the Supabase database, ensuring that API keys are not exposed to the client.

## Setup

1. Install the required dependencies:
   ```
   pip install supabase
   ```

2. Set the Supabase service key as an environment variable:
   ```
   # Windows
   set SUPABASE_SERVICE_KEY=your_service_key_here

   # Linux/Mac
   export SUPABASE_SERVICE_KEY=your_service_key_here
   ```

3. Run the API server:
   ```
   python run_api_server.py
   ```

   Or with a specific port:
   ```
   python run_api_server.py --port 8080
   ```

   Or with a specific Supabase key:
   ```
   python run_api_server.py --supabase-key your_service_key_here
   ```

## API Endpoints

### GET /api/metrics/popular

Get a list of popular essays based on view count and completion count.

**Query Parameters:**
- `limit` (optional): Maximum number of essays to return (default: 10)

**Response:**
```json
[
  {
    "essay_id": "123",
    "essay_title": "How to Start a Startup",
    "view_count": 1500,
    "completion_count": 750
  },
  ...
]
```

### POST /api/metrics/start

Start tracking essay reading.

**Request Body:**
```json
{
  "essay_id": "123",
  "essay_title": "How to Start a Startup",
  "session_id": "abc123"
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "abc123"
}
```

### POST /api/metrics/progress

Update reading progress.

**Request Body:**
```json
{
  "essay_id": "123",
  "progress": 75,
  "session_id": "abc123"
}
```

**Response:**
```json
{
  "success": true
}
```

### POST /api/metrics/complete

Mark essay as completed.

**Request Body:**
```json
{
  "essay_id": "123",
  "session_id": "abc123"
}
```

**Response:**
```json
{
  "success": true
}
```

### POST /api/metrics/save

Save reading metrics.

**Request Body:**
```json
{
  "essay_id": "123",
  "reading_time": 300,
  "session_id": "abc123"
}
```

**Response:**
```json
{
  "success": true
}
```

## Security Considerations

- The API server uses the Supabase service key, which has full access to the database. This key is never exposed to the client.
- The client-side JavaScript only communicates with this API server, not directly with Supabase.
- Session IDs are generated on the client side and used to track anonymous users.
- In a production environment, you should:
  - Use HTTPS
  - Implement rate limiting
  - Add more robust error handling
  - Consider adding authentication for admin endpoints
