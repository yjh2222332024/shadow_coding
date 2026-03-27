import sys
import os
import shutil
from pathlib import Path

# 确保导入路径正确
sys.path.append(os.getcwd())

from shadow_coding.core.fs_tunnel import FileSystemTunnelV2
from shadow_coding.core.shadow import ShadowGenerator, SpineProtocol

def test_path_boundary():
    print("\n" + "🛡️ Shadow_Coding Path Boundary & Sanitization ".center(60, "="))
    
    # 模拟环境
    real_dir = Path("./lab_real").resolve()
    shadow_dir = Path("./lab_shadow").resolve()
    real_dir.mkdir(exist_ok=True)
    shadow_dir.mkdir(exist_ok=True)
    
    tunnel = FileSystemTunnelV2(str(real_dir), str(shadow_dir))
    
    # 1. 测试目录穿越拦截
    traversal_path = Path("/etc/passwd")
    is_safe = tunnel._is_safe_path(traversal_path, real_dir)
    print(f"🔍 Testing Traversal (/etc/passwd):")
    print(f"  {'✅ [PASSED] Traversal blocked' if not is_safe else '❌ [FAILED] Traversal accepted'}")

    # 2. 测试日志脱敏 (Windows 路径兼容性)
    print(f"🔍 Testing Log Sanitization (Windows Case-Insensitive):")
    test_msg = f"Failed to open file at C:\\Users\\Administrator\\secret.py"
    sanitized = tunnel.logger._sanitize(test_msg)
    print(f"  Original: {test_msg}")
    print(f"  Sanitized: {sanitized}")
    
    is_clean = "Administrator" not in sanitized and "Users" not in sanitized
    print(f"  {'✅ [PASSED] Sensitive path removed' if is_clean else '❌ [FAILED] Path leak detected'}")

    # 3. 测试原子写入
    print(f"🔍 Testing Atomic Write:")
    target_file = shadow_dir / "atomic_test.py"
    try:
        tunnel._atomic_write(target_file, "print('hello')")
        if target_file.exists():
             print(f"  ✅ [PASSED] Atomic write successful.")
        else:
             print(f"  ❌ [FAILED] Atomic write failed.")
    except Exception as e:
        print(f"  ❌ [ERROR] Atomic write error: {e}")

    # 清理
    shutil.rmtree(real_dir)
    shutil.rmtree(shadow_dir)

if __name__ == "__main__":
    test_path_boundary()
