import sys
import os
from pathlib import Path

# 确保导入路径正确
sys.path.append(os.getcwd())

from shadow_coding.core.security import SecurityAuditor
from shadow_coding.core.exceptions import SecurityViolation

def run_test(name, code, mode="restore"):
    auditor = SecurityAuditor()
    print(f"🔍 Testing: {name}")
    try:
        auditor.audit(code, mode=mode)
        print(f"  ❌ [FAILED] Dynamic injection bypassed security check!")
        return False
    except SecurityViolation as e:
        print(f"  ✅ [PASSED] Intercepted injection: {e}")
        return True
    except Exception as e:
        print(f"  ❓ [ERROR] Unexpected error: {type(e).__name__}: {e}")
        return False

def test_suite():
    print("\n" + "🛡️ Shadow_Coding Dynamic Injection Test Suite ".center(60, "="))
    
    results = []
    
    # 1. importlib 动态导入
    results.append(run_test("importlib.import_module", 
        "import importlib; mod = importlib.import_module('os'); mod.system('whoami')"))
    
    # 2. base64.b64decode 解码 (直接拦截 b64decode)
    results.append(run_test("base64.b64decode string building", 
        "import base64; getattr(os, base64.b64decode(b'c3lzdGVt').decode())('whoami')"))
    
    # 3. bytes.decode() 常量折叠解析
    # 如果审计器发现 getattr(os, b'system'.decode())，应该识别出 system
    results.append(run_test("bytes.decode constant resolution", 
        "import os; getattr(os, b'system'.decode())('whoami')"))
    
    # 4. exec 动态代码执行
    results.append(run_test("exec built-in block", 
        "exec('import os; os.system(\"whoami\")')"))

    success_count = sum(1 for r in results if r)
    print(f"\n📊 Summary: {success_count}/{len(results)} injections blocked.")

if __name__ == "__main__":
    test_suite()
