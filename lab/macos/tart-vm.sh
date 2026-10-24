#!/usr/bin/env bash
# Apple silicon only: Linux and macOS target VMs with Tart.
#   tart-vm.sh create|start|stop|delete|status <linux|macos>
# Images are Cirrus Labs' public Tart images (default login admin/admin, which
# this script changes to the lab password once provisioned).
set -euo pipefail
. "$(dirname "$0")/../lib/common.sh"
load_config

action="${1:?create|start|stop|delete|status}"; kind="${2:?linux|macos}"
TART="$(tart_bin)"; [ -n "$TART" ] || die "Tart is not installed. Run: ./lab.sh install"
is_arm || die "Tart VMs need Apple silicon. On an Intel Mac the lab uses Vagrant + VirtualBox."

case "$kind" in
  linux) IMAGE="${TART_LINUX_IMAGE:-ghcr.io/cirruslabs/ubuntu:latest}"; PORT=2230; MEM=2048; CPU=2 ;;
  macos) IMAGE="${TART_MACOS_IMAGE:-ghcr.io/cirruslabs/macos-sequoia-base:latest}"; PORT=2231; MEM=4096; CPU=4 ;;
  *) die "kind must be linux or macos" ;;
esac
VM="rivendell-lab-$kind"
mkdir -p "$TART_HOME"
RUN_DIR="$LAB_CONFIG_DIR/run"; mkdir -p "$RUN_DIR"
SSH="$LAB_ROOT/lib/ssh.exp"

vm_exists() { "$TART" list --quiet 2>/dev/null | grep -qx "$VM"; }
vm_ip() { "$TART" ip "$VM" 2>/dev/null || true; }

wait_ip() {
  local i ip
  for i in $(seq 1 90); do ip="$(vm_ip)"; [ -n "$ip" ] && { echo "$ip"; return; }; sleep 2; done
  die "$VM did not get an IP address within 3 minutes"
}

start_forward() {
  local ip="$1" pidf="$RUN_DIR/forward-$PORT.pid"
  [ -f "$pidf" ] && kill "$(cat "$pidf")" 2>/dev/null || true
  nohup python3 "$LAB_ROOT/lib/forward.py" "$PORT" "$ip" 22 >"$RUN_DIR/forward-$PORT.log" 2>&1 &
  echo $! > "$pidf"
  ok "$VM SSH on 127.0.0.1:$PORT (-> $ip:22)"
}

start_vm() {
  if [ -z "$(vm_ip)" ]; then
    info "Starting $VM (headless)"
    nohup "$TART" run --no-graphics "$VM" >"$RUN_DIR/$VM.log" 2>&1 &
  fi
  local ip; ip="$(wait_ip)"
  start_forward "$ip"
}

provision() {
  local ip="$1" user=admin script remote
  require_password
  export LAB_SSH_PASSWORD="admin"
  # Already provisioned? The admin password will have been changed.
  if ! expect "$SSH" ssh "$user" "$ip" 22 true >/dev/null 2>&1; then
    export LAB_SSH_PASSWORD="$LAB_PASSWORD"
  fi
  info "Waiting for SSH on $ip"
  for _ in $(seq 1 60); do expect "$SSH" ssh "$user" "$ip" 22 true >/dev/null 2>&1 && break; sleep 3; done
  if [ "$kind" = "linux" ]; then
    for f in setup.sh entrypoint.sh; do expect "$SSH" scp "$user" "$ip" 22 "$LAB_ROOT/linux-targets/$f" "/tmp/$f" >/dev/null; done
    expect "$SSH" scp "$user" "$ip" 22 "$LAB_ROOT/linux-targets/seed/seed-artefacts.sh" /tmp/seed-artefacts.sh >/dev/null
    remote="echo '$LAB_SSH_PASSWORD' | sudo -S sh -c 'id gandalf >/dev/null 2>&1 || sh /tmp/setup.sh; sh /tmp/seed-artefacts.sh; echo gandalf:$LAB_PASSWORD | chpasswd; echo admin:$LAB_PASSWORD | chpasswd; systemctl restart ssh'"
  else
    expect "$SSH" scp "$user" "$ip" 22 "$LAB_ROOT/macos/seed-macos.sh" /tmp/seed-macos.sh >/dev/null
    remote="echo '$LAB_SSH_PASSWORD' | sudo -S env LAB_PASSWORD='$LAB_PASSWORD' sh /tmp/seed-macos.sh && echo '$LAB_SSH_PASSWORD' | sudo -S dscl . -passwd /Users/admin '$LAB_PASSWORD'"
  fi
  info "Provisioning $VM"
  expect "$SSH" ssh "$user" "$ip" 22 "$remote" | grep -v -i password || true
  ok "$VM provisioned: user 'gandalf', lab password; admin password changed to the lab password"
}

case "$action" in
  create)
    if ! vm_exists; then
      [ "$kind" = "macos" ] && warn "The macOS image is about 25 GB; the first pull takes a while."
      info "Pulling $IMAGE"
      "$TART" clone "$IMAGE" "$VM"
      "$TART" set "$VM" --memory "$MEM" --cpu "$CPU"
    else
      info "$VM already exists"
    fi
    start_vm
    provision "$(vm_ip)"
    ;;
  start) vm_exists || die "$VM doesn't exist; create it first"; start_vm ;;
  stop)
    "$TART" stop "$VM" 2>/dev/null || true
    [ -f "$RUN_DIR/forward-$PORT.pid" ] && kill "$(cat "$RUN_DIR/forward-$PORT.pid")" 2>/dev/null || true
    ok "$VM stopped" ;;
  delete)
    confirm "Delete $VM and its disk?" n || exit 0
    "$TART" stop "$VM" 2>/dev/null || true; "$TART" delete "$VM"; ok "$VM deleted" ;;
  status)
    if vm_exists; then echo "$VM: $([ -n "$(vm_ip)" ] && echo "running at $(vm_ip), SSH 127.0.0.1:$PORT" || echo stopped)"; else echo "$VM: not created"; fi ;;
  *) die "unknown action $action" ;;
esac
