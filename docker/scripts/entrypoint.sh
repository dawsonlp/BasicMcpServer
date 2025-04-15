#!/bin/bash
set -e

# Health check endpoint setup if needed
if [[ "$1" == "healthcheck" ]]; then
  python -c "import http.client; conn = http.client.HTTPConnection('localhost:7501'); conn.request('GET', '/health'); response = conn.getresponse(); exit(0 if response.status == 200 else 1)"
  exit $?
fi

# Run the application
exec python -m src.main
