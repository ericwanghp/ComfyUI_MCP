import functools
import time
import inspect
from typing import Any, Callable, Dict, TypeVar, cast, Optional
from .logger import default_logger

F = TypeVar('F', bound=Callable[..., Any])

def log_mcp_call(func: F) -> F:
    """
    装饰器：记录MCP工具调用和结果
    Decorator: Log MCP tool call and result
    
    参数:
        func: 要装饰的函数
    
    Args:
        func: Function to decorate
    
    返回:
        装饰后的函数
    
    Returns:
        Decorated function
    """
    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        # 获取工具名称
        # Get tool name
        tool_name = func.__name__
        
        # 获取调用参数
        # Get call parameters
        signature = inspect.signature(func)
        bound_args = signature.bind(*args, **kwargs)
        bound_args.apply_defaults()
        tool_args = dict(bound_args.arguments)
        
        # 排除self参数（如果存在）
        # Exclude self parameter (if exists)
        if 'self' in tool_args:
            del tool_args['self']
        
        # 记录调用
        # Log call
        default_logger.log_mcp_call(tool_name, tool_args)
        
        # 计算执行时间
        # Calculate execution time
        start_time = time.time()
        
        try:
            # 执行原函数
            # Execute original function
            result = await func(*args, **kwargs)
            
            # 计算执行时间（毫秒）
            # Calculate execution time (ms)
            execution_time = (time.time() - start_time) * 1000
            
            # 记录结果
            # Log result
            default_logger.log_mcp_result(tool_name, result, execution_time)
            
            return result
        except Exception as e:
            # 计算执行时间（毫秒）
            # Calculate execution time (ms)
            execution_time = (time.time() - start_time) * 1000
            
            # 记录错误
            # Log error
            default_logger.error(f"MCP工具 {tool_name} 执行失败: {str(e)}")
            
            # 重新抛出异常
            # Re-raise exception
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        # 获取工具名称
        # Get tool name
        tool_name = func.__name__
        
        # 获取调用参数
        # Get call parameters
        signature = inspect.signature(func)
        bound_args = signature.bind(*args, **kwargs)
        bound_args.apply_defaults()
        tool_args = dict(bound_args.arguments)
        
        # 排除self参数（如果存在）
        # Exclude self parameter (if exists)
        if 'self' in tool_args:
            del tool_args['self']
        
        # 记录调用
        # Log call
        default_logger.log_mcp_call(tool_name, tool_args)
        
        # 计算执行时间
        # Calculate execution time
        start_time = time.time()
        
        try:
            # 执行原函数
            # Execute original function
            result = func(*args, **kwargs)
            
            # 计算执行时间（毫秒）
            # Calculate execution time (ms)
            execution_time = (time.time() - start_time) * 1000
            
            # 记录结果
            # Log result
            default_logger.log_mcp_result(tool_name, result, execution_time)
            
            return result
        except Exception as e:
            # 计算执行时间（毫秒）
            # Calculate execution time (ms)
            execution_time = (time.time() - start_time) * 1000
            
            # 记录错误
            # Log error
            default_logger.error(f"MCP工具 {tool_name} 执行失败: {str(e)}")
            
            # 重新抛出异常
            # Re-raise exception
            raise
    
    # 根据原函数是否为异步函数选择对应的装饰器
    # Choose corresponding decorator based on whether the original function is async
    if inspect.iscoroutinefunction(func):
        return cast(F, async_wrapper)
    else:
        return cast(F, sync_wrapper)

def configure_logging(log_path: Optional[str] = None, 
                      console_output: bool = True, 
                      log_level: int = None) -> None:
    """
    配置MCP日志系统
    Configure MCP logging system
    
    参数:
        log_path: 日志文件路径，如果为None则使用默认路径
        console_output: 是否输出到控制台
        log_level: 日志级别，如果为None则使用默认级别
    
    Args:
        log_path: Path to log file, if None then use default path
        console_output: Whether to output to console
        log_level: Log level, if None then use default level
    """
    from .logger import MCPLogger
    import logging
    
    # 如果未指定日志级别，则使用默认日志级别
    # If log level is not specified, use default log level
    if log_level is None:
        log_level = logging.INFO
    
    # 如果未指定日志路径，则使用默认日志路径
    # If log path is not specified, use default log path
    if log_path is None:
        import os
        log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "mcp_server.log")
    
    # 替换默认日志记录器
    # Replace default logger
    global default_logger
    from .logger import default_logger as logger_instance
    default_logger = MCPLogger(log_path=log_path, console_output=console_output, log_level=log_level) 