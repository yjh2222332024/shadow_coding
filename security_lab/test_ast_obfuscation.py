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
        print(f"  ❌ [FAILED] Attack bypassed security check!")
        return False
    except SecurityViolation as e:
        print(f"  ✅ [PASSED] Intercepted: {e}")
        return True
    except Exception as e:
        print(f"  ❓ [ERROR] Unexpected error: {type(e).__name__}: {e}")
        return False

def test_suite():
    print("\n" + "🛡️ Shadow_Coding AST Obfuscation Test Suite ".center(60, "="))
    
    results = []
    
    # 1. f-string 混淆
    results.append(run_test("f-string dynamic attribute", 
        "import os; getattr(os, f\"{'sys'}{'tem'}\")('whoami')"))
    
    # 2. str.join 混淆
    results.append(run_test("str.join bypass", 
        "import os; getattr(os, ''.join(['s', 'y', 's', 't', 'e', 'm']))('whoami')"))
    
    # 3. str.format 混淆
    results.append(run_test("str.format bypass", 
        "import os; getattr(os, '{}{}'.format('sys', 'tem'))('whoami')"))
    
    # 4. 深度嵌套常量折叠
    results.append(run_test("Deep nested concatenation", 
        "import os; getattr(os, 's' + ('y' + ('s' + ('t' + ('e' + 'm')))))('whoami')"))

    success_count = sum(1 for r in results if r)
    print(f"\n📊 Summary: {success_count}/{len(results)} attacks intercepted.")

if __name__ == "__main__":
    test_suite()
