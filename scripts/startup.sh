#!/bin/bash
set -e

# Start Gunicorn in the background
gunicorn \
    --bind :$PORT \
    --workers 1 \
    --threads 8 \
    --timeout 0 \
    --access-logfile - \
    --error-logfile - \
    --log-level debug \
    --capture-output \
    --enable-stdio-inheritance \
    "wsgi:application" &

# Wait for the application to be ready
for i in {1..30}; do
    if curl -s http://localhost:$PORT/health >/dev/null; then
        echo "Application is ready!"
        break
    fi
    echo "Waiting for application to be ready... (attempt $i/30)"
    sleep 2
done

# Keep the container running
wait
