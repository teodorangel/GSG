#!/usr/bin/env bash
set -euo pipefail

# Development startup script: starts db, api, and crawler services
if docker compose up --help 2>&1 | grep -q -- '--profile'; then
  docker compose -f docker-compose.dev.yml up --build --force-recreate --profile dev -d
else
  COMPOSE_PROFILES=dev docker-compose -f docker-compose.dev.yml up --build --force-recreate -d
fi 