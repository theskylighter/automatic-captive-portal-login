#!/bin/bash
# Captive Portal Auto-Login - Linux Service Manager (systemd user service)
# Manages 24/7 background persistence across restarts without requiring sudo

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SERVICE_NAME="captive-portal-login.service"
SYSTEMD_USER_DIR="${HOME}/.config/systemd/user"
SERVICE_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}"
LOGIN_SH="${PROJECT_ROOT}/linux/login.sh"
LOG_DIR="${PROJECT_ROOT}/log"

check_systemd() {
    if ! command -v systemctl &> /dev/null; then
        echo "❌ systemctl command not found. systemd is required for user services."
        exit 1
    fi
}

install_service() {
    check_systemd
    echo "⚙️ Installing 24/7 systemd user service..."
    mkdir -p "${SYSTEMD_USER_DIR}"
    mkdir -p "${LOG_DIR}"

    cat > "${SERVICE_FILE}" << EOF
[Unit]
Description=Captive Portal Auto-Login (24/7)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/bin/bash ${LOGIN_SH}
WorkingDirectory=${PROJECT_ROOT}
Restart=always
RestartSec=5s
StandardOutput=append:${LOG_DIR}/service.out.log
StandardError=append:${LOG_DIR}/service.err.log

[Install]
WantedBy=default.target
EOF

    echo "✅ Service file created at ${SERVICE_FILE}"
    systemctl --user daemon-reload
    systemctl --user enable "${SERVICE_NAME}"
    systemctl --user restart "${SERVICE_NAME}"

    # Enable lingering so service runs across reboots even before graphical login
    if command -v loginctl &> /dev/null; then
        loginctl enable-linger "${USER}" 2>/dev/null || true
    fi

    echo "🚀 Service installed and started!"
    echo "   Status: ./linux/service.sh status"
    echo "   Logs:   ./linux/service.sh logs"
}

status_service() {
    check_systemd
    systemctl --user status "${SERVICE_NAME}" --no-pager
}

start_service() {
    check_systemd
    systemctl --user start "${SERVICE_NAME}"
    echo "✅ Service started."
}

stop_service() {
    check_systemd
    systemctl --user stop "${SERVICE_NAME}"
    echo "🛑 Service stopped."
}

restart_service() {
    check_systemd
    systemctl --user restart "${SERVICE_NAME}"
    echo "🔄 Service restarted."
}

logs_service() {
    check_systemd
    echo "📋 Showing live service logs (Press Ctrl+C to exit)..."
    journalctl --user -u "${SERVICE_NAME}" -f
}

uninstall_service() {
    check_systemd
    echo "🗑️ Removing systemd user service..."
    systemctl --user stop "${SERVICE_NAME}" 2>/dev/null || true
    systemctl --user disable "${SERVICE_NAME}" 2>/dev/null || true
    rm -f "${SERVICE_FILE}"
    systemctl --user daemon-reload
    echo "✅ Service uninstalled."
}

case "$1" in
    install)
        install_service
        ;;
    status)
        status_service
        ;;
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    logs|log)
        logs_service
        ;;
    uninstall|remove)
        uninstall_service
        ;;
    *)
        echo "Captive Portal Linux Service Manager"
        echo ""
        echo "Usage: ./linux/service.sh [command]"
        echo ""
        echo "Commands:"
        echo "  install    - Install and enable 24/7 auto-login service (starts at boot)"
        echo "  status     - Check current service status"
        echo "  start      - Start the service"
        echo "  stop       - Stop the service"
        echo "  restart    - Restart the service"
        echo "  logs       - Follow live journal logs"
        echo "  uninstall  - Remove the service"
        echo ""
        exit 1
        ;;
esac
