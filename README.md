# ComfyUI_MCP Server（ComfyUI的ModelContextProtocol 服务端 | ModelContextProtocol Server for ComfyUI）

## 项目简介 | Project Introduction

ComfyUI_MCP Server 是为 ComfyUI 设计的松耦合、可扩展、配置驱动的模型上下文协议（ModelContextProtocol）服务端。支持依据客户定制工作流可扩展MCP服务(tool) 如: txt2img、img2img，每个MCP服务(tool)的参数和行为均可通过 JSON初始化和MCP工具装饰器模块灵活扩展，适合 AI 绘图、推理等场景的自动化与集成。

ComfyUI_MCP Server is a loosely coupled, extensible, and configuration-driven Model Context Protocol (MCP) server designed for ComfyUI. It supports the extension of MCP services (tools) such as txt2img and img2img, based on user-customized workflows. The parameters and behaviors of each MCP service (tool) can be flexibly extended through JSON initialization and MCP tool decorator modules, making it ideal for automation and integration in AI image generation, inference, and similar scenarios.

## 视频演示 | Video Demo

<details open>
<summary>🎬 ComfyUI_MCP Server 功能演示 Demo（YouTube）</summary>

<p align="center">
  <a href="https://youtu.be/vXZOBZ_FsA8" target="_blank">
    <img src="https://img.youtube.com/vi/vXZOBZ_FsA8/0.jpg" alt="ComfyUI_MCP Server Demo" width="480">
  </a>
</p>
</details>


---

## 目录结构 | Directory Structure

```
mcp_server/
├── mcp_server/
│   ├── mcpserver.py         # 主入口，自动注册 tools 目录下所有工具 | Main entry, auto-registers all tools in the tools directory
│   ├── tools/               # 工具模块与mcp tool配置（每个mcp tool一个py和json）| Tool modules and configs (one .py and .json per mcp tool)
│   │   ├── txt2img.py
│   │   ├── txt2img_api.json
│   │   ├── img2img.py
│   │   ├── img2img_api.json
│   │   ├── {xxxx}.py        # 配合被调用的ComfyUI的工作流。可任意添加MCP工具配置，工具自动注册与API扩展机制。  
│   │   ├── {xxxx}_api.json  # Used in conjunction with the workflows of the callable ComfyUI, allowing for the addition of MCP tool configurations, with automatic registration and API extension mechanisms.
│   │   ├── ......
│   │   └── __init__.py
│   ├── utils.py             # 配置、模板、随机种子等通用工具 | Utilities for config, templates, random seed, etc.
│   ├── config.ini           # mcp服务与被调用的ComfyUI地址配置 | Service and ComfyUI address config
│   ├── logger.py & decorator.py                # 日志系统 | logs sys
│   └── __init__.py
├── workflows/               # MCP工具可实现的ComfyUI工作流json，与tools/对应。 | The "ComfyUI workflow json" that the "MCP tool" can achieve. Corresponding to "tools/".
│   ├── txt2img.json
│   ├── img2img.json
│   ├── {xxxx}.json          
│   ├── ......
├── pyproject.toml           # 构建配置与依赖 | Build config and dependencies
└── README.md                # 使用说明（本文件）| User guide (this file)
```

---

## 安装 & 配置 & 运行 | Installation & Configuration & Run

```bash
python install.py # install(check item 2~3) & config(check item 1) 

run_mcp.bat #run on windows
./run_mcp.sh #run on linux

```

- 默认以流式HTTP（streamable-http）模式运行 | Runs in streamable-http mode by default
- 自动注册 `tools/` 目录下所有工具模块 | Automatically registers all tool modules in the `tools/` directory

---

## ComfyUI_MCP工具自动注册与API扩展机制 | Tool Auto-Registration & API Extension

### 1. 新增自定义MCP工具和方法实现 | Add Custom MCP Tools and Method Implementations

以 `txt2img` 为例，扩展新工具只需：
- 新增 `tools/myapi.py`，实现 `register_myapi_tool(mcp)` 并注册 MCP服务(tool)
- 新增 `tools/myapi_api.json`，定义参数模板(在被调用的ComfyUI的自定义工作流导出同名API，加后缀_api) 
- 无需修改主入口，自动生效

