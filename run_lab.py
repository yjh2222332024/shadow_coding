import os
import sys
import subprocess

def run_script(script_path):
    print(f"\n🚀 Running: {script_path}")
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()

    try:
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, env=env)
        print(result.stdout)
        if result.stderr:
            print(f"⚠️ Errors:\n{result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Execution failed: {e}")
        return False

def main():
    print("="*60)
    print("  Shadow_Coding V3.3.1 L4 Security Laboratory Report  ")
    print("="*60)

    lab_dir = "security_lab"
    scripts = [
        "test_ast_obfuscation.py",
        "test_alias_tracking.py",
        "test_dynamic_injection.py",
        "test_path_boundary.py",
        "test_memory_dump.py",
        "test_l4_defense.py"  # L4 新增测试
    ]

    all_passed = True
    for s in scripts:
        if not run_script(os.path.join(lab_dir, s)):
            all_passed = False

    print("\n" + "="*60)
    if all_passed:
        print("🏆  Final Result: ALL SECURITY TESTS PASSED  🏆")
        print("   L4 Security Hardening Level: VERIFIED")
    else:
        print("🚨  Final Result: SOME TESTS FAILED - CHECK ABOVE  🚨")
    print("="*60)

if __name__ == "__main__":
    main()
