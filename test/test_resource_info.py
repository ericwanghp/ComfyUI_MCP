import os
import sys
import asyncio
import inspect

# 将父目录添加到路径以便导入mcp_server模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# 定义一个简单的MCP模拟类
class MockMCP:
    def __init__(self):
        self.resources = {}
    
    def resource(self, resource_uri):
        def decorator(func):
            self.resources[resource_uri] = func
            return func
        return decorator

# 从测试中导入modules需要将mcp_server添加到sys.modules
import sys
import types
if 'mcp_server' not in sys.modules:
    sys.modules['mcp_server'] = types.ModuleType('mcp_server')
if 'mcp_server.tools' not in sys.modules:
    sys.modules['mcp_server.tools'] = types.ModuleType('mcp_server.tools')
if 'mcp_server.logger_decorator' not in sys.modules:
    sys.modules['mcp_server.logger_decorator'] = types.ModuleType('mcp_server.logger_decorator')
    
    # 创建模拟的log_mcp_call装饰器
    def log_mcp_call(func):
        def wrapper(*args, **kwargs):
            print(f"调用: {func.__name__}")
            result = func(*args, **kwargs)
            print(f"结果: {func.__name__}")
            return result
        return wrapper
    
    sys.modules['mcp_server.logger_decorator'].log_mcp_call = log_mcp_call

if 'mcp_server.logger' not in sys.modules:
    sys.modules['mcp_server.logger'] = types.ModuleType('mcp_server.logger')
    
    # 创建模拟的logger
    class MockLogger:
        def info(self, msg):
            print(f"INFO: {msg}")
        
        def error(self, msg):
            print(f"ERROR: {msg}")
        
        def debug(self, msg):
            print(f"DEBUG: {msg}")
    
    sys.modules['mcp_server.logger'].default_logger = MockLogger()

if 'mcp_server.utils' not in sys.modules:
    sys.modules['mcp_server.utils'] = types.ModuleType('mcp_server.utils')
    
    # 创建模拟的load_object_info和load_config函数
    def load_object_info(logger):
        try:
            object_info_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'object_info', '127.0.0.1_8188_object_info.json')
            if not os.path.exists(object_info_path):
                logger.error(f"未找到对象信息文件: {object_info_path}")
                return None
            
            with open(object_info_path, 'r', encoding='utf-8') as f:
                import json
                return json.load(f)
        except Exception as e:
            logger.error(f"加载对象信息时出错: {str(e)}")
            return None
    
    def load_config():
        return "http://127.0.0.1:8188"
    
    sys.modules['mcp_server.utils'].load_object_info = load_object_info
    sys.modules['mcp_server.utils'].load_config = load_config

# 直接定义资源获取函数
def register_resource_info_tool(mcp):
    from mcp_server.logger_decorator import log_mcp_call
    from mcp_server.logger import default_logger
    from mcp_server.utils import load_object_info, load_config
    
    @mcp.resource("info://ckpt")
    @log_mcp_call
    async def get_checkpoint_list() -> str:
        """
        获取ComfyUI模型清单
        Get ComfyUI checkpoint model list
        
        Returns:
            str 格式化的模型清单 | Formatted checkpoint list
        """
        try:
            # 加载节点描述信息
            # Load node description information
            object_info = load_object_info(default_logger)
            
            if not object_info:
                return "无法加载ComfyUI节点描述信息，请确保MCP服务已成功从ComfyUI获取节点描述信息。"
            
            # 获取CheckpointLoaderSimple节点的ckpt_name选项
            # Get ckpt_name options from CheckpointLoaderSimple node
            if "CheckpointLoaderSimple" not in object_info:
                return "未找到CheckpointLoaderSimple节点，无法获取模型清单。"
            
            node_info = object_info["CheckpointLoaderSimple"]
            
            # 检查input和required字段
            if "input" not in node_info:
                return "CheckpointLoaderSimple节点中未找到input字段。"
                
            input_info = node_info["input"]
            
            if "required" not in input_info:
                return "CheckpointLoaderSimple节点中未找到required字段。"
                
            required_info = input_info["required"]
            
            if "ckpt_name" not in required_info:
                return "CheckpointLoaderSimple节点中未找到ckpt_name字段。"
                
            # 获取模型列表和描述
            ckpt_info = required_info["ckpt_name"]
            
            # 获取tooltip描述
            tooltip = "无描述"
            if isinstance(ckpt_info, list) and len(ckpt_info) > 1:
                # 数组的第二个元素通常包含tooltip
                tooltip_obj = ckpt_info[1]
                if isinstance(tooltip_obj, dict) and "tooltip" in tooltip_obj:
                    tooltip = tooltip_obj["tooltip"]
            
            # 获取模型列表
            model_list = []
            if isinstance(ckpt_info, list) and len(ckpt_info) > 0 and isinstance(ckpt_info[0], list):
                # 数组的第一个元素通常包含模型列表
                model_list = ckpt_info[0]
            
            # 格式化输出
            # Format output
            result = [
                "## ComfyUI Checkpoint模型列表",
                f"描述: {tooltip}",
                f"共找到 {len(model_list)} 个模型\n"
            ]
            
            for i, model_name in enumerate(model_list, 1):
                # 确保直接使用原始模型名称
                result.append(f"{i}. {model_name}")
            
            return "\n".join(result)
            
        except Exception as e:
            error_msg = f"获取模型清单时出错: {str(e)}"
            default_logger.error(error_msg)
            return error_msg

async def main():
    # 创建模拟的MCP实例
    mcp = MockMCP()
    
    # 注册资源
    register_resource_info_tool(mcp)
    
    # 测试ckpt资源
    resource_uri = "info://ckpt"
    
    if resource_uri in mcp.resources:
        print(f"\n=== 测试 {resource_uri} ===")
        result = await mcp.resources[resource_uri]()
        print(result)
    else:
        print(f"\n未找到资源: {resource_uri}")

if __name__ == "__main__":
    asyncio.run(main()) 