import os
import json
import sys
import traceback

# 将父目录添加到路径以便导入mcp_server模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def main():
    # 获取对象信息JSON文件路径
    object_info_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'object_info')
    if not os.path.exists(object_info_dir):
        print(f"目录不存在: {object_info_dir}")
        return
    
    # 查找对象信息JSON文件
    json_files = [f for f in os.listdir(object_info_dir) if f.endswith('_object_info.json')]
    if not json_files:
        print(f"未找到对象信息JSON文件在 {object_info_dir} 目录中")
        return
    
    json_file = os.path.join(object_info_dir, json_files[0])
    print(f"使用对象信息文件: {json_file}")
    
    try:
        # 加载JSON文件
        with open(json_file, 'r', encoding='utf-8') as f:
            object_info = json.load(f)
        
        # 检查CheckpointLoaderSimple节点
        if "CheckpointLoaderSimple" not in object_info:
            print("未找到CheckpointLoaderSimple节点")
            return
        
        node_info = object_info["CheckpointLoaderSimple"]
        print(f"\n=== CheckpointLoaderSimple节点结构 ===")
        print(f"节点键: {list(node_info.keys())}")
        
        # 检查input字段
        if "input" not in node_info:
            print("未找到input字段")
            return
        
        input_info = node_info["input"]
        print(f"Input键: {list(input_info.keys())}")
        
        # 检查required字段
        if "required" not in input_info:
            print("未找到required字段")
        else:
            required_info = input_info["required"]
            print(f"Required键: {list(required_info.keys())}")
            
            # 检查ckpt_name字段
            if "ckpt_name" not in required_info:
                print("未找到ckpt_name字段")
            else:
                ckpt_info = required_info["ckpt_name"]
                print(f"\n=== ckpt_name字段结构 ===")
                if isinstance(ckpt_info, list):
                    print(f"类型: 列表, 长度: {len(ckpt_info)}")
                    
                    # 显示模型列表
                    if len(ckpt_info) > 0:
                        model_list = ckpt_info[0]
                        if isinstance(model_list, list):
                            print(f"模型列表长度: {len(model_list)}")
                            print(f"前5个模型: {model_list[:5]}")
                        else:
                            print(f"第一个元素不是列表: {type(model_list)}")
                    
                    # 显示tooltip信息
                    if len(ckpt_info) > 1:
                        tooltip_obj = ckpt_info[1]
                        if isinstance(tooltip_obj, dict):
                            print(f"第二个元素键: {list(tooltip_obj.keys())}")
                            if "tooltip" in tooltip_obj:
                                print(f"Tooltip: {tooltip_obj['tooltip']}")
                        else:
                            print(f"第二个元素不是字典: {type(tooltip_obj)}")
                else:
                    print(f"类型: {type(ckpt_info)}")
                    print(f"内容: {ckpt_info}")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 