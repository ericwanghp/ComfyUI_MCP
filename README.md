<<<<<<< HEAD
# MCP Server（ComfyUI ModelContextProtocol 服务端 | ModelContextProtocol Server for ComfyUI）

## 项目简介 | Project Introduction

MCP Server 是为 ComfyUI 设计的松耦合、可扩展、配置驱动的模型上下文协议（ModelContextProtocol）服务端。支持依据客户定制工作流可扩展 API（如 txt2img、img2img），每个 API 的参数和行为均可通过 JSON 配置和工具模块灵活扩展，适合 AI 绘图、推理等场景的自动化与集成。

MCP Server is a loosely coupled, extensible, and configuration-driven ModelContextProtocol (MCP) server designed for ComfyUI. It supports extensible APIs (such as txt2img, img2img) based on customer-customized workflows. Each API's parameters and behaviors can be flexibly extended via JSON configuration and tool modules, making it suitable for automation and integration in AI drawing, inference, and similar scenarios.

---

## 目录结构 | Directory Structure

```
mcp_server/
├── mcp_server/
│   ├── mcpserver.py         # 主入口，自动注册 tools 目录下所有工具 | Main entry, auto-registers all tools in the tools directory
│   ├── tools/               # 工具模块与 API 配置（每个API一个py和json）| Tool modules and API configs (one .py and .json per API)
│   │   ├── txt2img.py
│   │   ├── txt2img_api.json
│   │   ├── img2img.py
│   │   ├── img2img_api.json
│   │   └── __init__.py
│   ├── utils.py             # 配置、模板、随机种子等通用工具 | Utilities for config, templates, random seed, etc.
│   ├── config.ini           # 服务与ComfyUI地址配置 | Service and ComfyUI address config
│   └── __init__.py
├── pyproject.toml           # 构建配置与依赖 | Build config and dependencies
└── README.md                # 使用说明（本文件）| User guide (this file)
```

---

## 依赖安装 | Dependency Installation

