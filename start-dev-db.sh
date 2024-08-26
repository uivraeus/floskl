#!/usr/bin/env bash

set -euo pipefail

# Check prerequisites
if ! command -v docker-compose &> /dev/null
then
  echo "❌ docker-compose could not be found"
  exit 1
fi

# Do the work
if ! docker-compose --file dev-db/docker-compose.yaml up -d
then
  echo "❌ Couldn't start the PostgreSQL container"
  exit 1
fi

ip_address=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' dev-db_postgres)
echo "✅ PostgreSQL container is running"
echo "   - Connect via \"localhost\" or ${ip_address}, port 5432"
echo "   - Check the logs by running \"docker logs -f dev-db_postgres\""