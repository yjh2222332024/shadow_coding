import hashlib
import string
import re
from typing import Dict, Optional, List
from .models import SpineProtocol, SpineNode

class ShadowGenerator:
    """
    【影子协议生成器】：实现确定性语义混淆。
    改用哈希算法保证混淆名称在不同 Session 间具有一致性。
    """
    def __init__(self, protocol: SpineProtocol):
        self.protocol = protocol
        self.mapping = {} # 真名 -> 影子名
        self.reverse_mapping = {} # 影子名 -> 真名
        self.seed = "S_" 

    def get_or_create_mapping(self, real_name: str) -> str:
        """基于哈希生成确定的影子映射名"""
        if real_name not in self.mapping:
            # 🏛️ 确定性混淆：使用哈希值的前 6 位 + 序列号
            hash_suffix = hashlib.md5(real_name.encode()).hexdigest()[:6]
            shadow_name = f"{self.seed}{hash_suffix}_{len(self.mapping)}"
            self.mapping[real_name] = shadow_name
            self.reverse_mapping[shadow_name] = real_name
        return self.mapping[real_name]

    def obfuscate_spine(self):
        """对整个协议中的所有节点进行递归混淆"""
        self._recursive_obfuscate(self.protocol.spine)
        self.protocol.mapping = self.mapping

    def _recursive_obfuscate(self, nodes: List[SpineNode]):
        for node in nodes:
            node.sn = self.get_or_create_mapping(node.t)
            if node.children:
                self._recursive_obfuscate(node.children)

    def generate_shadow_snippet(self, code_snippet: str) -> str:
        """
        利用混淆映射表，将一段代码片段转化为“影子片段”。
        """
        shadow_code = code_snippet
        sorted_names = sorted(self.mapping.keys(), key=len, reverse=True)
        for real_name in sorted_names:
            shadow_name = self.mapping[real_name]
            # \b 对中文可能失效，这里添加兼容处理
            pattern = r'(?<![a-zA-Z0-9_])' + re.escape(real_name) + r'(?![a-zA-Z0-9_])'
            shadow_code = re.sub(pattern, shadow_name, shadow_code)
        return shadow_code

    def restore_snippet(self, shadow_snippet: str) -> str:
        """反向还原"""
        real_code = shadow_snippet
        sorted_shadow_names = sorted(self.reverse_mapping.keys(), key=len, reverse=True)
        for shadow_name in sorted_shadow_names:
            real_name = self.reverse_mapping[shadow_name]
            pattern = r'(?<![a-zA-Z0-9_])' + re.escape(shadow_name) + r'(?![a-zA-Z0-9_])'
            real_code = re.sub(pattern, real_name, real_code)
        return real_code
