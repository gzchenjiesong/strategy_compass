#!/bin/bash
# local-status.sh — 查看本地开发环境状态
#
# 用法:
#   ./scripts/local-status.sh

BACKEND_PORT=5000
FRONTEND_PORT=8080

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_ok()    { echo -e "${GREEN}●${NC} $1"; }
log_error() { echo -e "${RED}●${NC} $1"; }
log_warn()  { echo -e "${YELLOW}●${NC} $1"; }
log_info()  { echo -e "  $1"; }

check_service() {
    local port=$1
    local name=$2
    local url=$3
    local pid_info

    pid_info=$(lsof -i :"$port" | grep LISTEN)

    if [ -n "$pid_info" ]; then
        local pid
        pid=$(echo "$pid_info" | awk '{print $2}' | head -1)
        local cmd
        cmd=$(echo "$pid_info" | awk '{print $1}' | head -1)

        # 尝试健康检查
        local health_status
        health_status=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")

        if [ "$health_status" = "200" ]; then
            log_ok "$name 运行中 (端口: $port, PID: $pid, 命令: $cmd)"
            log_info "访问: $url"
        else
            log_warn "$name 进程存在但响应异常 (端口: $port, PID: $pid, HTTP: $health_status)"
        fi
    else
        log_error "$name 未运行 (端口: $port)"
    fi
}

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║              Strategy Compass 本地环境状态               ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

check_service $BACKEND_PORT "后端" "http://127.0.0.1:$BACKEND_PORT/health"
echo ""
check_service $FRONTEND_PORT "前端" "http://127.0.0.1:$FRONTEND_PORT/"

echo ""
echo "───────────────────────────────────────────────────────────"
echo ""

# 检查 API 连通性
if curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:$BACKEND_PORT/health" | grep -q "200"; then
    log_ok "API 连通性正常"
    log_info "后端日志: backend/logs/flask.log"
else
    log_warn "API 连通性异常"
fi

echo ""
echo "常用命令:"
echo "  ./scripts/local-deploy.sh     启动服务"
echo "  ./scripts/local-stop.sh       停止服务"
echo "  ./scripts/local-restart.sh    重启服务"
echo "  ./scripts/api-check.sh        API 测试"
echo ""
