import logging
import os
import sys
import json
import datetime
import socket
import getpass
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, Optional, Union
from .utils import load_logging_config

class JournalctlFormatter(logging.Formatter):
    """
    自定义日志格式化器，输出符合Journalctl格式的日志
    Custom log formatter that outputs logs in Journalctl format
    """
    
    def __init__(self):
        super().__init__()
        self.hostname = socket.gethostname()
        self.username = getpass.getuser()
        self.process_name = "mcp-server"
        self.pid = os.getpid()
    
    def format(self, record: logging.LogRecord) -> str:
        # 转换Python日志级别到Syslog优先级
        # Convert Python log level to Syslog priority
        priority_map = {
            logging.DEBUG: 7,      # DEBUG -> DEBUG
            logging.INFO: 6,       # INFO -> INFO
            logging.WARNING: 4,    # WARNING -> WARNING
            logging.ERROR: 3,      # ERROR -> ERR
            logging.CRITICAL: 2,   # CRITICAL -> CRIT
        }
        priority = priority_map.get(record.levelno, 6)
        
        # 获取ISO格式的时间戳
        # Get timestamp in ISO format
        timestamp = datetime.datetime.fromtimestamp(record.created).isoformat()
        
        # 构建符合Journalctl格式的日志条目
        # Build log entry in Journalctl format
        entry = {
            "PRIORITY": priority,
            "TIMESTAMP": timestamp,
            "HOSTNAME": self.hostname,
            "USER": self.username,
            "SYSLOG_IDENTIFIER": self.process_name,
            "_PID": self.pid,
            "MESSAGE": record.getMessage(),
            "CODE_FILE": record.pathname,
            "CODE_LINE": record.lineno,
            "CODE_FUNC": record.funcName,
        }
        
        # 添加额外的字段（如果有的话）
        # Add extra fields (if any)
        if hasattr(record, 'mcp_call'):
            entry["MCP_CALL"] = record.mcp_call
        
        if hasattr(record, 'mcp_result'):
            entry["MCP_RESULT"] = record.mcp_result
            
        if hasattr(record, 'execution_time'):
            entry["EXECUTION_TIME_MS"] = record.execution_time
        
        # 将条目格式化为Journalctl样式的字符串
        # Format entry as Journalctl-style string
        parts = []
        for key, value in entry.items():
            if key == "MESSAGE":
                parts.append(f"{value}")
            elif isinstance(value, (dict, list)):
                parts.append(f"{key}={json.dumps(value)}")
            else:
                parts.append(f"{key}={value}")
        
        return " ".join(parts)

class MCPLogger:
    """
    MCP日志记录器，用于记录MCP调用和输出
    MCP logger for recording MCP calls and outputs
    """
    
    def __init__(self, log_path: Optional[str] = None, console_output: bool = True, log_level: int = logging.INFO, max_file_size: int = 10*1024*1024, backup_count: int = 5):
        """
        初始化MCP日志记录器
        Initialize the MCP logger
        
        参数:
            log_path: 日志文件路径，如果为None则只输出到控制台
            console_output: 是否输出到控制台
            log_level: 日志级别
            max_file_size: 最大日志文件大小（字节）
            backup_count: 备份文件数量
        
        Args:
            log_path: Path to log file, if None then output to console only
            console_output: Whether to output to console
            log_level: Log level
            max_file_size: Maximum log file size (bytes)
            backup_count: Number of backup files
        """
        self.logger = logging.getLogger("mcp_logger")
        self.logger.setLevel(log_level)
        
        # 文件用详细格式
        formatter_file = JournalctlFormatter()
        # 控制台用简单格式
        formatter_console = logging.Formatter('%(levelname)s %(message)s')
        
        # 清除现有的处理器
        # Clear existing handlers
        self.logger.handlers = []
        
        # 添加控制台处理器
        # Add console handler
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter_console)
            self.logger.addHandler(console_handler)
        
        # 添加文件处理器（如果提供了路径）
        # Add file handler (if path is provided)
        if log_path:
            # 确保日志目录存在
            # Ensure log directory exists
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            
            # 使用循环日志文件处理器
            # Use rotating file handler
            file_handler = RotatingFileHandler(
                log_path, 
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter_file)
            self.logger.addHandler(file_handler)
            self.logger.propagate = False
    
    def log_mcp_call(self, 
                     tool_name: str, 
                     tool_args: Dict[str, Any], 
                     level: int = logging.INFO) -> None:
        """
        记录MCP工具调用
        Log MCP tool call
        
        参数:
            tool_name: 工具名称
            tool_args: 工具参数
            level: 日志级别
        
        Args:
            tool_name: Tool name
            tool_args: Tool arguments
            level: Log level
        """
        record = logging.LogRecord(
            name="mcp_logger",
            level=level,
            pathname=__file__,
            lineno=0,
            msg=f"MCP调用: {tool_name}",
            args=(),
            exc_info=None
        )
        record.mcp_call = {
            "tool": tool_name,
            "args": tool_args
        }
        self.logger.handle(record)
    
    def log_mcp_result(self, 
                       tool_name: str, 
                       result: Any, 
                       execution_time: float,
                       level: int = logging.INFO) -> None:
        """
        记录MCP工具调用结果
        Log MCP tool call result
        
        参数:
            tool_name: 工具名称
            result: 调用结果
            execution_time: 执行时间（毫秒）
            level: 日志级别
        
        Args:
            tool_name: Tool name
            result: Call result
            execution_time: Execution time (ms)
            level: Log level
        """
        # 对于大型结果进行截断，避免日志过大
        # Truncate large results to avoid large logs
        result_str = str(result)
        if len(result_str) > 1000:
            result_str = result_str[:997] + "..."
            
        record = logging.LogRecord(
            name="mcp_logger",
            level=level,
            pathname=__file__,
            lineno=0,
            msg=f"MCP结果: {tool_name}",
            args=(),
            exc_info=None
        )
        record.mcp_result = result_str
        record.execution_time = round(execution_time, 2)
        self.logger.handle(record)
    
    def error(self, message: str) -> None:
        """记录错误日志 | Log error message"""
        self.logger.error(message)
    
    def info(self, message: str) -> None:
        """记录信息日志 | Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """记录警告日志 | Log warning message"""
        self.logger.warning(message)
    
    def debug(self, message: str) -> None:
        """记录调试日志 | Log debug message"""
        self.logger.debug(message)
    
    def critical(self, message: str) -> None:
        """记录严重错误日志 | Log critical message"""
        self.logger.critical(message)

# 创建默认日志记录器实例
# Create default logger instance
try:
    # 尝试从配置文件加载日志配置
    # Try to load logging configuration from config file
    config = load_logging_config()
    default_logger = MCPLogger(
        log_path=config['log_path'],
        console_output=config['console_output'],
        log_level=config['level'],
        max_file_size=config['max_file_size'],
        backup_count=config['backup_count']
    )
except Exception as e:
    # 如果配置加载失败，使用默认配置
    # If configuration loading fails, use default configuration
    print(f"加载日志配置失败，使用默认配置: {str(e)}")
    default_logger = MCPLogger(
        log_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "mcp_server.log"),
        console_output=True,
        log_level=logging.INFO
    ) 