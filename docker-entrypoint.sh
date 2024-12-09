# Run migrations
python manage.py migrate

# Start Daphne for WebSocket
daphne -b 0.0.0.0 -p 8001 Roleplay.asgi:application &

# Start Gunicorn
gunicorn Roleplay.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --threads 2 \
    --timeout 60