To add a new tool (e.g., `txt2img`):
- Add `tools/myapi.py`, implement `register_myapi_tool(mcp)` and register the MCP service(tool)
- Add `tools/myapi_api.json` to define the parameter template (export the same-named API with `_api` suffix from the custom workflow of the target ComfyUI instance)
- No need to modify the main entry, it will take effect automatically

#### 典型方法实现与返回格式 | Typical Usage & Return Format

文生图（txt2img）| Text-to-Image (txt2img)

```python
# tools/txt2img.py 
def register_txt2img_tool(mcp):
    async def comfyui_txt2img_impl(prompt: str, pic_width: str, pic_height: str, negative_prompt: str, batch_size: str, model: str) -> str:
      ...
# 返回图片 Markdown 格式 | Returns image in Markdown format
      ...
        markdown_images = [f"![image]({url})" for url in image_urls]
        return "\n".join(markdown_images)
```

- 调用ComfyUI在线工作流HTTP API，获得结果。 | Call the ComfyUI online workflow HTTP API to obtain results.
- 所有参数均可省略，默认值取自对应Json `tools/txt2img_api.json` | All parameters are optional; default values are taken from the corresponding JSON file `tools/txt2img_api.json`.
- 返回图片 Markdown 链接，可直接用于文档或前端展示 | Returns image Markdown links, can be used directly in docs or frontend
- 再把以上功能实现，封装成对应的MCP服务(tool) | Then encapsulate the above functionalities into the corresponding MCP service (tool).

---

### 2. MCP工具自动注册 | MCP Tool Auto-Registration

- `mcpserver.py` 会自动遍历 `tools/` 目录下所有 `.py` 文件（如 `txt2img.py`），并调用其中的 `register_xxx_tool(mcp)` 注册函数。
- 每个工具模块需实现 `register_xxx_tool(mcp)`，并通过 `@mcp.tool()` 装饰器注册 MCP服务(tool)。

- `mcpserver.py` will automatically traverse all `.py` files in the `tools/` directory (such as `txt2img.py`) and call their `register_xxx_tool(mcp)` registration function.
- Each tool module must implement `register_xxx_tool(mcp)` and register the MCP service(tool) via the `@mcp.tool()` decorator.

**示例 | Example：**

```python
# tools/txt2img.py
def register_txt2img_tool(mcp):
    @mcp.tool()
    async def txt2img(prompt: str, pic_width: str = '512', ... ) -> str:
        ...
```

### 3. 配置驱动参数 | Config-Driven Parameters

- 每个 MCP服务(tool) 的参数签名、类型、注释均可通过同名 JSON（如 `tools/txt2img_api.json`）配置生成。在被调用的ComfyUI的自定义工作流导出同名API，加后缀_api。
- 所有参数均为可选，未传时自动取模板默认值，支持递归 seed 随机化、模型白名单、batch_size 限制等业务规则。
- 新增MCP服务(tool)的JSON模板需在被调用的ComfyUI自定义工作流导出同名API，加后缀_api，并放置于tools目录。

- Each API's parameter signature, type, and docstring can be auto-generated via a same-named JSON (e.g., `tools/txt2img_api.json`).
- MCP service(tool) parameters are optional; if not provided, default values from the template are used. Supports recursive seed randomization, model whitelist, batch_size limit, and other business rules.
- For new MCP service(tool), the JSON template should be exported from the custom workflow of the target ComfyUI instance, with the same API name and the suffix `_api`, and placed in the `tools` directory.

**示例片段 `tools/txt2img_api.json`| Example snippet：**

```json
{
  "5": {
    "inputs": {
      "width": 512,
      "height": 512,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage"
  }
}
```

### 4. 资源注册与管理 | Resource Registration & Management

支持通过 `@mcp.resource("info//ckpt")` 装饰器注册资源型API，实现如模型等资源的自动发现与管理。

Supports resource-type API registration via the `@mcp.resource("info//ckpt")` decorator, enabling automatic discovery and management of resources such as models.

**示例 | Example：**

```python
@mcp.resource("info//ckpt")
async def list_checkpoints() -> list:
    # 返回所有可用的ckpt模型列表
    ...
```

---

## 使用 MCP Inspector 进行调试 | Debug with MCP Inspector

MCP Inspector 是官方推荐的交互式开发者工具，可用于测试和调试 MCP 服务端。

MCP Inspector is the officially recommended interactive developer tool for testing and debugging MCP servers.

