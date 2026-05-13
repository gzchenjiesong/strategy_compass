#!/bin/bash

# 日志清理脚本
# 清理30天前的日志文件，归档到archive目录

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 配置
LOG_DIR="agent/memory"
ARCHIVE_DIR="agent/memory/archive"
RETENTION_DAYS=30

# 检查目录是否存在
check_directories() {
    log_info "检查目录结构..."

    if [ ! -d "$LOG_DIR" ]; then
        log_error "日志目录不存在: $LOG_DIR"
        exit 1
    fi

    # 创建归档目录（如果不存在）
    mkdir -p "$ARCHIVE_DIR"

    log_success "目录检查完成"
}

# 清理日志文件
cleanup_logs() {
    log_info "清理 $RETENTION_DAYS 天前的日志文件..."

    local cleaned_count=0
    local archived_count=0

    # 查找并处理日志文件
    find "$LOG_DIR" -maxdepth 1 -name "*.md" -type f -mtime +$RETENTION_DAYS | while read file; do
        local filename=$(basename "$file")

        # 跳过特殊文件
        if [[ "$filename" == "README.md" ]] || [[ "$filename" == "session-framework.md" ]]; then
            log_info "跳过特殊文件: $filename"
            continue
        fi

        # 检查是否是日期格式的日志文件
        if [[ "$filename" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}\.md$ ]]; then
            log_info "归档日志文件: $filename"

            # 移动到归档目录
            mv "$file" "$ARCHIVE_DIR/"

            if [ $? -eq 0 ]; then
                archived_count=$((archived_count + 1))
                log_success "已归档: $filename"
            else
                log_error "归档失败: $filename"
            fi
        else
            log_info "跳过非日期格式文件: $filename"
        fi
    done

    log_success "日志清理完成。归档文件数: $archived_count"
}

# 压缩归档目录
compress_archive() {
    log_info "压缩归档目录..."

    local archive_date=$(date +%Y%m%d)
    local archive_file="logs/archive-$archive_date.tar.gz"

    # 创建logs目录
    mkdir -p logs

    # 压缩归档目录
    tar -czf "$archive_file" -C agent memory/archive 2>/dev/null || {
        log_warning "压缩失败，可能归档目录为空"
        return 0
    }

    log_success "归档压缩完成: $archive_file"
}

# 清理临时文件
cleanup_temp_files() {
    log_info "清理临时文件..."

    # 清理pytest缓存
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true

    # 清理测试数据库
    rm -f backend/test.db 2>/dev/null || true

    log_success "临时文件清理完成"
}

# 生成清理报告
generate_report() {
    log_info "生成清理报告..."

    local report_file="reports/log-cleanup-report-$(date +%Y%m%d-%H%M%S).md"
    mkdir -p reports

    cat > "$report_file" << EOF
# 日志清理报告

**清理时间**: $(date '+%Y-%m-%d %H:%M:%S')
**保留天数**: $RETENTION_DAYS 天

## 清理统计

- 归档目录: $ARCHIVE_DIR
- 归档文件数: $(find "$ARCHIVE_DIR" -name "*.md" -type f 2>/dev/null | wc -l | xargs)
- 压缩文件: logs/archive-$(date +%Y%m%d).tar.gz

## 保留的日志文件

$(find "$LOG_DIR" -maxdepth 1 -name "*.md" -type f -mtime -$RETENTION_DAYS | sort | sed 's/^/- /')

## 归档的日志文件

$(find "$ARCHIVE_DIR" -name "*.md" -type f 2>/dev/null | sort | sed 's/^/- /')

## 下次清理时间

$(date -v+${RETENTION_DAYS}d '+%Y-%m-%d')

EOF

    log_success "清理报告已生成: $report_file"
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -d, --days DAYS     设置保留天数（默认30天）"
    echo "  -a, --archive       仅归档，不压缩"
    echo "  -c, --compress      仅压缩已归档文件"
    echo "  -r, --report        仅生成报告"
    echo "  -h, --help          显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                  # 使用默认设置清理"
    echo "  $0 -d 7             # 保留最近7天的日志"
    echo "  $0 -a               # 仅归档，不压缩"
}

# 主函数
main() {
    local archive_only=false
    local compress_only=false
    local report_only=false

    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--days)
                RETENTION_DAYS="$2"
                shift 2
                ;;
            -a|--archive)
                archive_only=true
                shift
                ;;
            -c|--compress)
                compress_only=true
                shift
                ;;
            -r|--report)
                report_only=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done

    log_info "开始日志清理..."
    echo "=========================================="

    # 检查目录
    check_directories

    # 执行清理操作
    if [ "$archive_only" = true ]; then
        cleanup_logs
    elif [ "$compress_only" = true ]; then
        compress_archive
    elif [ "$report_only" = true ]; then
        generate_report
    else
        # 执行完整清理流程
        cleanup_logs
        compress_archive
        cleanup_temp_files
        generate_report
    fi

    echo "=========================================="
    log_success "日志清理完成！"
}

# 执行主函数
main "$@"