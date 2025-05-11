import json
import configparser
import os
import random

def load_config():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'config.ini'), encoding='utf-8')
    host = config.get('comfyui_server', 'host', fallback='127.0.0.1')
    port = config.get('comfyui_server', 'port', fallback='8188')
    return f"http://{host}:{port}"

def load_uvicorn_config():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'config.ini'), encoding='utf-8')
    uvicorn_host = config.get('mcp_server', 'host', fallback='0.0.0.0')
    uvicorn_port = config.getint('mcp_server', 'port', fallback=9000)
    return uvicorn_host, uvicorn_port

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