#!/usr/bin/env bash
# ZeroMic 构建脚本 (Linux / macOS)
# 使用方法: chmod +x build.sh && ./build.sh

set -e

# 图标文件：Linux 用 png，macOS 用 icns
if [[ "$OSTYPE" == "darwin"* ]]; then
    ICON="icon.icns"
else
    ICON="icon.png"
fi

if [ ! -f "$ICON" ]; then
    echo "[警告] 未找到 $ICON，将跳过图标。"
    ICON_ARG=""
else
    ICON_ARG="-i $ICON"
fi

echo "=== 清理旧构建 ==="
rm -rf build dist *.spec

echo "=== 开始打包 ==="
pyinstaller \
    $ICON_ARG \
    --onefile \
    --add-data "webui:webui" \
    --hidden-import="engineio.async_drivers.threading" \
    main.py

echo "=== 打包完成 ==="
echo "可执行文件在: $(pwd)/dist/main"
