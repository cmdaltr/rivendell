#!/bin/sh
# Install what Gandalf needs on a target: sshd, sudo, bash, python3, tar/gzip,
# sha256sum and zip. Creates the 'gandalf' user (password set at start-up).
set -eu

if command -v apt-get >/dev/null 2>&1; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get update
  apt-get install -y --no-install-recommends openssh-server openssh-client sudo bash python3 tar gzip coreutils zip unzip cron procps iproute2 ca-certificates
  rm -rf /var/lib/apt/lists/*
elif command -v dnf >/dev/null 2>&1; then
  dnf install -y --allowerasing openssh-server openssh-clients sudo bash python3 tar gzip coreutils zip unzip cronie procps-ng iproute passwd
  dnf clean all
else
  echo "Unsupported base image" >&2
  exit 1
fi

mkdir -p /run/sshd /var/run/sshd
ssh-keygen -A

if command -v useradd >/dev/null 2>&1; then
  useradd -m -s /bin/bash gandalf
else
  adduser -D -s /bin/bash gandalf
fi
# Gandalf's bash collector runs `sudo bash` over SSH with no TTY, so it needs NOPASSWD.
echo 'gandalf ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/gandalf
chmod 0440 /etc/sudoers.d/gandalf

sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
grep -q '^PasswordAuthentication yes' /etc/ssh/sshd_config || echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config
# Alpine's sshd needs this for password logins with a locked root.
grep -q '^KbdInteractiveAuthentication' /etc/ssh/sshd_config || echo 'KbdInteractiveAuthentication yes' >> /etc/ssh/sshd_config
