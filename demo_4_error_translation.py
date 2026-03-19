from spine_code.core.translator import ErrorLogTranslator

def run_demo():
    print("🚀 [Demo 4] Error Translator - Bilingual Debugging")
    
    # 1. 模拟一个映射表 (真实语义 -> 影子符号)
    # 在真实运行中，这个 mapping 来自 ShadowGenerator.mapping
    mapping = {
        "calculate_tax": "S_f1_99",
        "user_balance": "S_v2_04",
        "amount": "S_v3_11"
    }
    
    # 2. 模拟一个真实环境产生的报错日志（明文）
    real_error_log = """
Traceback (most recent call last):
  File "main.py", line 10, in <module>
    calculate_tax(user_balance, amount)
TypeError: unsupported operand type for *: 'NoneType' and 'float' in user_balance
"""
    print("\n🔴 Real Context Error (Private Semantics):")
    print(real_error_log)

    # 3. 执行日志翻译
    # 🏛️ 修正：传入 {真实名: 影子名} 映射表
    translator = ErrorLogTranslator(mapping)
    translated_log = translator.translate_log(real_error_log)
    
    print("\n🎭 Shadow Context Error (What the AI sees):")
    print("-" * 60)
    print(translated_log)
    print("-" * 60)
    
    # 验证是否成功替换
    if "S_f1_99" in translated_log and "calculate_tax" not in translated_log:
        print("\n✅ [SUCCESS] Traceback translated to Shadow Semantics!")
    else:
        print("\n❌ [FAILED] Translation failed. Real names leaked!")

if __name__ == "__main__":
    run_demo()
