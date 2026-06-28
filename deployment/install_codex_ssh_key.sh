#!/usr/bin/env bash
set -euo pipefail

KEY="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPgPUpTFKh79sMYwvMt03z7MLPF0MnomTylCzGC9CkFP codex-qimam-odoo-saas"
SSH_DIR="/root/.ssh"
AUTHORIZED_KEYS="${SSH_DIR}/authorized_keys"

if [ "$(id -u)" -ne 0 ]; then
  echo "Run this script as root." >&2
  exit 1
fi

mkdir -p "${SSH_DIR}"
chmod 700 "${SSH_DIR}"
touch "${AUTHORIZED_KEYS}"

if ! grep -qxF "${KEY}" "${AUTHORIZED_KEYS}"; then
  printf '%s\n' "${KEY}" >> "${AUTHORIZED_KEYS}"
fi

chmod 600 "${AUTHORIZED_KEYS}"

echo "Codex SSH key is installed for root."
tail -n 1 "${AUTHORIZED_KEYS}"
