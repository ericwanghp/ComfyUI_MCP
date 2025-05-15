import json
import configparser
import os
import random
import logging
import httpx
import asyncio

def _get_config_parser():
    """
    获取配置解析器
    Get config parser
    
    返回:
        configparser.ConfigParser: 配置解析器
    
    Returns:
        configparser.ConfigParser: Config parser
    """
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'config.ini'), encoding='utf-8')
    return config

def load_comfyui_server_info():
    """
    加载ComfyUI服务器信息（主机和端口）
    Load ComfyUI server information (host and port)
    
    返回:
        tuple: (host, port)
    
    Returns:
        tuple: (host, port)
    """
    config = _get_config_parser()
    host = config.get('comfyui_server', 'host', fallback='127.0.0.1')
    port = config.get('comfyui_server', 'port', fallback='8188')
    return host, port

def load_config():
    """
    加载ComfyUI服务器URL
    Load ComfyUI server URL
    
    返回:
        str: ComfyUI服务器完整URL
    
    Returns:
        str: Complete ComfyUI server URL
    """
    host, port = load_comfyui_server_info()
    return f"http://{host}:{port}"

def load_uvicorn_config():
    """
    加载MCP服务器配置
    Load MCP server configuration
    
    返回:
        tuple: (host, port, transport)
    
    Returns:
        tuple: (host, port, transport)
    """
    config = _get_config_parser()
    uvicorn_host = config.get('mcp_server', 'host', fallback='0.0.0.0')
    uvicorn_port = config.getint('mcp_server', 'port', fallback=9000)
    transport = config.get('mcp_server', 'transport', fallback='sse')
    return uvicorn_host, uvicorn_port, transport

def load_logging_config():
    """
    加载日志配置
    Load logging configuration
    
    返回:
        dict 日志配置 | logging configuration
    
    Returns:
        dict logging configuration
    """
    config = _get_config_parser()
    
    # 获取日志级别
    # Get log level
    level_str = config.get('logging', 'level', fallback='INFO').upper()
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    level = level_map.get(level_str, logging.INFO)
    
    # 获取控制台输出设置
    # Get console output setting
    console_output = config.getboolean('logging', 'console_output', fallback=True)
    
    # 获取日志文件路径
    # Get log file path
    log_path = config.get('logging', 'log_path', fallback='logs/mcp_server.log')
    
    # 如果路径是相对路径，则转换为绝对路径
    # If path is relative, convert to absolute path
    if not os.path.isabs(log_path):
        log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), log_path)
    
    # 获取日志文件大小限制
    # Get log file size limit
    max_file_size = config.getint('logging', 'max_file_size', fallback=10*1024*1024)  # 默认10MB
    
    # 获取备份文件数量
    # Get backup count
    backup_count = config.getint('logging', 'backup_count', fallback=5)
    
    return {
        'level': level,
        'console_output': console_output,
        'log_path': log_path,
        'max_file_size': max_file_size,
        'backup_count': backup_count
    }