- 官方文档 | Official Docs：[https://modelcontextprotocol.io/docs/tools/inspector](https://modelcontextprotocol.io/docs/tools/inspector)

### 快速启动 Inspector | Quick Start Inspector

```bash
run_mcp.bat --inspector #run on windows
./run_mcp.sh --inspector #run on linux
```

- Inspector 可以连接本地 MCP 服务，支持工具、资源、提示词等全方位交互测试。
- 可在 Inspector 的 Tools 面板中查看所有自动注册的 API 工具，测试参数、查看返回、调试异常。

- Inspector can connect to the local MCP server, supporting full interactive testing of tools, resources, prompts, etc.
- You can view all auto-registered API tools in the Inspector's Tools panel, test parameters, view results, and debug exceptions.

更多用法详见 [官方 Inspector 指南 | See more in the official Inspector guide](https://modelcontextprotocol.io/docs/tools/inspector)。

---

## 常见问题 | FAQ

- **ComfyUI 未启动或地址错误**：请检查 `config.ini` 配置
- **依赖未安装**：请先执行 `uv pip install -r pyproject.toml` 
- **新增工具未生效**：确认已实现 `register_xxx_tool(mcp)` 并放置于 `tools/` 目录
- **参数校验失败**：请检查 JSON 模板与实际参数类型、范围。(在被调用的ComfyUI的自定义工作流导出同名API，加后缀_api，并放置于 `tools/` 目录) 
- **Inspector 无法连接**：确认 MCP 服务已启动且端口未被占用
- **日志未生成或无输出**：请检查`config.ini`中的`logging`配置项，确保`log_path`路径存在且有写入权限。
- **MCP服务传输模式切换无效**：请确认已正确修改`config.ini`中的`transport`参数，并重启服务。

- **ComfyUI not started or wrong address**: Please check `config.ini`
- **Dependencies not installed**: Please run `uv pip install -r pyproject.toml` 
- **New tool not effective**: Make sure `register_xxx_tool(mcp)` is implemented and placed in the `tools/` directory
- **Parameter validation failed**: Please check the JSON template and actual parameter types/ranges. (Export the same-named API with `_api` suffix from the custom workflow of the target ComfyUI instance and place it in the `tools/` directory)
- **Inspector cannot connect**: Make sure the MCP server is running and the port is not occupied
- **Logs not generated or no output**: Please check the `logging` configuration in `config.ini` to ensure the `log_path` exists and has write permissions.
- **MCP service transport mode switch ineffective**: Please confirm that the `transport` parameter in `config.ini` has been correctly modified and restart the service.

---

## 贡献与扩展 | Contribution & Extension

欢迎提交 PR 或 issue，完善更多 API 工具与业务逻辑。
如需集成更多模型、参数或业务规则，仅需新增/修改工具模块与 JSON 配置，无需侵入主流程。

Contributions are welcome via PR or issue to improve more API tools and business logic.
To integrate more models, parameters, or business rules, just add/modify tool modules and JSON configs, no need to change the main process.

---

## 待优化 | To Do

- 参数类型自动推断与校验增强：支持更智能的参数类型推断和更严格的校验，提升健壮性。
  
  Enhanced parameter type inference and validation: Smarter type inference and stricter validation for better robustness.

- 更丰富的错误处理与日志：增加详细的错误日志、异常追踪和用户友好提示。
  
  Richer error handling and logging: More detailed error logs, exception tracing, and user-friendly messages.

- 热加载工具/配置：支持tools目录和配置文件的热加载，无需重启服务即可生效。
  
  Hot-reload for tools/config: Support hot-reloading of tools directory and config files without restarting the service.

- 多ComfyUI后端支持：支持同时连接和调度多个ComfyUI后端实例，实现负载均衡或多模型推理。
  
  Multi-ComfyUI backend support: Connect and schedule multiple ComfyUI backend instances for load balancing or multi-model inference.

- 多媒体数据交互支持：支持图片、声音、视频等多媒体数据的输入输出与处理。
  
  Multimedia data interaction support: Support input, output, and processing of multimedia data such as images, audio, and video.

- 更全面的ComfyUI HTTP API的集成。

  More comprehensive integration of the ComfyUI HTTP API.

- 单元测试与CI完善：补充更多单元测试用例，集成持续集成（CI）流程，保障代码质量。
  
  Improved unit testing & CI: Add more unit tests and integrate CI pipelines to ensure code quality.

