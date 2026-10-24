#!/bin/sh
# Set the gandalf password from the environment (taken from the macOS Keychain
# by lab.sh at start-up, never baked into the image), then run sshd.
set -eu
if [ -z "${LAB_PASSWORD:-}" ]; then
  echo "LAB_PASSWORD is not set; start the targets with ./lab.sh" >&2
  exit 1
fi
echo "gandalf:${LAB_PASSWORD}" | chpasswd
unset LAB_PASSWORD

# Cron gives the seeded crontab a running daemon for live-state collection.
(command -v cron >/dev/null && cron) || (command -v crond >/dev/null && crond) || true

exec /usr/sbin/sshd -D -e
