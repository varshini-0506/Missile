# Docker Setup Guide

This guide explains how to build and run the application in Docker.

## Prerequisites

- Docker installed on your system
- Environment variables configured (see below)

## Environment Variables

Create a `.env` file or set these environment variables when running Docker:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Google Custom Search API
GOOGLE_API_KEY=your-google-api-key
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id

# Optional: Country code for Google Search (default: 'in' for India)
# Set via code, not env var
```

## Building the Docker Image

```bash
cd finalDeploy
docker build -t crawlbot-app .
```

## Running the Docker Container

### Option 1: Using .env file

```bash
docker run --env-file .env crawlbot-app
```

### Option 2: Using environment variables directly

```bash
docker run \
  -e SUPABASE_URL=https://your-project.supabase.co \
  -e SUPABASE_KEY=your-supabase-anon-key \
  -e GOOGLE_API_KEY=your-google-api-key \
  -e GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id \
  crawlbot-app
```

### Option 3: Using docker-compose (recommended)

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  crawlbot:
    build: .
    container_name: crawlbot-app
    restart: unless-stopped
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - GOOGLE_SEARCH_ENGINE_ID=${GOOGLE_SEARCH_ENGINE_ID}
    volumes:
      # Optional: Mount logs directory if needed
      - ./logs:/app/logs
```

Then run:

```bash
docker-compose up
```

## Verifying the Setup

After starting the container, check the logs:

```bash
# If running with docker run
docker logs crawlbot-app

# If running with docker-compose
docker-compose logs -f
```

You should see:
- `[✓] Connected to Supabase`
- `[✓] Product Extractor initialized`
- `[✓] Category Search Pipeline thread started`
- `[✓] Product Extraction Pipeline thread started`

## Troubleshooting

### Chrome/Selenium Issues

If you see Selenium errors:
1. Verify Chrome is installed: `docker exec crawlbot-app google-chrome --version`
2. Check ChromeDriver: The `webdriver-manager` should automatically download the correct version

### Environment Variable Issues

If the application can't connect to Supabase:
1. Verify environment variables are set: `docker exec crawlbot-app env | grep SUPABASE`
2. Check that the values are correct and not wrapped in quotes

### Port Issues

This application doesn't expose any HTTP ports - it runs as a background service. No port mapping is needed.

## Stopping the Container

```bash
# Using docker run
docker stop crawlbot-app

# Using docker-compose
docker-compose down
```

## Updating the Application

1. Rebuild the image: `docker build -t crawlbot-app .`
2. Stop the old container: `docker stop crawlbot-app`
3. Run the new container with the same command as before

