#!/bin/sh

flask db upgrade

gunicorn --worker-class gevent \
  --workers 2 \
  --bind 0.0.0.0:$NAA_SERVER_PORT \
  auth.patched:app

# Run the main container process
exec "$@"
