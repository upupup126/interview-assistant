#!/bin/bash

# 面试助手部署脚本
# 支持本地Docker部署和云端部署

set -e

# 颜色输出
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

# 检查依赖
check_dependencies() {
    log_info "检查部署依赖..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    log_success "依赖检查通过"
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."
    
    mkdir -p data/{uploads,exports,templates,recordings}
    mkdir -p logs
    mkdir -p ssl
    
    log_success "目录创建完成"
}

# 构建Docker镜像
build_image() {
    log_info "构建Docker镜像..."
    
    docker build -t interview-assistant:latest .
    
    if [ $? -eq 0 ]; then
        log_success "Docker镜像构建成功"
    else
        log_error "Docker镜像构建失败"
        exit 1
    fi
}

# 本地部署
deploy_local() {
    log_info "开始本地部署..."
    
    # 停止现有容器
    docker-compose down 2>/dev/null || true
    
    # 启动服务
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        log_success "本地部署成功"
        log_info "API服务地址: http://localhost:8000"
        log_info "API文档地址: http://localhost:8000/docs"
    else
        log_error "本地部署失败"
        exit 1
    fi
}

# 生产环境部署
deploy_production() {
    log_info "开始生产环境部署..."
    
    # 停止现有容器
    docker-compose --profile production down 2>/dev/null || true
    
    # 启动生产环境服务
    docker-compose --profile production up -d
    
    if [ $? -eq 0 ]; then
        log_success "生产环境部署成功"
        log_info "服务地址: http://localhost"
        log_info "HTTPS地址: https://localhost (需要配置SSL证书)"
    else
        log_error "生产环境部署失败"
        exit 1
    fi
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 等待服务启动
    sleep 10
    
    # 检查API健康状态
    for i in {1..30}; do
        if curl -f http://localhost:8000/health &>/dev/null; then
            log_success "服务健康检查通过"
            return 0
        fi
        
        log_info "等待服务启动... ($i/30)"
        sleep 2
    done
    
    log_error "服务健康检查失败"
    return 1
}

# 显示日志
show_logs() {
    log_info "显示服务日志..."
    docker-compose logs -f
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    docker-compose down
    log_success "服务已停止"
}

# 清理资源
cleanup() {
    log_info "清理Docker资源..."
    
    # 停止容器
    docker-compose down
    
    # 删除镜像
    docker rmi interview-assistant:latest 2>/dev/null || true
    
    # 清理未使用的资源
    docker system prune -f
    
    log_success "清理完成"
}

# 备份数据
backup_data() {
    log_info "备份数据..."
    
    BACKUP_DIR="backup/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # 备份数据库和文件
    cp -r data/ "$BACKUP_DIR/"
    cp -r logs/ "$BACKUP_DIR/"
    
    # 创建压缩包
    tar -czf "${BACKUP_DIR}.tar.gz" "$BACKUP_DIR"
    rm -rf "$BACKUP_DIR"
    
    log_success "数据备份完成: ${BACKUP_DIR}.tar.gz"
}

# 恢复数据
restore_data() {
    if [ -z "$1" ]; then
        log_error "请指定备份文件路径"
        exit 1
    fi
    
    BACKUP_FILE="$1"
    
    if [ ! -f "$BACKUP_FILE" ]; then
        log_error "备份文件不存在: $BACKUP_FILE"
        exit 1
    fi
    
    log_info "恢复数据从: $BACKUP_FILE"
    
    # 停止服务
    docker-compose down
    
    # 解压备份
    tar -xzf "$BACKUP_FILE"
    
    # 恢复数据
    BACKUP_DIR=$(basename "$BACKUP_FILE" .tar.gz)
    cp -r "${BACKUP_DIR}/data/" ./
    cp -r "${BACKUP_DIR}/logs/" ./
    
    # 清理临时文件
    rm -rf "$BACKUP_DIR"
    
    log_success "数据恢复完成"
}

# 显示帮助信息
show_help() {
    echo "面试助手部署脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  build       构建Docker镜像"
    echo "  local       本地部署"
    echo "  production  生产环境部署"
    echo "  logs        显示服务日志"
    echo "  stop        停止服务"
    echo "  restart     重启服务"
    echo "  health      健康检查"
    echo "  backup      备份数据"
    echo "  restore     恢复数据 (需要指定备份文件)"
    echo "  cleanup     清理Docker资源"
    echo "  help        显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 build           # 构建镜像"
    echo "  $0 local           # 本地部署"
    echo "  $0 production      # 生产环境部署"
    echo "  $0 backup          # 备份数据"
    echo "  $0 restore backup.tar.gz  # 恢复数据"
}

# 主函数
main() {
    case "$1" in
        "build")
            check_dependencies
            create_directories
            build_image
            ;;
        "local")
            check_dependencies
            create_directories
            build_image
            deploy_local
            health_check
            ;;
        "production")
            check_dependencies
            create_directories
            build_image
            deploy_production
            health_check
            ;;
        "logs")
            show_logs
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            sleep 2
            deploy_local
            health_check
            ;;
        "health")
            health_check
            ;;
        "backup")
            backup_data
            ;;
        "restore")
            restore_data "$2"
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"