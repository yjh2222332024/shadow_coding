"""
批量更新版权信息脚本
运行此脚本更新所有 shadow_coding/core 目录下的 Python 文件版权头
"""
import os
import re

NEW_COPYRIGHT = '''"""
Shadow_Coding - AI 代码隐私保护网关
Copyright (C) 2026 严俊皓 <2857922968@qq.com>

基于 AGPLv3 许可证开源
https://github.com/yjh2222332024/shadow_coding
"""'''

def update_file(file_path):
    """更新单个文件的版权头"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配旧的版权头（多行文档字符串）
    old_pattern = r'""".*?"""'

    # 替换为新的版权头
    new_content = re.sub(old_pattern, NEW_COPYRIGHT, content, count=1, flags=re.DOTALL)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ 已更新：{file_path}")

if __name__ == "__main__":
    # 需要更新的文件列表
    files_to_update = [
        "shadow_coding/core/contract_generator.py",
        "shadow_coding/core/dynamic_detector.py",
        "shadow_coding/core/exceptions.py",
        "shadow_coding/core/fs_tunnel.py",
        "shadow_coding/core/models.py",
        "shadow_coding/core/shadow.py",
        "shadow_coding/core/sharder.py",
        "shadow_coding/core/translator.py",
    ]
    
    print("🔄 开始批量更新版权信息...")
    print("=" * 50)
    
    for file_path in files_to_update:
        if os.path.exists(file_path):
            update_file(file_path)
        else:
            print(f"⚠️  文件不存在：{file_path}")
    
    print("=" * 50)
    print("✅ 版权信息更新完成！")
