#!/usr/bin/env bash
# LightMes Docker 部署脚本

set -e

ROOT_DIR=$(cd "$(dirname "$0")" && pwd)

echo "=== LightMes Docker 部署 ==="

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 检查环境变量文件
if [ ! -f "$ROOT_DIR/.env" ]; then
    echo ">>> 创建 .env 文件..."
    cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
    echo "请修改 .env 文件中的配置后重新运行"
    exit 1
fi

# 构建镜像
echo ">>> 构建 Docker 镜像..."
docker-compose build

# 启动服务
echo ">>> 启动服务..."
docker-compose up -d

# 等待服务启动
echo ">>> 等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo "=== 服务状态 ==="
docker-compose ps

echo ""
echo "=== 部署完成 ==="
echo "管理命令:"
echo "  查看状态: docker-compose ps"
echo "  查看日志: docker-compose logs -f celery-worker"
echo "  重启服务: docker-compose restart celery-worker"
echo "  停止服务: docker-compose down"
echo ""