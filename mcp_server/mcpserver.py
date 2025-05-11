import importlib
import os
from mcp.server.fastmcp import FastMCP

# 获取当前文件的同级目录（即mcp_server/mcp_server/）
# Get the current file's directory (i.e., mcp_server/mcp_server/)
base_dir = os.path.dirname(os.path.abspath(__file__))
tools_dir = os.path.join(base_dir, 'tools')

mcp = FastMCP("comfyui-mcp")

# 自动遍历tools目录下所有.py文件，注册为MCP工具
# Automatically traverse all .py files in the tools directory and register as MCP tools
for fname in os.listdir(tools_dir):
    if fname.endswith('.py') and not fname.startswith('__'):
        modname = fname[:-3]
        import_path = f"mcp_server.tools.{modname}"
        mod = importlib.import_module(import_path)
        register_func = getattr(mod, f"register_{modname}_tool", None)
        if register_func:
            register_func(mcp)

if __name__ == "__main__":
    # 以SSE模式启动MCP服务
    # Start MCP server in SSE mode
    mcp.run(transport='sse')
