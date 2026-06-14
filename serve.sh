#!/bin/bash
# Offer捕手 · 本地静态服务（Cloud Studio 部署用）
# 监听 0.0.0.0 以便端口插件生成公网预览链接

PORT="${PORT:-8080}"
echo "启动静态服务: http://0.0.0.0:${PORT}"
echo "请在 Cloud Studio 左侧「端口」面板中打开 ${PORT} 端口的公网预览"

if command -v python3 &>/dev/null; then
  exec python3 -m http.server "$PORT" --bind 0.0.0.0
elif command -v python &>/dev/null; then
  exec python -m SimpleHTTPServer "$PORT"
else
  echo "未找到 Python，请安装 Python 3 后重试" >&2
  exit 1
fi
