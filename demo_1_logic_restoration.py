import ast
from spine_code.core.shadow import ShadowGenerator
from spine_code.core.models import SpineProtocol

def run_demo():
    print("🚀 [Demo 1] Logic Restoration - Isomorphic Check")
    
    # 1. 原始 Bug 代码
    real_code = """
def calculate_member_discount(price: float, level: int):
    # BUG: 应该乘 0.7，误写成了 1.7
    if level > 10:
        return price * 1.7 
    return price * 0.9
"""
    # 2. 影子化
    protocol = SpineProtocol(project_id="Demo1", file_hash="X", spine=[])
    shadow_gen = ShadowGenerator(protocol)
    shadow_gen.get_or_create_mapping("calculate_member_discount")
    shadow_gen.get_or_create_mapping("price")
    shadow_gen.get_or_create_mapping("level")
    
    shadow_snippet = shadow_gen.generate_shadow_snippet(real_code)
    print("\n🎭 AI Perspective (Shadowed):")
    print(shadow_snippet)

    # 3. 模拟 AI 修复逻辑 (1.7 -> 0.7)
    ai_fixed_shadow = shadow_snippet.replace("1.7", "0.7")
    print("\n🧠 AI Fixed the logic error in Shadow Space.")

    # 4. 还原
    restored_code = shadow_gen.restore_snippet(ai_fixed_shadow)
    print("\n✨ Restored Code (Back to Real Semantics):")
    print(restored_code)

    # 5. 验证
    local_env = {}
    exec(restored_code, {}, local_env)
    result = local_env['calculate_member_discount'](100.0, 15)
    print(f"\n📊 Result: {result} (Expected: 70.0)")
    if result == 70.0:
        print("\n✅ [SUCCESS] Logic healed without knowing the variable names!")

if __name__ == "__main__":
    run_demo()
