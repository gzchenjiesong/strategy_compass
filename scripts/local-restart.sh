#!/bin/bash
# local-restart.sh — 重启本地开发环境
#
# 用法:
#   ./scripts/local-restart.sh           # 重启全部
#   ./scripts/local-restart.sh backend   # 只重启后端
#   ./scripts/local-restart.sh frontend  # 只重启前端
#   ./scripts/local-restart.sh --build   # 先构建再重启全部

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 颜色输出
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC}  $1"; }

main() {
    local mode="${1:-all}"

    case "$mode" in
        backend)
            log_info "重启后端..."
            "$SCRIPT_DIR/local-stop.sh" backend
            sleep 1
            "$SCRIPT_DIR/local-deploy.sh" backend
            ;;
        frontend)
            log_info "重启前端..."
            "$SCRIPT_DIR/local-stop.sh" frontend
            sleep 1
            "$SCRIPT_DIR/local-deploy.sh" frontend
            ;;
        --build)
            log_info "先构建前端，再重启全部..."
            "$SCRIPT_DIR/local-stop.sh"
            sleep 1
            "$SCRIPT_DIR/local-deploy.sh" --build
            ;;
        all)
            log_info "重启全部服务..."
            "$SCRIPT_DIR/local-stop.sh"
            sleep 1
            "$SCRIPT_DIR/local-deploy.sh"
            ;;
        *)
            echo "用法: $0 [backend|frontend|--build|all]"
            echo ""
            echo "  backend   只重启后端"
            echo "  frontend  只重启前端"
            echo "  --build   先构建前端再重启全部"
            echo "  all       重启全部（默认）"
            exit 1
            ;;
    esac
}

main "$@"
