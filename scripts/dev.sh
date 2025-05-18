#!/usr/bin/env bash
set -euo pipefail

# Load environment variables from .env.dev for variable substitution
if [ -f .env.dev ]; then
  set -o allexport
  source .env.dev
  set +o allexport
fi

# Create .env for Compose interpolation if missing
if [ ! -f .env ]; then
  cp .env.dev .env
fi

# Development startup script: starts db, api, and crawler services
# Use Docker Compose v2 if it supports profiles, else fallback to v1
if docker compose up --help 2>&1 | grep -q -- '--profile'; then
  docker compose --env-file .env.dev -f docker-compose.dev.yml down --remove-orphans
  docker compose --env-file .env.dev -f docker-compose.dev.yml up --build --force-recreate --profile dev -d
else
  COMPOSE_PROFILES=dev docker-compose --env-file .env.dev -f docker-compose.dev.yml down --remove-orphans
  COMPOSE_PROFILES=dev docker-compose --env-file .env.dev -f docker-compose.dev.yml up --build --force-recreate -d
fi 