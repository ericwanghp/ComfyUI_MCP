import os
import sys
import configparser
import subprocess
import platform


CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'mcp_server', 'config.ini')
REQUIREMENTS_PATH = os.path.join(os.path.dirname(__file__), 'requirements.txt')
PYPROJECT_PATH = os.path.join(os.path.dirname(__file__), 'pyproject.toml')


def print_menu():
    print("\n==== MCP 安装与配置工具 ====")
    print("1. 配置 config.ini")
    print("2. 检查并安装依赖环境")
    print("3. 检查 Python 版本")
    print("4. 退出")

def input_with_default(prompt, default):
    val = input(f"{prompt} [{default}]: ").strip()
    return val if val else default

def config_config_ini():
    if not os.path.exists(CONFIG_PATH):
        print(f"未找到 config.ini，路径: {CONFIG_PATH}")
        return
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH, encoding='utf-8')
    while True:
        print("\n--- config.ini 配置子菜单 ---")
        sections = config.sections()
        for idx, section in enumerate(sections, 1):
            print(f"{idx}. [{section}]")
        print(f"{len(sections)+1}. 保存并返回主菜单")
        try:
            sec_choice = int(input("选择要配置的区段(输入序号): ").strip())
        except ValueError:
            print("无效输入，请输入数字。")
            continue
        if sec_choice == len(sections)+1:
            confirm = input("\n确认保存修改？(y/n): ").strip().lower()
            if confirm == 'y':
                with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                    config.write(f)
                print("已保存 config.ini。返回主菜单。")
            else:
                print("未保存修改。返回主菜单。")
            break
        if not (1 <= sec_choice <= len(sections)):
            print("无效选择，请重新输入。"); continue
        section = sections[sec_choice-1]
        while True:
            print(f"\n[{section}] 配置项:")
            keys = list(config[section].keys())
            for idx, key in enumerate(keys, 1):
                print(f"{idx}. {key} = {config[section][key]}")
            print(f"{len(keys)+1}. 返回上一级")
            try:
                key_choice = int(input("选择要编辑的key(输入序号): ").strip())
            except ValueError:
                print("无效输入，请输入数字。"); continue
            if key_choice == len(keys)+1:
                break
            if not (1 <= key_choice <= len(keys)):
                print("无效选择，请重新输入。"); continue
            key = keys[key_choice-1]
            old = config[section][key]
            new = input_with_default(f"修改 {key}", old)
            config[section][key] = new
            print(f"已修改: {key} = {new}")

def check_python_version():
    print("\n--- 检查 Python 版本 ---")
    print(f"当前 Python 版本: {platform.python_version()}")
    if sys.version_info < (3, 8):
        print("警告：建议使用 Python 3.8 及以上版本！")
    else:
        print("Python 版本满足要求。")

def install_dependencies():
    print("\n--- 检查并安装依赖 ---")
    # 检查 config.ini 配置的 ComfyUI 是否可访问（用utils.py能力）
    try:
        from mcp_server.utils import load_comfyui_server_info
        host, port = load_comfyui_server_info()
        url = f"http://{host}:{port}/"
        print(f"检测 ComfyUI 服务可访问性: {url}")
        try:
            import httpx
            with httpx.Client(timeout=3.0) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    print("ComfyUI 服务可访问！")
                else:
                    print(f"ComfyUI 服务响应异常，状态码: {resp.status_code}")
        except Exception as e:
            print(f"无法访问 ComfyUI 服务: {e}\n请检查 config.ini 配置和 ComfyUI 是否已启动！")
    except Exception as e:
        print(f"读取 config.ini 或检测 ComfyUI 服务时出错: {e}")
    # 优先用 uv/pdm，否则用 pip
    if os.path.exists(PYPROJECT_PATH):
        # 检查 uv
        try:
            subprocess.run([sys.executable, '-m', 'uv', '--version'], check=True, stdout=subprocess.DEVNULL)
            print("检测到 uv，使用 uv 安装依赖...")
            subprocess.run([sys.executable, '-m', 'uv', 'pip', 'install', '-r', 'pyproject.toml'], check=True)
            return
        except Exception:
            pass
        # 检查 pdm
        try:
            subprocess.run([sys.executable, '-m', 'pdm', '--version'], check=True, stdout=subprocess.DEVNULL)
            print("检测到 pdm，使用 pdm 安装依赖...")
            subprocess.run([sys.executable, '-m', 'pdm', 'install'], check=True)
            return
        except Exception:
            pass
    # fallback: pip
    if os.path.exists(REQUIREMENTS_PATH):
        print("使用 pip 安装 requirements.txt 依赖...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', REQUIREMENTS_PATH], check=True)
    else:
        print("未找到 requirements.txt 或 pyproject.toml，无法自动安装依赖。")


def main():
    while True:
        print_menu()
        choice = input("请选择操作: ").strip()
        if choice == '1':
            config_config_ini()
        elif choice == '2':
            install_dependencies()
        elif choice == '3':
            check_python_version()
        elif choice == '4':
            print("退出安装工具。")
            break
        else:
            print("无效选择，请重新输入。")

if __name__ == '__main__':
    main() 