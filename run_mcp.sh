#!/bin/bash
# 启动 MCP 服务（支持 --Inspector 参数）
cd "$(dirname "$0")"

INSPECTOR=0
for arg in "$@"; do
  if [[ "$arg" == "--Inspector" ]]; then
    INSPECTOR=1
    break
  fi
done

if [[ $INSPECTOR -eq 1 ]]; then
  echo "启动 MCP Inspector..."
  npx @modelcontextprotocol/inspector uv run -m mcp_server.mcpserver
else
  python3 -m mcp_server.mcpserver
fi 