#!/bin/bash

# 设计文档同步检查脚本
# 用于验证设计文档与代码实现的一致性

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

# 检查设计文档是否存在
check_design_docs() {
    log_info "检查设计文档完整性..."

    local missing_docs=()

    # 检查模块设计文档
    for module in 0 1 2 3 4; do
        local doc_pattern="docs/modules/module-${module}-*.md"
        if ! ls $doc_pattern 1> /dev/null 2>&1; then
            missing_docs+=("Module $module 设计文档")
        fi
    done

    # 检查需求文档
    for module in 0 1 2 3 4; do
        local doc_pattern="docs/features/module-${module}-*.md"
        if ! ls $doc_pattern 1> /dev/null 2>&1; then
            missing_docs+=("Module $module 需求文档")
        fi
    done

    if [ ${#missing_docs[@]} -eq 0 ]; then
        log_success "所有设计文档存在"
        return 0
    else
        log_warning "缺少以下设计文档:"
        for doc in "${missing_docs[@]}"; do
            echo "  - $doc"
        done
        return 1
    fi
}

# 检查API接口一致性
check_api_consistency() {
    log_info "检查API接口一致性..."

    local issues=()

    # 从设计文档中提取API定义
    local design_apis=()
    for doc in docs/modules/module-*.md; do
        if [ -f "$doc" ]; then
            # 提取API路径
            local apis=$(grep -oE 'GET|POST|PUT|DELETE /api/v[0-9]+/[a-zA-Z/]+' "$doc" 2>/dev/null || true)
            if [ -n "$apis" ]; then
                while IFS= read -r api; do
                    design_apis+=("$api")
                done <<< "$apis"
            fi
        fi
    done

    # 从代码中提取API定义
    local code_apis=()
    for route_file in backend/app/routes/*.py; do
        if [ -f "$route_file" ]; then
            # 提取路由定义
            local routes=$(grep -oE '@bp\.route\("[^"]*"' "$route_file" 2>/dev/null || true)
            if [ -n "$routes" ]; then
                while IFS= read -r route; do
                    local path=$(echo "$route" | grep -oE '"/[^"]*"' | tr -d '"')
                    code_apis+=("$path")
                done <<< "$routes"
            fi
        fi
    done

    # 比较API定义
    for design_api in "${design_apis[@]}"; do
        local found=false
        for code_api in "${code_apis[@]}"; do
            if [[ "$design_api" == *"$code_api"* ]]; then
                found=true
                break
            fi
        done
        if [ "$found" = false ]; then
            issues+=("设计文档中的API '$design_api' 在代码中未找到")
        fi
    done

    if [ ${#issues[@]} -eq 0 ]; then
        log_success "API接口一致性检查通过"
        return 0
    else
        log_warning "发现以下API接口不一致:"
        for issue in "${issues[@]}"; do
            echo "  - $issue"
        done
        return 1
    fi
}

# 检查数据表一致性
check_table_consistency() {
    log_info "检查数据表一致性..."

    local issues=()

    # 从设计文档中提取表定义
    local design_tables=()
    for doc in docs/modules/module-*.md; do
        if [ -f "$doc" ]; then
            # 提取表名
            local tables=$(grep -oE 'CREATE TABLE [a-zA-Z_]+' "$doc" 2>/dev/null || true)
            if [ -n "$tables" ]; then
                while IFS= read -r table; do
                    local table_name=$(echo "$table" | awk '{print $3}')
                    design_tables+=("$table_name")
                done <<< "$tables"
            fi
        fi
    done

    # 从代码中提取表定义
    local code_tables=()
    for model_file in backend/app/models/*.py; do
        if [ -f "$model_file" ]; then
            # 提取表名
            local tables=$(grep -oE '__tablename__ = "[^"]*"' "$model_file" 2>/dev/null || true)
            if [ -n "$tables" ]; then
                while IFS= read -r table; do
                    local table_name=$(echo "$table" | grep -oE '"[^"]*"' | tr -d '"')
                    code_tables+=("$table_name")
                done <<< "$tables"
            fi
        fi
    done

    # 比较表定义
    for design_table in "${design_tables[@]}"; do
        local found=false
        for code_table in "${code_tables[@]}"; do
            if [ "$design_table" = "$code_table" ]; then
                found=true
                break
            fi
        done
        if [ "$found" = false ]; then
            issues+=("设计文档中的表 '$design_table' 在代码中未找到")
        fi
    done

    if [ ${#issues[@]} -eq 0 ]; then
        log_success "数据表一致性检查通过"
        return 0
    else
        log_warning "发现以下数据表不一致:"
        for issue in "${issues[@]}"; do
            echo "  - $issue"
        done
        return 1
    fi
}

# 检查功能完整性
check_feature_completeness() {
    log_info "检查功能完整性..."

    local issues=()

    # 检查需求文档中的功能是否实现
    for doc in docs/features/module-*.md; do
        if [ -f "$doc" ]; then
            local module_name=$(basename "$doc" .md)
            local features=$(grep -oE 'F[0-9]+: [^|]+' "$doc" 2>/dev/null || true)

            if [ -n "$features" ]; then
                while IFS= read -r feature; do
                    local feature_id=$(echo "$feature" | grep -oE 'F[0-9]+')
                    local feature_name=$(echo "$feature" | cut -d':' -f2 | xargs)

                    # 检查功能是否在代码中实现
                    if ! grep -r "$feature_name" backend/ 1> /dev/null 2>&1; then
                        issues+=("$module_name: 功能 '$feature_id: $feature_name' 可能未实现")
                    fi
                done <<< "$features"
            fi
        fi
    done

    if [ ${#issues[@]} -eq 0 ]; then
        log_success "功能完整性检查通过"
        return 0
    else
        log_warning "发现以下功能可能未实现:"
        for issue in "${issues[@]}"; do
            echo "  - $issue"
        done
        return 1
    fi
}

# 生成检查报告
generate_report() {
    log_info "生成检查报告..."

    local report_file="reports/design-sync-report-$(date +%Y%m%d-%H%M%S).md"
    mkdir -p reports

    cat > "$report_file" << EOF
# 设计文档同步检查报告

**检查时间**: $(date '+%Y-%m-%d %H:%M:%S')
**检查范围**: 设计文档与代码实现的一致性

## 检查结果摘要

$(if [ $overall_status -eq 0 ]; then echo "✅ **总体状态**: 通过"; else echo "⚠️ **总体状态**: 存在问题"; fi)

## 详细检查结果

### 1. 设计文档完整性
$(if [ $doc_status -eq 0 ]; then echo "✅ 通过"; else echo "⚠️ 存在问题"; fi)

### 2. API接口一致性
$(if [ $api_status -eq 0 ]; then echo "✅ 通过"; else echo "⚠️ 存在问题"; fi)

### 3. 数据表一致性
$(if [ $table_status -eq 0 ]; then echo "✅ 通过"; else echo "⚠️ 存在问题"; fi)

## 建议行动

1. 对于发现的问题，优先修复高优先级的不一致
2. 定期运行此检查脚本，确保文档与代码保持同步
3. 在代码审查流程中添加设计文档验证环节

## 附录

### 检查的文件

**设计文档**:
$(find docs/modules -name "*.md" -type f | sort | sed 's/^/- /')

**需求文档**:
$(find docs/features -name "*.md" -type f | sort | sed 's/^/- /')

**代码文件**:
$(find backend -name "*.py" -type f | sort | sed 's/^/- /')

EOF

    log_success "检查报告已生成: $report_file"
}

# 主函数
main() {
    log_info "开始设计文档同步检查..."
    echo "=========================================="

    # 执行各项检查
    check_design_docs
    doc_status=$?

    check_api_consistency
    api_status=$?

    check_table_consistency
    table_status=$?

    check_feature_completeness
    feature_status=$?

    # 计算总体状态
    overall_status=$((doc_status + api_status + table_status + feature_status))

    echo "=========================================="

    # 生成报告
    generate_report

    # 输出总结
    if [ $overall_status -eq 0 ]; then
        log_success "所有检查通过！设计文档与代码实现保持一致。"
        exit 0
    else
        log_warning "检查发现 $overall_status 个问题，请查看报告详情。"
        exit 1
    fi
}

# 执行主函数
main