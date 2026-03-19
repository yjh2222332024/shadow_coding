import re
from typing import Dict

class ErrorLogTranslator:
    """
    【双语调试器】：工业级日志还原。
    优化了对非 ASCII 字符边界的处理，支持复杂报错日志的精准翻译。
    """
    def __init__(self, reverse_mapping: Dict[str, str]):
        self.reverse_mapping = reverse_mapping
        
    def translate_log(self, log_content: str) -> str:
        translated_log = log_content
        # 降序排列防止子串干扰
        sorted_shadow_names = sorted(self.reverse_mapping.keys(), key=len, reverse=True)
        
        for shadow_name in sorted_shadow_names:
            real_name = self.reverse_mapping[shadow_name]
            # 🏛️ 采用更健壮的非捕获组边界匹配，解决 \b 在某些环境下的失效问题
            pattern = r'(?<![a-zA-Z0-9_])' + re.escape(shadow_name) + r'(?![a-zA-Z0-9_])'
            replacement = f"[{real_name}]"
            translated_log = re.sub(pattern, replacement, translated_log)
            
        return translated_log
