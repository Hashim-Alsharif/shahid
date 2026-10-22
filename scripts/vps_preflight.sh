#!/bin/sh
# Read-only inventory. No installation, service restart, or configuration edit.
set -u
printf '\nOS\n'
cat /etc/os-release
printf '\nMemory\n'
free -h
printf '\nDisk\n'
df -h / /opt /var/lib
printf '\nLoad\n'
uptime
printf '\nListeners (80, 443, 8080, 8011)\n'
ss -ltn '( sport = :80 or sport = :443 or sport = :8080 or sport = :8011 )'
printf '\nExisting services\n'
systemctl is-active caddy rihlati nginx docker 2>/dev/null || true
printf '\nTools\n'
python3 --version
command -v caddy || true
command -v docker || true
printf '\nShahid DNS, if configured\n'
getent ahostsv4 shahid.rihlati.me || true
