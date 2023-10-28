#!/usr/bin/env bash

if ! command -v docker-compose &> /dev/null
then
  echo "❌ docker-compose could not be found"
  exit 1
fi

if ! docker-compose --file dev-db/docker-compose.yaml down
then
  echo "❌ Couldn't stop the PostgreSQL container"
  exit 1
fi

echo '✅ PostgreSQL container is stopped'
