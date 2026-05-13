#!/bin/bash
# local-deploy.sh — 启动本地开发环境
#
# 用法:
#   ./scripts/local-deploy.sh           # 启动后端 + 前端
#   ./scripts/local-deploy.sh backend   # 只启动后端
#   ./scripts/local-deploy.sh frontend  # 只启动前端（需后端已运行）
#   ./scripts/local-deploy.sh --build   # 先构建前端再启动
#
# 服务地址:
#   前端页面: http://127.0.0.1:8080
#   后端 API: http://127.0.0.1:5000
#   API 代理: http://127.0.0.1:8080/api/* → http://127.0.0.1:5000

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
DB_PATH="$BACKEND_DIR/data/strategy_compass.db"

BACKEND_PORT=5000
FRONTEND_PORT=8080

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info()  { echo -e "${BLUE}[INFO]${NC}  $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ── 检查后端虚拟环境 ──
check_backend_env() {
    if [ ! -d "$BACKEND_DIR/.venv" ]; then
        log_error "后端虚拟环境不存在: $BACKEND_DIR/.venv"
        echo "请先在 backend 目录执行: python -m venv .venv && .venv/bin/pip install -r requirements.txt"
        exit 1
    fi
}

# ── 检查数据库文件 ──
check_database() {
    if [ ! -f "$DB_PATH" ]; then
        log_warn "数据库文件不存在: $DB_PATH"
        log_info "请先执行初始化: cd backend && .venv/bin/python scripts/init_db.py"
        exit 1
    fi
}

# ── 检查端口占用 ──
check_port() {
    local port=$1
    local name=$2
    if lsof -i :"$port" | grep LISTEN > /dev/null 2>&1; then
        log_warn "$name 端口 $port 已被占用"
        lsof -i :"$port" | grep LISTEN | awk '{print "       PID:", $2, " 命令:", $1}'
        return 1
    fi
    return 0
}

# ── 启动后端 ──
start_backend() {
    log_info "启动后端服务..."
    check_port $BACKEND_PORT "后端" || return 1

    cd "$BACKEND_DIR"
    export FLASK_ENV=development
    export DATABASE_URL="sqlite:///$DB_PATH"
    export JWT_SECRET="dev-secret"
    export PYTHONPATH="$BACKEND_DIR"

    nohup "$BACKEND_DIR/.venv/bin/python" wsgi.py > "$BACKEND_DIR/logs/flask.log" 2>&1 &
    local pid=$!

    # 等待后端启动
    local retries=0
    while [ $retries -lt 30 ]; do
        if curl -s http://127.0.0.1:$BACKEND_PORT/health > /dev/null 2>&1; then
            log_ok "后端启动成功 (PID: $pid) → http://127.0.0.1:$BACKEND_PORT"
            return 0
        fi
        sleep 1
        retries=$((retries + 1))
    done

    log_error "后端启动失败，请检查日志: $BACKEND_DIR/logs/flask.log"
    return 1
}

# ── 构建前端 ──
build_frontend() {
    log_info "构建前端..."
    cd "$FRONTEND_DIR"
    npm run build 2>&1 | tail -5
    log_ok "前端构建完成 → $FRONTEND_DIR/dist"
}

# ── 启动前端 ──
start_frontend() {
    log_info "启动前端服务..."
    check_port $FRONTEND_PORT "前端" || return 1

    # 检查 dist 目录
    if [ ! -d "$FRONTEND_DIR/dist" ] || [ ! -f "$FRONTEND_DIR/dist/index.html" ]; then
        log_warn "前端 dist 目录不存在，先执行构建..."
        build_frontend
    fi

    # 内联 Python 静态服务器脚本
    python3 - "$FRONTEND_DIR/dist" $BACKEND_PORT $FRONTEND_PORT << 'PYEOF' &
import sys, os, http.server, socketserver, urllib.request

DIST_DIR = sys.argv[1]
BACKEND_PORT = sys.argv[2]
FRONTEND_PORT = sys.argv[3]
BACKEND_URL = f"http://127.0.0.1:{BACKEND_PORT}"

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/'):
            self._proxy('GET')
        else:
            self._static()
    
    def do_POST(self):
        if self.path.startswith('/api/'):
            self._proxy('POST')
        else:
            self.send_error(405)
    
    def do_OPTIONS(self):
        if self.path.startswith('/api/'):
            self._proxy('OPTIONS')
        else:
            self.send_error(405)
    
    def do_PUT(self):
        if self.path.startswith('/api/'):
            self._proxy('PUT')
        else:
            self.send_error(405)
    
    def do_DELETE(self):
        if self.path.startswith('/api/'):
            self._proxy('DELETE')
        else:
            self.send_error(405)

    def _proxy(self, method):
        try:
            url = BACKEND_URL + self.path
            headers = {k: v for k, v in self.headers.items() if k.lower() not in ('host', 'content-length')}
            data = None
            if method in ('POST', 'PUT', 'PATCH'):
                length = int(self.headers.get('Content-Length', 0))
                data = self.rfile.read(length)
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            with urllib.request.urlopen(req) as resp:
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() not in ('transfer-encoding', 'content-encoding'):
                        self.send_header(k, v)
                self.end_headers()
                self.wfile.write(resp.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            for k, v in e.headers.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_error(502, str(e))

    def _static(self):
        filepath = os.path.join(DIST_DIR, self.path.lstrip('/'))
        if os.path.isdir(filepath) or not os.path.exists(filepath):
            filepath = os.path.join(DIST_DIR, 'index.html')
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            self.send_response(200)
            if filepath.endswith('.js'):
                self.send_header('Content-Type', 'application/javascript')
            elif filepath.endswith('.css'):
                self.send_header('Content-Type', 'text/css')
            elif filepath.endswith('.html'):
                self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        except Exception:
            self.send_error(404)

os.chdir(DIST_DIR)
with socketserver.TCPServer(("", int(FRONTEND_PORT)), Handler) as httpd:
    httpd.serve_forever()
PYEOF

    local pid=$!
    sleep 2

    if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$FRONTEND_PORT/ | grep -q "200"; then
        log_ok "前端启动成功 (PID: $pid) → http://127.0.0.1:$FRONTEND_PORT"
    else
        log_error "前端启动失败"
        return 1
    fi
}

# ── 主流程 ──
main() {
    local mode="${1:-all}"
    local do_build=false

    if [ "$mode" = "--build" ]; then
        do_build=true
        mode="all"
    fi

    log_info "项目目录: $PROJECT_DIR"

    case "$mode" in
        backend)
            check_backend_env
            check_database
            start_backend
            ;;
        frontend)
            if [ "$do_build" = true ]; then
                build_frontend
            fi
            start_frontend
            ;;
        all)
            check_backend_env
            check_database
            start_backend
            if [ "$do_build" = true ]; then
                build_frontend
            fi
            start_frontend
            log_info ""
            log_ok "本地部署完成！"
            echo ""
            echo "  前端页面: http://127.0.0.1:$FRONTEND_PORT"
            echo "  后端 API: http://127.0.0.1:$BACKEND_PORT"
            echo "  API 代理: http://127.0.0.1:$FRONTEND_PORT/api/*"
            echo ""
            echo "  操作命令:"
            echo "    ./scripts/local-stop.sh      停止服务"
            echo "    ./scripts/local-status.sh    查看状态"
            echo "    ./scripts/api-check.sh       API 测试"
            ;;
        *)
            echo "用法: $0 [backend|frontend|--build|all]"
            echo ""
            echo "  backend   只启动后端"
            echo "  frontend  只启动前端"
            echo "  --build   先构建前端再启动全部"
            echo "  all       启动后端 + 前端（默认）"
            exit 1
            ;;
    esac
}

main "$@"
