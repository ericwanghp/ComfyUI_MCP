import json
import os
import sys

# 将父目录添加到路径以便导入mcp_server模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def main():
    # 获取文件路径
    object_info_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'object_info')
    file_path = os.path.join(object_info_dir, '127.0.0.1_8188_object_info.json')
    
    try:
        # 打开并加载JSON文件
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 输出基本信息
        print(f"文件载入成功: {file_path}")
        print(f"节点总数: {len(data)}")
        
        # 检查是否存在CheckpointLoaderSimple节点
        if 'CheckpointLoaderSimple' in data:
            print("\n--- CheckpointLoaderSimple节点信息 ---")
            node = data['CheckpointLoaderSimple']
            print(f"节点键: {list(node.keys())}")
            
            # 检查input字段
            if 'input' in node:
                print(f"输入参数: {list(node['input'].keys())}")
                
                # 检查required字段
                if 'required' in node['input']:
                    required = node['input']['required']
                    print(f"Required参数: {list(required.keys())}")
                    
                    # 检查ckpt_name字段
                    if 'ckpt_name' in required:
                        ckpt_input = required['ckpt_name']
                        print(f"ckpt_name类型: {type(ckpt_input)}")
                        
                        if isinstance(ckpt_input, list):
                            print(f"ckpt_name数组长度: {len(ckpt_input)}")
                            
                            if len(ckpt_input) > 0 and isinstance(ckpt_input[0], list):
                                options = ckpt_input[0]
                                print(f"选项数量: {len(options)}")
                                print(f"前5个选项: {options[:5] if len(options) > 5 else options}")
                            
                            if len(ckpt_input) > 1 and isinstance(ckpt_input[1], dict):
                                tooltip = ckpt_input[1]
                                print(f"Tooltip: {tooltip.get('tooltip', '无')}")
                        else:
                            print(f"ckpt_name不是数组")
                    else:
                        print("未找到ckpt_name字段")
                else:
                    print("未找到required字段")
            else:
                print("未找到input字段")
        else:
            print("未找到CheckpointLoaderSimple节点")
            
            # 输出所有节点的名称
            print("\n可用的节点:")
            for i, node_name in enumerate(sorted(data.keys())[:20], 1):
                print(f"{i}. {node_name}")
            
            if len(data) > 20:
                print(f"... 以及{len(data) - 20}个其他节点")
    
    except FileNotFoundError:
        print(f"错误: 文件不存在 - {file_path}")
    except json.JSONDecodeError:
        print(f"错误: 无法解析JSON文件 - {file_path}")
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    main() 