推荐使用 [uv](https://github.com/astral-sh/uv) 或 [pdm](https://pdm.fming.dev/) 管理依赖：

It is recommended to use [uv](https://github.com/astral-sh/uv) or [pdm](https://pdm.fming.dev/) for dependency management:

```bash
# 安装uv（推荐）| Install uv (recommended)
pip install uv
uv pip install -r pyproject.toml

# 或使用pdm | Or use pdm
pip install pdm
pdm install
```

如需手动安装依赖，可参考 pyproject.toml：
- Python >= 3.12
- httpx >= 0.28.1
- mcp[cli] >= 1.8.0

If you need to install dependencies manually, refer to pyproject.toml:
- Python >= 3.12
- httpx >= 0.28.1
- mcp[cli] >= 1.8.0

---

## 配置说明 | Configuration

编辑 `mcp_server/mcp_server/config.ini`：

Edit `mcp_server/mcp_server/config.ini`:

```ini
[comfyui_server]
host = 127.0.0.1
port = 8188

[mcp_server]
host = 0.0.0.0
port = 8000
```

- `comfyui_server`：ComfyUI 被调用ComfyUI的服务地址与端口 | The service address and port of the target ComfyUI instance to be called
- `mcp_server`：MCP 服务自身监听地址与端口 | MCP server's own listening address and port

---

## 启动服务 | Start the Service

推荐使用 uv 启动（无需切换目录，自动识别包结构）：

It is recommended to use uv to start (no need to change directory, package structure is auto-detected):

```bash
uv run -m mcp_server.mcpserver
```

- 默认以 SSE（Server-Sent Events）模式运行 | Runs in SSE (Server-Sent Events) mode by default
- 自动注册 `tools/` 目录下所有工具模块 | Automatically registers all tool modules in the `tools/` directory

---

## 工具自动注册与API扩展机制 | Tool Auto-Registration & API Extension

### 1. 工具自动注册 | Tool Auto-Registration

- `mcpserver.py` 会自动遍历 `tools/` 目录下所有 `.py` 文件（如 `txt2img.py`），并调用其中的 `register_xxx_tool(mcp)` 注册函数。
- 每个工具模块需实现 `register_xxx_tool(mcp)`，并通过 `@mcp.tool()` 装饰器注册 API。

- `mcpserver.py` will automatically traverse all `.py` files in the `tools/` directory (such as `txt2img.py`) and call their `register_xxx_tool(mcp)` registration function.
- Each tool module must implement `register_xxx_tool(mcp)` and register the API via the `@mcp.tool()` decorator.

**示例 | Example：**

```python
# tools/txt2img.py
from mcp_server.utils import load_config, load_prompt_template, randomize_all_seeds

def register_txt2img_tool(mcp):
    @mcp.tool()
    async def txt2img(prompt: str, pic_width: str = '512', ... ) -> str:
        ...
```

### 2. 配置驱动参数 | Config-Driven Parameters

- 每个 API 的参数签名、类型、注释均可通过同名 JSON（如 `txt2img_api.json`）配置自动生成。
- 所有参数均为可选，未传时自动取模板默认值，支持递归 seed 随机化、模型白名单、batch_size 限制等业务规则。
- 新增API的JSON模板需在被调用的ComfyUI自定义工作流导出同名API，加后缀_api，并放置于tools目录。

- Each API's parameter signature, type, and docstring can be auto-generated via a same-named JSON (e.g., `txt2img_api.json`).
- All parameters are optional; if not provided, default values from the template are used. Supports recursive seed randomization, model whitelist, batch_size limit, and other business rules.
- For new APIs, the JSON template should be exported from the custom workflow of the target ComfyUI instance, with the same API name and the suffix `_api`, and placed in the `tools` directory.

**示例片段 | Example snippet：**

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

### 3. 异步高效 | Asynchronous & Efficient

- 所有 HTTP 调用均为 `async`/`await`，基于 `httpx.AsyncClient`，支持高并发。

- All HTTP calls use `async`/`await` and are based on `httpx.AsyncClient`, supporting high concurrency.

### 4. 新增自定义工具 | Add Custom Tools

以 `txt2img` 为例，扩展新工具只需：
- 新增 `tools/myapi.py`，实现 `register_myapi_tool(mcp)` 并注册 API
- 新增 `tools/myapi_api.json`，定义参数模板(在被调用的ComfyUI的自定义工作流导出同名API，加后缀_api) 
- 无需修改主入口，自动生效

To add a new tool (e.g., `txt2img`):
- Add `tools/myapi.py`, implement `register_myapi_tool(mcp)` and register the API
- Add `tools/myapi_api.json` to define the parameter template (export the same-named API with `_api` suffix from the custom workflow of the target ComfyUI instance)
- No need to modify the main entry, it will take effect automatically

---

## 典型用法与返回格式 | Typical Usage & Return Format

### 文生图（txt2img）| Text-to-Image (txt2img)

```python
result = await mcp.tools.txt2img(
    prompt="一只可爱的猫",
    pic_width="512",
    pic_height="512",
    negative_prompt="bad hand",
    batch_size="1",
    model="sd_xl_base_1.0.safetensors"
)
# 返回图片 Markdown 格式 | Returns image in Markdown format
```

- 所有参数均可省略，自动取默认模板 | All parameters are optional, defaults are used if omitted
- 返回图片 Markdown 链接，可直接用于文档或前端展示 | Returns image Markdown links, can be used directly in docs or frontend

---

## 使用 MCP Inspector 进行调试 | Debug with MCP Inspector

MCP Inspector 是官方推荐的交互式开发者工具，可用于测试和调试 MCP 服务端。

MCP Inspector is the official recommended interactive developer tool for testing and debugging MCP servers.

- 官方文档 | Official Docs：[https://modelcontextprotocol.io/docs/tools/inspector](https://modelcontextprotocol.io/docs/tools/inspector)

### 快速启动 Inspector | Quick Start Inspector

无需安装，直接使用 npx：

No installation required, use npx directly:

```bash
npx @modelcontextprotocol/inspector uv run -m mcp_server.mcpserver
```

- Inspector 会自动连接本地 MCP 服务，支持工具、资源、提示词等全方位交互测试。
- 可在 Inspector 的 Tools 面板中查看所有自动注册的 API 工具，测试参数、查看返回、调试异常。

- Inspector will automatically connect to the local MCP server, supporting full interactive testing of tools, resources, prompts, etc.
- You can view all auto-registered API tools in the Inspector's Tools panel, test parameters, view results, and debug exceptions.

更多用法详见 [官方 Inspector 指南 | See more in the official Inspector guide](https://modelcontextprotocol.io/docs/tools/inspector)。

---

## 常见问题 | FAQ

- **ComfyUI 未启动或地址错误**：请检查 `config.ini` 配置
- **依赖未安装**：请先执行 `uv pip install -r pyproject.toml` 或 `pdm install`
- **新增工具未生效**：确认已实现 `register_xxx_tool(mcp)` 并放置于 `tools/` 目录
- **参数校验失败**：请检查 JSON 模板与实际参数类型、范围。(在被调用的ComfyUI的自定义工作流导出同名API，加后缀_api，并放置于 `tools/` 目录) 
- **Inspector 无法连接**：确认 MCP 服务已启动且端口未被占用

- **ComfyUI not started or wrong address**: Please check `config.ini`
- **Dependencies not installed**: Please run `uv pip install -r pyproject.toml` or `pdm install` first
- **New tool not effective**: Make sure `register_xxx_tool(mcp)` is implemented and placed in the `tools/` directory
- **Parameter validation failed**: Please check the JSON template and actual parameter types/ranges. (Export the same-named API with `_api` suffix from the custom workflow of the target ComfyUI instance and place it in the `tools/` directory)
- **Inspector cannot connect**: Make sure the MCP server is running and the port is not occupied

---

## 贡献与扩展 | Contribution & Extension

欢迎提交 PR 或 issue，完善更多 API 工具与业务逻辑。
如需集成更多模型、参数或业务规则，仅需新增/修改工具模块与 JSON 配置，无需侵入主流程。

Contributions are welcome via PR or issue to improve more API tools and business logic.
To integrate more models, parameters, or business rules, just add/modify tool modules and JSON configs, no need to change the main process.

---

## License

MIT

---

如需详细开发文档、API 参考或二次开发指导，请参考项目内 Memory Bank 设计文档与规则说明。

For detailed development docs, API reference, or secondary development guidance, please refer to the Memory Bank design docs and rule descriptions in the project.

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

- 单元测试与CI完善：补充更多单元测试用例，集成持续集成（CI）流程，保障代码质量。
  
  Improved unit testing & CI: Add more unit tests and integrate CI pipelines to ensure code quality.

=======
# ComfyUI_MCP
 MCP Server is a loosely coupled, extensible, and configuration-driven ModelContextProtocol (MCP) server designed for ComfyUI. 
>>>>>>> 7fff40a54a5a0c647cbdbcbd1d1b762932dec7ce
