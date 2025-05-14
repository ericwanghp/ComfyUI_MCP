import os
import json
import httpx
import asyncio
from mcp_server.logger_decorator import log_mcp_call
from mcp_server.logger import default_logger
from mcp_server.utils import load_object_info, load_config

def register_resource_info_tool(mcp):
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