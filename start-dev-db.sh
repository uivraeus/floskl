#!/usr/bin/env bash

set -euo pipefail

if ! command -v docker-compose &> /dev/null
then
  echo "❌ docker-compose could not be found"
  exit 1
fi

if ! docker-compose --file dev-db/docker-compose.yaml up -d
then
  echo "❌ Couln't start the PosgreSQL container"
  exit 1
fi

echo '✅ PostgreSQL container is running, check the logs by running "docker logs -f dev-db-db-1"'