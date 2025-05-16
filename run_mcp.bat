@echo off
REM 启动 MCP 服务
cd /d %~dp0

REM 检查是否带有 --Inspector 参数
set INSPECTOR=0
for %%i in (%*) do (
    if /I "%%i"=="--Inspector" set INSPECTOR=1
)

if %INSPECTOR%==1 (
    echo 启动 MCP Inspector...
    powershell -Command "Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass"
    npx @modelcontextprotocol/inspector uv run -m mcp_server.mcpserver
) else (
    python -m mcp_server.mcpserver
)
pause
