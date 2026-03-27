import sys
import os
from pathlib import Path

# 确保导入路径正确
sys.path.append(os.getcwd())

from shadow_coding.core.shadow import ShadowGenerator, SpineProtocol

def test_memory_dump():
    print("\n" + "🛡️ Shadow_Coding Memory Protection (ProtectedDict) ".center(60, "="))
    
    protocol = SpineProtocol(project_id="lab", file_hash="hash", spine=[])
    gen = ShadowGenerator(protocol)
    
    # 注入敏感符号
    real_name = "user_balance_secret"
    shadow_name = gen.get_or_create_mapping(real_name)
    
    print(f"🔍 Mapping Table Dump (Internal Storage):")
    # 获取原始数据存储对象
    internal_storage = gen._mapping._data
    
    plain_text_leaks = []
    for obs_key, obs_val in internal_storage.items():
        # 这里模拟攻击者直接 Dump 内存中的字典键值对
        # 看看能不能搜到明文
        if real_name in str(obs_key) or shadow_name in str(obs_val):
            plain_text_leaks.append((obs_key, obs_val))
            
    print(f"  Internal Keys (Obfuscated): {list(internal_storage.keys())[:2]}")
    
    if not plain_text_leaks:
        print(f"  ✅ [PASSED] No plain-text leaks in memory dump.")
    else:
        print(f"  ❌ [FAILED] Plain-text found in memory: {plain_text_leaks}")

if __name__ == "__main__":
    test_memory_dump()