async def fetch_and_save_object_info(logger=None):
    """
    从ComfyUI服务器获取节点描述信息并保存到本地
    Fetch node description information from ComfyUI server and save it locally
    
    参数:
        logger: 日志记录器，如果为None则不记录日志
        
    Args:
        logger: Logger, if None, no logs will be recorded
    
    返回:
        bool: 是否成功获取并保存
        
    Returns:
        bool: Whether successfully fetched and saved
    """
    try:
        # 获取ComfyUI服务器信息
        # Get ComfyUI server information
        host, port = load_comfyui_server_info()
        comfyui_url = f"http://{host}:{port}"
        
        # 构建目标文件名
        # Build target filename
        object_info_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'object_info')
        os.makedirs(object_info_dir, exist_ok=True)
        
        object_info_filename = f"{host}_{port}_object_info.json"
        object_info_path = os.path.join(object_info_dir, object_info_filename)
        
        # 检查文件是否已存在
        # Check if the file already exists
        if os.path.exists(object_info_path):
            if logger:
                logger.info(f"ComfyUI节点描述文件已存在: {object_info_path}")
            return True
        
        # 从ComfyUI API获取节点描述信息
        # Get node description information from ComfyUI API
        object_info_url = f"{comfyui_url}/api/object_info"
        if logger:
            logger.info(f"正在从ComfyUI服务器获取节点描述信息: {object_info_url}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(object_info_url, timeout=30.0)
            
            if response.status_code != 200:
                if logger:
                    logger.error(f"获取ComfyUI节点描述信息失败，状态码: {response.status_code}")
                return False
            
            object_info = response.json()
            
            # 保存到文件
            # Save to file
            with open(object_info_path, 'w', encoding='utf-8') as f:
                json.dump(object_info, f, ensure_ascii=False, indent=2)
            
            if logger:
                logger.info(f"已成功获取并保存ComfyUI节点描述信息: {object_info_path}")
            
            return True
    
    except Exception as e:
        if logger:
            logger.error(f"获取ComfyUI节点描述信息时出错: {str(e)}")
        return False

def load_object_info(logger=None):
    """
    加载ComfyUI节点描述信息
    Load ComfyUI node description information
    
    参数:
        logger: 日志记录器，如果为None则不记录日志
    
    Args:
        logger: Logger, if None, no logs will be recorded
    
    返回:
        dict: 节点描述信息，如果加载失败则返回空字典
    
    Returns:
        dict: Node description information, empty dict if loading fails
    """
    try:
        # 获取ComfyUI服务器信息
        # Get ComfyUI server information
        host, port = load_comfyui_server_info()
        
        # 构建目标文件名
        # Build target filename
        object_info_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'object_info')
        object_info_filename = f"{host}_{port}_object_info.json"
        object_info_path = os.path.join(object_info_dir, object_info_filename)
        
        # 检查文件是否存在
        # Check if the file exists
        if not os.path.exists(object_info_path):
            if logger:
                logger.warning(f"ComfyUI节点描述文件不存在: {object_info_path}")
            return {}
        
        # 加载节点描述信息
        # Load node description information
        with open(object_info_path, 'r', encoding='utf-8') as f:
            object_info = json.load(f)
        
        if logger:
            logger.debug(f"已加载ComfyUI节点描述信息: {object_info_path}")
        
        return object_info
    
    except Exception as e:
        if logger:
            logger.error(f"加载ComfyUI节点描述信息时出错: {str(e)}")
        return {}

def load_prompt_template(api_name):
    # 加载指定API的prompt模板（JSON格式）
    # Load the prompt template (JSON) for the specified API
    with open(os.path.join(os.path.dirname(__file__), 'tools', f'{api_name}_api.json'), 'r', encoding='utf-8') as f:
        return json.load(f)

def randomize_all_seeds(prompt_template):
    # 遍历所有节点，递归随机化所有seed字段
    # Traverse all nodes and recursively randomize all seed fields
    for node in prompt_template.values():
        inputs = node.get("inputs", {})
        if "seed" in inputs:
            # 生成15位随机数
            # Generate a 15-digit random number
            inputs["seed"] = random.randint(10**14, 10**15 - 1)

async def init_mcp(logger=None):
    """
    初始化 MCP 服务环境，包括创建必要的目录结构和获取 ComfyUI 节点描述信息
    Initialize MCP service environment, including creating necessary directory structure and obtaining ComfyUI node description information
    
    参数:
        logger: 日志记录器，如果为None则不记录日志
        
    Args:
        logger: Logger, if None, no logs will be recorded
        
    返回:
        bool: 初始化是否成功
        
    Returns:
        bool: Whether initialization was successful
    """
    try:
        # 获取项目根目录和mcp_server目录
        # Get project root directory and mcp_server directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(base_dir)
        
        # 确保logs目录存在
        # Ensure logs directory exists
        logs_dir = os.path.join(root_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        
        # 确保object_info目录存在
        # Ensure object_info directory exists
        object_info_dir = os.path.join(root_dir, 'object_info')
        os.makedirs(object_info_dir, exist_ok=True)
        
        if logger:
            logger.info("====== MCP服务初始化开始 ======")
            logger.info("目录结构初始化完成")
        
        # 尝试获取ComfyUI节点描述信息
        # Try to fetch ComfyUI node description information
        if logger:
            logger.info("正在检查ComfyUI节点描述信息...")
        
        success = await fetch_and_save_object_info(logger)
        
        if success:
            if logger:
                logger.info("ComfyUI节点描述信息获取成功")
        else:
            if logger:
                logger.warning("无法获取ComfyUI节点描述信息，服务将继续启动")
        
        return True
    
    except Exception as e:
        if logger:
            logger.error(f"初始化MCP服务环境时出错: {str(e)}")
        return False

def get_tools_dir():
    """
    获取工具目录路径
    Get tools directory path
    
    返回:
        str: 工具目录的绝对路径
        
    Returns:
        str: Absolute path of tools directory
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, 'tools') 