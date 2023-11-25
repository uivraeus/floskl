#!/usr/bin/env bash

# Check prerequisites
if ! command -v docker-compose &> /dev/null
then
  echo "❌ docker-compose could not be found"
  exit 1
fi

# Parse (optional) arguments
# https://www.baeldung.com/linux/bash-parse-command-line-arguments#parsing-long-command-line-options-with-getopt
VALID_ARGS=$(getopt -o d --long delete -- "$@")
if [[ $? -ne 0 ]]; then
    exit 1;
fi

eval set -- "$VALID_ARGS"
while [ : ]; do
  case "$1" in
    -d | --delete)
        DOWN_ARGS="--volumes"
        shift
        ;;
    --) shift; 
        break 
        ;;
  esac
done

# Do the work
if ! docker-compose --file dev-db/docker-compose.yaml down ${DOWN_ARGS}
then
  echo "❌ Couldn't stop the PostgreSQL container"
  exit 1
fi

echo '✅ PostgreSQL container is stopped'
