import uuid
import httpx
import asyncio
import json
from mcp_server.utils import load_config, load_prompt_template, randomize_all_seeds
from mcp_server.logger_decorator import log_mcp_call
from mcp_server.logger import default_logger

def register_img2img_tool(mcp):
    async def comfyui_img2img_impl(prompt: str) -> str:
        """
        实现ComfyUI图生图API调用，返回Markdown图片格式（异步版）
        Implement ComfyUI image-to-image API call, return Markdown image format (async version).
        """
        default_logger.debug(f"开始处理图生图请求: prompt='{prompt[:50]}...'")
        
        comfyui_host = load_config()
        prompt_template = load_prompt_template('img2img')
        # 随机化所有seed | randomize all seeds
        randomize_all_seeds(prompt_template)
        # 设置正向prompt | set positive prompt
        prompt_template["6"]["inputs"]["text"] = prompt
        
        default_logger.debug(f"配置ComfyUI模板参数完成")
        
        client_id = str(uuid.uuid4())
        body = {
            "client_id": client_id,
            "prompt": prompt_template
        }
        
        default_logger.debug(f"开始向ComfyUI发送API请求: {comfyui_host}/api/prompt")
        default_logger.debug(f"请求体内容: {json.dumps(body, ensure_ascii=False, indent=2)}")
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{comfyui_host}/api/prompt", json=body)
            resp.raise_for_status()
            prompt_id = resp.json()["prompt_id"]
            
            default_logger.debug(f"成功提交ComfyUI任务, prompt_id: {prompt_id}")
            
            while True:
                await asyncio.sleep(3)
                history_url = f"{comfyui_host}/api/history/{prompt_id}"
                his_resp = await client.get(history_url)
                his_resp.raise_for_status()
                data = his_resp.json()
                if prompt_id in data:
                    status = data[prompt_id]["status"]
                    if status["completed"] and status["status_str"] == "success":
                        default_logger.debug(f"ComfyUI任务完成: {status['status_str']}")
                        outputs = data[prompt_id]["outputs"]
                        images = None
                        for node_id, node_data in outputs.items():
                            if "images" in node_data:
                                images = node_data["images"]
                                break
                        if images is None:
                            error_msg = "未找到包含images的输出节点 | No output node with images found"
                            default_logger.error(error_msg)
                            raise Exception(error_msg)
                        break
                        
        default_logger.debug(f"生成图片数量: {len(images)}")
        
        image_urls = [
            f"{comfyui_host}/api/view?filename={img['filename']}&subfolder={img['subfolder']}&type=output"
            for img in images
        ]
        markdown_images = [f"![image]({url})" for url in image_urls]
        return "\n".join(markdown_images)

    @mcp.tool()
    @log_mcp_call
    async def img2img(prompt: str) -> str:
        """
        图生图服务：输入prompt，返回图片Markdown格式（异步版）
        Image-to-image service: input prompt, return image in Markdown format (async version).
        Args:
            prompt: str 正向prompt | positive prompt

        Returns:
            str 图片Markdown格式 | image in Markdown format
        Raises: 
            httpx.RequestError: API请求失败 | API request failed
            KeyError: 返回数据格式错误 | response data format error
            Exception: 其他未预期的异常 | other unexpected exception
        """
        try:
            default_logger.info(f"接收到图生图请求: prompt='{prompt[:30]}...'")
            result = await comfyui_img2img_impl(prompt)
            default_logger.info(f"图生图请求完成")
            return result
        except httpx.RequestError as e:
            error_msg = f"API请求失败: {str(e)} | API request failed: {str(e)}"
            default_logger.error(error_msg)
            raise Exception(error_msg)
        except KeyError as e:
            error_msg = f"返回数据格式错误: {str(e)} | response data format error: {str(e)}"
            default_logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"图生图服务异常: {str(e)} | image-to-image service error: {str(e)}"
            default_logger.error(error_msg)
            raise Exception(error_msg) 