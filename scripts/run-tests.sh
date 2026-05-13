#!/bin/bash

# 测试运行脚本
# 运行项目的单元测试和集成测试

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

# 检查Python环境
check_python_env() {
    log_info "检查Python环境..."

    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi

    # 检查虚拟环境
    if [ -d "backend/venv" ]; then
        log_info "激活虚拟环境..."
        source backend/venv/bin/activate
    elif [ -d "backend/.venv" ]; then
        log_info "激活虚拟环境..."
        source backend/.venv/bin/activate
    else
        log_warning "未找到虚拟环境，使用系统Python"
    fi

    # 检查pytest
    if ! python3 -m pytest --version &> /dev/null; then
        log_info "安装pytest..."
        pip install pytest
    fi

    log_success "Python环境检查完成"
}

# 运行单元测试
run_unit_tests() {
    log_info "运行单元测试..."

    cd backend

    # 运行单元测试
    python3 -m pytest tests/ -v --tb=short -m "unit" || {
        log_error "单元测试失败"
        cd ..
        return 1
    }

    log_success "单元测试通过"
    cd ..
    return 0
}

# 运行集成测试
run_integration_tests() {
    log_info "运行集成测试..."

    cd backend

    # 运行集成测试
    python3 -m pytest tests/ -v --tb=short -m "integration" || {
        log_error "集成测试失败"
        cd ..
        return 1
    }

    log_success "集成测试通过"
    cd ..
    return 0
}

# 运行所有测试
run_all_tests() {
    log_info "运行所有测试..."

    cd backend

    # 运行所有测试
    python3 -m pytest tests/ -v --tb=short || {
        log_error "测试失败"
        cd ..
        return 1
    }

    log_success "所有测试通过"
    cd ..
    return 0
}

# 生成测试覆盖率报告
generate_coverage_report() {
    log_info "生成测试覆盖率报告..."

    cd backend

    # 检查coverage是否安装
    if ! python3 -m coverage --version &> /dev/null; then
        log_info "安装coverage..."
        pip install coverage
    fi

    # 运行测试并生成覆盖率报告
    python3 -m coverage run -m pytest tests/ || {
        log_error "测试运行失败"
        cd ..
        return 1
    }

    # 生成报告
    python3 -m coverage report -m || {
        log_error "覆盖率报告生成失败"
        cd ..
        return 1
    }

    # 生成HTML报告
    python3 -m coverage html -d reports/coverage || {
        log_warning "HTML报告生成失败"
    }

    log_success "测试覆盖率报告已生成"
    cd ..
    return 0
}

# 清理测试文件
cleanup_test_files() {
    log_info "清理测试文件..."

    # 清理pytest缓存
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true

    # 清理测试数据库
    rm -f backend/test.db 2>/dev/null || true
    rm -f backend/app.db 2>/dev/null || true

    log_success "测试文件清理完成"
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -u, --unit          运行单元测试"
    echo "  -i, --integration   运行集成测试"
    echo "  -a, --all           运行所有测试"
    echo "  -c, --coverage      生成测试覆盖率报告"
    echo "  -C, --cleanup       清理测试文件"
    echo "  -h, --help          显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 -a               # 运行所有测试"
    echo "  $0 -u               # 运行单元测试"
    echo "  $0 -c               # 生成覆盖率报告"
}

# 主函数
main() {
    local run_unit=false
    local run_integration=false
    local run_all=false
    local generate_coverage=false
    local cleanup=false

    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -u|--unit)
                run_unit=true
                shift
                ;;
            -i|--integration)
                run_integration=true
                shift
                ;;
            -a|--all)
                run_all=true
                shift
                ;;
            -c|--coverage)
                generate_coverage=true
                shift
                ;;
            -C|--cleanup)
                cleanup=true
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

    # 如果没有指定选项，默认运行所有测试
    if [ "$run_unit" = false ] && [ "$run_integration" = false ] && [ "$run_all" = false ] && [ "$generate_coverage" = false ] && [ "$cleanup" = false ]; then
        run_all=true
    fi

    log_info "开始测试运行..."
    echo "=========================================="

    # 检查Python环境
    check_python_env

    # 清理测试文件
    if [ "$cleanup" = true ]; then
        cleanup_test_files
    fi

    # 运行测试
    local test_status=0

    if [ "$run_unit" = true ]; then
        run_unit_tests
        test_status=$((test_status + $?))
    fi

    if [ "$run_integration" = true ]; then
        run_integration_tests
        test_status=$((test_status + $?))
    fi

    if [ "$run_all" = true ]; then
        run_all_tests
        test_status=$((test_status + $?))
    fi

    if [ "$generate_coverage" = true ]; then
        generate_coverage_report
        test_status=$((test_status + $?))
    fi

    echo "=========================================="

    # 输出总结
    if [ $test_status -eq 0 ]; then
        log_success "测试运行完成！"
        exit 0
    else
        log_error "测试运行失败！"
        exit 1
    fi
}

# 执行主函数
main "$@"