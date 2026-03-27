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
        print(f"  ❌ [FAILED] Alias bypassed security check!")
        return False
    except SecurityViolation as e:
        print(f"  ✅ [PASSED] Intercepted alias: {e}")
        return True
    except Exception as e:
        print(f"  ❓ [ERROR] Unexpected error: {type(e).__name__}: {e}")
        return False

def test_suite():
    print("\n" + "🛡️ Shadow_Coding Alias Tracking Test Suite ".center(60, "="))
    
    results = []
    
    # 1. 简单别名
    results.append(run_test("Simple import as alias", 
        "import os as o; o.system('whoami')"))
    
    # 2. 从模块导入函数别名
    results.append(run_test("From import as function alias", 
        "from os import system as s; s('whoami')"))
    
    # 3. 多层别名链
    # 目前 _resolve_alias 可支持 5 层递归
    results.append(run_test("Multi-level alias chain", 
        "import os as _o\n_oo = _o\n_ooo = _oo\n_ooo.system('whoami')", mode="sync")) # sync 模式绕过 import 限制来测试调用链
    
    # 4. 装饰器注入
    results.append(run_test("Dangerous decorator injection", 
        "import os\n@os.system\ndef backdoor(): pass", mode="sync"))

    success_count = sum(1 for r in results if r)
    print(f"\n📊 Summary: {success_count}/{len(results)} aliases tracked.")

if __name__ == "__main__":
    test_suite()
