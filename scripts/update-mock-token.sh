#!/bin/bash
# update-mock-token.sh — 更新前端 Mock Token
#
# 用法:
#   ./scripts/update-mock-token.sh                    # 自动生成新 token（365天有效期）
#   ./scripts/update-mock-token.sh <token>            # 使用指定 token
#   ./scripts/update-mock-token.sh --check            # 检查当前 token 是否过期
#
# 说明:
#   开发环境使用 mock token 绕过微信登录。token 有过期时间，
#   过期后用户登录会立即被踢回登录页。本脚本负责生成新 token
#   并同步更新到前端代码中。

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

LOGIN_VIEW="$FRONTEND_DIR/src/views/LoginView.vue"
REQUEST_TS="$FRONTEND_DIR/src/utils/request.ts"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC}  $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ── 生成新 token ──
generate_token() {
    local secret="${JWT_SECRET:-dev-secret}"
    local days="${1:-365}"

    if [ ! -d "$BACKEND_DIR/.venv" ]; then
        log_error "后端虚拟环境不存在: $BACKEND_DIR/.venv"
        exit 1
    fi

    log_info "生成新 mock token（有效期 ${days} 天）..."

    local token
    token=$(cd "$BACKEND_DIR" && .venv/bin/python -c "
import jwt, datetime, sys
payload = {
    'user_id': 1,
    'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=int('$days')),
    'iat': datetime.datetime.now(datetime.UTC)
}
token = jwt.encode(payload, '$secret', algorithm='HS256')
print(token)
" 2>/dev/null || true)

    if [ -z "$token" ]; then
        log_error "生成 token 失败，尝试备用方式..."
        # 备用：直接调用系统 python3
        token=$(python3 -c "
import jwt, datetime, sys
try:
    payload = {
        'user_id': 1,
        'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=int('$days')),
        'iat': datetime.datetime.now(datetime.UTC)
    }
    print(jwt.encode(payload, '$secret', algorithm='HS256'))
except ImportError:
    print('ERROR: PyJWT not installed', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null || true)
    fi

    if [ -z "$token" ] || [ "$token" = "ERROR: PyJWT not installed" ]; then
        log_error "无法生成 token，请确保 PyJWT 已安装: pip install PyJWT"
        exit 1
    fi

    echo "$token"
}

# ── 解析 token 查看过期时间 ──
decode_token() {
    local token=$1
    python3 -c "
import jwt, datetime, sys
try:
    decoded = jwt.decode('$token', options={'verify_signature': False})
    exp_ts = decoded.get('exp', 0)
    exp_dt = datetime.datetime.fromtimestamp(exp_ts, tz=datetime.timezone.utc)
    now = datetime.datetime.now(datetime.timezone.utc)
    remaining = exp_dt - now
    days = remaining.days
    hours = remaining.seconds // 3600
    print(f'用户ID: {decoded.get(\"user_id\")}')
    print(f'过期时间: {exp_dt.strftime(\"%Y-%m-%d %H:%M:%S UTC\")}')
    print(f'剩余时间: {days}天 {hours}小时')
    if exp_dt < now:
        print('状态: 已过期')
        sys.exit(1)
    else:
        print('状态: 有效')
        sys.exit(0)
except Exception as e:
    print(f'解析失败: {e}')
    sys.exit(2)
"
}

# ── 更新前端文件 ──
update_frontend() {
    local token=$1

    log_info "更新前端代码中的 mock token..."

    # 更新 LoginView.vue
    if [ -f "$LOGIN_VIEW" ]; then
        sed -i.bak "s/const mockToken = '.*/const mockToken = '${token}'/" "$LOGIN_VIEW"
        rm -f "${LOGIN_VIEW}.bak"
        log_ok "已更新: src/views/LoginView.vue"
    fi

    # 更新 request.ts
    if [ -f "$REQUEST_TS" ]; then
        sed -i.bak "s/token = '.*/token = '${token}'/" "$REQUEST_TS"
        rm -f "${REQUEST_TS}.bak"
        log_ok "已更新: src/utils/request.ts"
    fi
}

# ── 主流程 ──
main() {
    local mode="${1:-generate}"

    case "$mode" in
        --check)
            log_info "检查当前 mock token..."
            # 从 LoginView.vue 中提取当前 token
            current_token=$(grep -o "const mockToken = '[^']*'" "$LOGIN_VIEW" 2>/dev/null | sed "s/const mockToken = '//;s/'$//" || echo "")
            if [ -z "$current_token" ]; then
                log_error "无法提取当前 token"
                exit 1
            fi
            log_info "Token: ${current_token:0:50}..."
            decode_token "$current_token"
            ;;
        generate|"")
            local token
            token=$(generate_token)
            log_info "新 Token: ${token:0:50}..."
            echo ""
            decode_token "$token" || true
            echo ""
            update_frontend "$token"
            log_ok "Mock token 更新完成"
            echo ""
            log_warn "请重新构建前端: cd frontend && npm run build"
            echo "  或: ./scripts/local-restart.sh --build"
            ;;
        *)
            # 直接传入 token
            log_info "使用指定 token..."
            decode_token "$mode" || true
            echo ""
            update_frontend "$mode"
            log_ok "Mock token 更新完成"
            echo ""
            log_warn "请重新构建前端: cd frontend && npm run build"
            ;;
    esac
}

main "$@"
