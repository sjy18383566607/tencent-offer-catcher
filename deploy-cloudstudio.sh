#!/bin/bash
# Offer捕手 · 腾讯云 Cloud Studio 一键启动脚本
# 用法：在 Cloud Studio 终端执行 bash deploy-cloudstudio.sh

set -e
cd "$(dirname "$0")"
PORT="${PORT:-8080}"

echo "=========================================="
echo " Offer捕手 · Cloud Studio 部署"
echo "=========================================="
echo ""
echo "【1】确认项目文件："
ls -lh index.html tencent_jobs.json serve.sh 2>/dev/null || true
echo ""
echo "【2】启动静态服务（端口 ${PORT}）..."
echo ""
echo "【3】开启公网访问："
echo "  → 点击左侧「端口」面板"
echo "  → 找到端口 ${PORT}，点击「公网访问」/「预览」"
echo "  → 复制生成的链接（格式类似 https://8080-xxxxx.cloudstudio.work）"
echo ""
echo "【4】作业提交示例："
echo "  作业一（主应用）：<公网链接>/index.html"
echo "  作业二（方案说明）：<公网链接>/doc.html"
echo ""
echo "服务启动中，按 Ctrl+C 停止..."
echo "=========================================="

exec bash serve.sh
