#!/bin/bash
# local-stop.sh — 停止本地开发环境
#
# 用法:
#   ./scripts/local-stop.sh         # 停止后端 + 前端
#   ./scripts/local-stop.sh backend # 只停止后端
#   ./scripts/local-stop.sh frontend # 只停止前端

set -e

BACKEND_PORT=5000
FRONTEND_PORT=8080

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC}  $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }

stop_port() {
    local port=$1
    local name=$2
    local pids

    pids=$(lsof -i :"$port" | grep LISTEN | awk '{print $2}' | sort -u)
    if [ -n "$pids" ]; then
        for pid in $pids; do
            kill -9 "$pid" 2>/dev/null && log_ok "$name (PID: $pid, 端口: $port) 已停止"
        done
    else
        log_warn "$name 端口 $port 未运行"
    fi
}

main() {
    local mode="${1:-all}"

    case "$mode" in
        backend)
            log_info "停止后端服务..."
            stop_port $BACKEND_PORT "后端"
            ;;
        frontend)
            log_info "停止前端服务..."
            stop_port $FRONTEND_PORT "前端"
            ;;
        all)
            log_info "停止本地开发环境..."
            stop_port $FRONTEND_PORT "前端"
            stop_port $BACKEND_PORT "后端"
            log_ok "全部服务已停止"
            ;;
        *)
            echo "用法: $0 [backend|frontend|all]"
            exit 1
            ;;
    esac
}

main "$@"
