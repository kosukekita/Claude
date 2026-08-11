#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
destination="${CONFIG_AUDIT_SYSTEMD_USER_DIR:-${HOME}/.config/systemd/user}"

install -d -m 0755 "$destination"
install -m 0644 "$script_dir/config-audit.service" "$destination/config-audit.service"
install -m 0644 "$script_dir/config-audit.timer" "$destination/config-audit.timer"
systemctl --user daemon-reload
systemctl --user enable --now config-audit.timer

printf 'Installed and enabled config-audit.timer\n'
