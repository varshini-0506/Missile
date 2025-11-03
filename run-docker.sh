#!/bin/bash
# Bash script to run the Docker container (for Linux/Mac)

# Option 1: Run with environment variables
docker run --rm -it \
  -e SUPABASE_URL="https://whfjofihihlhctizchmj.supabase.co" \
  -e SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndoZmpvZmloaWhsaGN0aXpjaG1qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEzNzQzNDMsImV4cCI6MjA3Njk1MDM0M30.OsJnOqeJgT5REPg7uxkGmmVcHIcs5QO4vdyDi66qpR0" \
  -e GOOGLE_API_KEY="AIzaSyDvWUeUaMF7otiD1EYs5OzyJ1dQFfxgHu8" \
  -e GOOGLE_SEARCH_ENGINE_ID="858497242c8c04abc" \
  --name crawlbot-app \
  crawlbot-app

# Option 2: Run in detached mode (background)
# docker run -d \
#   -e SUPABASE_URL="https://whfjofihihlhctizchmj.supabase.co" \
#   -e SUPABASE_KEY="your-key" \
#   -e GOOGLE_API_KEY="your-key" \
#   -e GOOGLE_SEARCH_ENGINE_ID="your-id" \
#   --name crawlbot-app \
#   crawlbot-app

# View logs: docker logs -f crawlbot-app
# Stop: docker stop crawlbot-app
# Remove: docker rm crawlbot-app

