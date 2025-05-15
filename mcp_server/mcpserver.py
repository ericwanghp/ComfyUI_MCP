import importlib
import os
import asyncio
from mcp.server.fastmcp import FastMCP
from .logger import default_logger
from .utils import load_logging_config, init_mcp, get_tools_dir, load_uvicorn_config
import logging

# 获取工具目录路径
# Get tools directory path
tools_dir = get_tools_dir()

# 异步初始化 MCP 服务环境
# Asynchronously initialize MCP service environment
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(init_mcp(default_logger))
except Exception as e:
    default_logger.error(f"初始化MCP服务环境时出错: {str(e)}")

mcp = FastMCP("comfyui-mcp")
# 从配置文件中读取MCP服务器的主机、端口和传输模式配置
# Load MCP server host, port and transport mode from configuration file
host, port, transport = load_uvicorn_config()
mcp.settings.port = port
mcp.settings.host = host

# 记录MCP服务器配置信息
# Log MCP server configuration information
default_logger.info(f"MCP服务器配置 - 主机: {host}, 端口: {port}, 传输模式: {transport}")

# 自动遍历tools目录下所有.py文件，注册为MCP工具
# Automatically traverse all .py files in the tools directory and register as MCP tools
tool_count = 0
for fname in os.listdir(tools_dir):
    if fname.endswith('.py') and not fname.startswith('__'):
        modname = fname[:-3]
        import_path = f"mcp_server.tools.{modname}"
        try:
            mod = importlib.import_module(import_path)
            register_func = getattr(mod, f"register_{modname}_tool", None)
            if register_func:
                register_func(mcp)
                tool_count += 1
                default_logger.info(f"成功注册MCP工具: {modname}")
            else:
                default_logger.warning(f"模块 {modname} 中未找到注册函数 register_{modname}_tool")
        except Exception as e:
            default_logger.error(f"注册MCP工具 {modname} 时出错: {str(e)}")

# 记录服务初始化信息
# Log service initialization information
default_logger.info(f"====== MCP服务已初始化完成，共加载 {tool_count} 个工具 ======")

if __name__ == "__main__":
    try:
        # 记录服务启动信息
        # Log service start information
        default_logger.info("====== MCP服务正在启动 ======")
        
        # 加载日志配置
        # Load logging configuration
        log_config = load_logging_config()
        default_logger.info(f"日志级别: {logging.getLevelName(log_config['level'])}")
        default_logger.info(f"日志文件: {log_config['log_path']}")
        
        # 显示MCP服务器配置
        # Display MCP server configuration
        default_logger.info(f"MCP服务器地址: {mcp.settings.host}:{mcp.settings.port}")
        
        # 启动MCP服务
        # Start MCP server
        default_logger.info(f"正在启动MCP服务，传输模式: {transport}")
        mcp.run(transport=transport)
    except Exception as e:
        # 记录服务异常信息
        # Log service exception information
        default_logger.critical(f"MCP服务启动失败: {str(e)}")
        raise
