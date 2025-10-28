#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${REPO_ROOT}/.env"

info() { printf "\033[1;34m[INFO]\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33m[WARN]\033[0m %s\n" "$*"; }
error() { printf "\033[1;31m[ERROR]\033[0m %s\n" "$*"; }

ensure_docker() {
  if command -v docker >/dev/null 2>&1; then
    return
  fi

  info "Docker not detected. Installing Docker Engine via convenience script..."
  curl -fsSL https://get.docker.com | sh
}

ensure_docker_group_membership() {
  if ! getent group docker >/dev/null 2>&1; then
    sudo groupadd docker
  fi

  if id -nG "${USER}" | grep -qw docker; then
    return
  fi

  warn "Adding ${USER} to the docker group (a logout/login may be required)."
  sudo usermod -aG docker "${USER}"
  warn "Docker group membership updated. Please log out and log back in, then re-run this script."
  exit 0
}

ensure_compose_plugin() {
  if docker compose version >/dev/null 2>&1; then
    return
  fi

  info "Installing docker compose plugin..."
  sudo apt-get update
  sudo apt-get install -y docker-compose-plugin
}

ensure_env_file() {
  if [[ ! -f "${ENV_FILE}" ]]; then
    info "Creating .env from template (.env.example)."
    cp "${REPO_ROOT}/.env.example" "${ENV_FILE}"
    warn "Populate PICOVOICE_ACCESS_KEY (and other overrides) in .env, then re-run this script."
    exit 0
  fi

  if grep -q "replace-with-your-key" "${ENV_FILE}"; then
    error "PICOVOICE_ACCESS_KEY in .env is still set to the placeholder. Update it and re-run."
    exit 1
  fi
}

main() {
  cd "${REPO_ROOT}"
  ensure_docker
  ensure_docker_group_membership
  ensure_compose_plugin
  ensure_env_file

  info "Building and starting the voice assistant container..."
  docker compose up -d --build
  info "Deployment complete. The assistant will start automatically on boot (restart policy: unless-stopped)."
}

main "$@"
