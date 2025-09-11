# API Security Configuration

This document explains how to set up API key authentication for the HappyRobot application.

## Overview

The HappyRobot application now includes API key authentication to secure access to both the backend API and frontend. This is essential for production deployment, especially when hosting on AWS.

## Configuration

### 1. Backend Configuration

The backend uses environment variables to configure API key authentication:

```bash
# Required: Your secure API key
API_KEY=your-secure-api-key-here

# Optional: Enable/disable API key requirement (default: true)
REQUIRE_API_KEY=true
```

### 2. Frontend Configuration

The frontend uses Vite environment variables:

```bash
# Backend URL
VITE_API_URL=http://localhost:8000

# API key (must match backend)
VITE_API_KEY=your-secure-api-key-here
```

### 3. Environment Setup

1. **Copy the example configuration:**
   ```bash
   cp config.example.env .env
   ```

2. **Edit the `.env` file with your secure API key:**
   ```bash
   API_KEY=my-super-secure-api-key-2025
   VITE_API_KEY=my-super-secure-api-key-2025
   ```

3. **For development, you can disable API key requirement:**
   ```bash
   REQUIRE_API_KEY=false
   ```

## Usage

### Backend API

All API endpoints (except `/health`) now require the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/shipments
```

### Frontend

The frontend automatically includes the API key in all requests. No additional configuration needed.

### Python Scripts

The `create_load.py` script supports API key authentication:

```bash
# Using command line argument
python create_load.py --api-key "your-api-key" --sample

# Using environment variable
export API_KEY="your-api-key"
python create_load.py --sample
```

### Jupyter Notebook

The `api_testing_notebook.ipynb` includes API key configuration:

```python
API_KEY = "your-secure-api-key-here"
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-API-Key": API_KEY
}
```

## Security Best Practices

### 1. Generate a Strong API Key

```python
import secrets
import string

def generate_api_key(length=32):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# Generate a secure API key
api_key = generate_api_key()
print(f"Your API key: {api_key}")
```

### 2. Environment Variables

- **Never commit API keys to version control**
- Use environment variables or secure secret management
- Rotate API keys regularly

### 3. Production Deployment

For AWS deployment:

```bash
# Set environment variables in your deployment platform
API_KEY=your-production-api-key
REQUIRE_API_KEY=true
VITE_API_KEY=your-production-api-key
```

### 4. Network Security

- Use HTTPS in production
- Consider IP whitelisting for additional security
- Implement rate limiting
- Monitor API usage

## Error Handling

### Invalid API Key

```json
{
  "detail": "Invalid API key"
}
```

### Missing API Key

```json
{
  "detail": "API key required. Please provide X-API-Key header."
}
```

## Development vs Production

### Development Mode

For local development, you can disable API key requirement:

```bash
REQUIRE_API_KEY=false
```

This allows testing without authentication.

### Production Mode

Always enable API key authentication in production:

```bash
REQUIRE_API_KEY=true
API_KEY=your-secure-production-key
```

## Troubleshooting

### 1. Frontend Not Loading Data

Check that the API key is correctly set in the frontend environment:

```bash
# Check if environment variable is set
echo $VITE_API_KEY
```

### 2. Backend Rejecting Requests

Verify the API key matches between frontend and backend:

```bash
# Test with curl
curl -H "X-API-Key: your-api-key" http://localhost:8000/health
```

### 3. Environment Variables Not Loading

Make sure your `.env` file is in the correct location:

- Backend: Root directory of the project
- Frontend: Root directory of the frontend folder

## API Key Rotation

To rotate your API key:

1. Generate a new API key
2. Update the environment variables
3. Restart the backend and frontend
4. Update any external integrations

## Monitoring

Consider implementing:

- API key usage logging
- Failed authentication monitoring
- Rate limiting per API key
- Usage analytics

## Example Configuration Files

### Backend `.env`
```bash
API_KEY=happyrobot-prod-key-2025-xyz789
REQUIRE_API_KEY=true
```

### Frontend `.env`
```bash
VITE_API_URL=https://api.yourdomain.com
VITE_API_KEY=happyrobot-prod-key-2025-xyz789
```

### Docker Compose
```yaml
environment:
  - API_KEY=happyrobot-prod-key-2025-xyz789
  - REQUIRE_API_KEY=true
  - VITE_API_KEY=happyrobot-prod-key-2025-xyz789
```

This security setup ensures that your HappyRobot application is properly protected when deployed to AWS or any other production environment.
