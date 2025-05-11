import uuid
import httpx
import asyncio
from mcp_server.utils import load_config, load_prompt_template, randomize_all_seeds

def register_img2img_tool(mcp):
    async def comfyui_img2img_impl(prompt: str) -> str:
        """
        实现ComfyUI图生图API调用，返回Markdown图片格式（异步版）
        Implement ComfyUI image-to-image API call, return Markdown image format (async version).
        """
        comfyui_host = load_config()
        prompt_template = load_prompt_template('img2img')
        # 随机化所有seed | randomize all seeds
        randomize_all_seeds(prompt_template)
        # 设置正向prompt | set positive prompt
        prompt_template["6"]["inputs"]["text"] = prompt
        client_id = str(uuid.uuid4())
        body = {
            "client_id": client_id,
            "prompt": prompt_template
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{comfyui_host}/api/prompt", json=body)
            resp.raise_for_status()
            prompt_id = resp.json()["prompt_id"]
            while True:
                await asyncio.sleep(3)
                history_url = f"{comfyui_host}/api/history/{prompt_id}"
                his_resp = await client.get(history_url)
                his_resp.raise_for_status()
                data = his_resp.json()
                if prompt_id in data:
                    status = data[prompt_id]["status"]
                    if status["completed"] and status["status_str"] == "success":
                        outputs = data[prompt_id]["outputs"]
                        images = None
                        for node_id, node_data in outputs.items():
                            if "images" in node_data:
                                images = node_data["images"]
                                break
                        if images is None:
                            raise Exception("未找到包含images的输出节点 | No output node with images found")
                        break
        image_urls = [
            f"{comfyui_host}/api/view?filename={img['filename']}&subfolder={img['subfolder']}&type=output"
            for img in images
        ]
        markdown_images = [f"![image]({url})" for url in image_urls]
        return "\n".join(markdown_images)

    @mcp.tool()
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
            return await comfyui_img2img_impl(prompt)
        except httpx.RequestError as e:
            raise Exception(f"API请求失败: {str(e)} | API request failed: {str(e)}")
        except KeyError as e:
            raise Exception(f"返回数据格式错误: {str(e)} | response data format error: {str(e)}")
        except Exception as e:
            raise Exception(f"图生图服务异常: {str(e)} | image-to-image service error: {str(e)}") 