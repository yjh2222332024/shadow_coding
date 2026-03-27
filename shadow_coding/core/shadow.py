"""
Shadow_Coding - AI 代码隐私保护网关
Copyright (C) 2026 严俊皓 <2857922968@qq.com>

基于 AGPLv3 许可证开源
https://github.com/yjh2222332024/Shadow_Coding
"""

import hashlib
import string
import re
import random
import base64
import secrets
import logging
from typing import Dict, Optional, List, Any
from .models import SpineProtocol, SpineNode
from .exceptions import ShadowError

logger = logging.getLogger('Shadow_Coding.shadow')

class ProtectedDict:
    """
    【内存受保护字典】：使用动态盐值对内存中的键值进行混淆，防止明文 Dump。
    """
    def __init__(self):
        self._data: Dict[str, str] = {}
        self._salt = secrets.token_hex(32)  # 256 位随机盐，确保不可预测性

    def _obfuscate(self, data: str) -> str:
        # 简单的 XOR + Base64 混淆
        salt_bytes = self._salt.encode()
        data_bytes = data.encode()
        result = bytearray()
        for i in range(len(data_bytes)):
            result.append(data_bytes[i] ^ salt_bytes[i % len(salt_bytes)])
        return base64.b64encode(result).decode()

    def _deobfuscate(self, data: str) -> str:
        try:
            salt_bytes = self._salt.encode()
            data_bytes = base64.b64decode(data.encode())
            result = bytearray()
            for i in range(len(data_bytes)):
                result.append(data_bytes[i] ^ salt_bytes[i % len(salt_bytes)])
            return result.decode()
        except Exception as e:
            logger.error(f"解密内存映射失败: {e}")
            raise ShadowError(f"无法解密受保护内存数据: {e}")

    def __setitem__(self, key: str, value: str):
        self._data[self._obfuscate(key)] = self._obfuscate(value)

    def __getitem__(self, key: str) -> str:
        obs_key = self._obfuscate(key)
        if obs_key in self._data:
            return self._deobfuscate(self._data[obs_key])
        raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        return self._obfuscate(key) in self._data

    def keys(self):
        return [self._deobfuscate(k) for k in self._data.keys()]

    def items(self):
        return [(self._deobfuscate(k), self._deobfuscate(v)) for k, v in self._data.items()]

class AdaptiveNoiseConfig:
    """
    【自适应噪声配置】：基于变量敏感度的分级噪声注入。
    """
    ENABLE_NOISE = False
    DEFAULT_NOISE_RATIO = 0.0
    
    HIGH_SENSITIVE = [
        'balance', 'password', 'secret', 'token', 'key', 'credential',
        'auth', 'permission', 'role', 'admin', 'private', 'encrypt'
    ]
    
    LOW_SENSITIVE = [
        'temp', 'result', 'data', 'item', 'index', 'count',
        'list', 'array', 'buffer', 'cache'
    ]
    
    @classmethod
    def get_noise_ratio(cls, variable_name: str) -> float:
        if not cls.ENABLE_NOISE:
            return 0.0
        name_lower = variable_name.lower()
        if any(kw in name_lower for kw in cls.HIGH_SENSITIVE):
            return 0.5
        if any(kw in name_lower for kw in cls.LOW_SENSITIVE):
            return 0.1
        return cls.DEFAULT_NOISE_RATIO
    
    @classmethod
    def enable_production_mode(cls):
        cls.ENABLE_NOISE = False
        cls.DEFAULT_NOISE_RATIO = 0.0
    
    @classmethod
    def enable_developer_mode(cls, noise_ratio: float = 0.2):
        cls.ENABLE_NOISE = True
        cls.DEFAULT_NOISE_RATIO = noise_ratio

class CategoryObfuscator:
    """
    【确定性语义迷彩引擎 V3.2】：实现多维技术范畴欺骗。
    """
    GENERALIZED_MAP = {
        "Entity": ["Record", "Node", "Item", "Entry", "Unit", "Elem"],
        "Metric": ["Value", "Measure", "Data", "Point", "Scale", "Stat"],
        "State": ["Flag", "Status", "Mode", "Cond", "Phase", "Step"],
        "Collection": ["List", "Group", "Set", "Buffer", "Batch", "Stream"],
        "Access": ["Handle", "Ref", "Link", "Socket", "Pipe", "Route"],
        "Auth": ["Token", "Ticket", "Claim", "Permit", "Scope", "Role"],
        "Resource": ["Asset", "Object", "Blob", "Cache", "Store", "File"],
        "Logic": ["Rule", "Flow", "Task", "Job", "Op", "Proc"],
        "Generic": ["Attr", "Prop", "Var", "Comp", "Meta", "Base"]
    }

    _ALL_CATS = [item for sublist in GENERALIZED_MAP.values() for item in sublist]

    @classmethod
    def _infer_base_category(cls, name: str) -> str:
        n = name.lower()
        if any(x in n for x in ['id', 'name', 'user', 'account', 'client', 'target', 'person', 'profile']):
            return "Entity"
        if any(x in n for x in ['price', 'rate', 'amount', 'count', 'sum', 'balance', 'total', 'val', 'num']):
            return "Metric"
        if any(x in n for x in ['is_', 'has_', 'can_', 'status', 'state', 'mode', 'phase', 'active']):
            return "State"
        if any(x in n for x in ['list', 'array', 'items', 'group', 'batch', 'queue', 'stack', 'set']):
            return "Collection"
        if any(x in n for x in ['url', 'ip', 'host', 'port', 'path', 'api', 'route', 'link', 'socket']):
            return "Access"
        if any(x in n for x in ['auth', 'login', 'token', 'key', 'secret', 'password', 'permit', 'claim']):
            return "Auth"
        if any(x in n for x in ['db', 'file', 'cache', 'store', 'blob', 'asset', 'res']):
            return "Resource"
        if any(x in n for x in ['calc', 'process', 'run', 'task', 'job', 'handle', 'rule', 'flow']):
            return "Logic"
        return "Generic"

    @classmethod
    def generate_shadow_name(cls, real_name: str) -> str:
        try:
            md5_val = hashlib.md5(real_name.encode()).hexdigest()
            short_hash = md5_val[:6]
            seed_val = int(md5_val[:8], 16)
            local_rng = random.Random(seed_val)

            base_cat = cls._infer_base_category(real_name)
            noise_ratio = AdaptiveNoiseConfig.get_noise_ratio(real_name)
            
            if noise_ratio > 0 and local_rng.random() < noise_ratio:
                noise_pool = [c for c in cls._ALL_CATS if c not in cls.GENERALIZED_MAP[base_cat]]
                chosen_prefix = local_rng.choice(noise_pool) if noise_pool else local_rng.choice(cls.GENERALIZED_MAP[base_cat])
            else:
                chosen_prefix = local_rng.choice(cls.GENERALIZED_MAP[base_cat])

            return f"S_{chosen_prefix}_{short_hash}"
        except Exception as e:
            raise ShadowError(f"生成影子名称失败 ({real_name}): {e}")

class ShadowGenerator:
    """
    【影子协议生成器】：实现确定性语义混淆与内存保护。
    """
    def __init__(self, protocol: SpineProtocol):
        self.protocol = protocol
        self._mapping = ProtectedDict()
        self._reverse_mapping = ProtectedDict()

    def get_or_create_mapping(self, real_name: str) -> str:
        if real_name not in self._mapping:
            shadow_name = CategoryObfuscator.generate_shadow_name(real_name)
            self._mapping[real_name] = shadow_name
            self._reverse_mapping[shadow_name] = real_name
        return self._mapping[real_name]

    def obfuscate_spine(self):
        self._recursive_obfuscate(self.protocol.spine)
        # 协议中的 mapping 保持明文供外部参考（仅限非敏感环境）
        self.protocol.mapping = {k: v for k, v in self._mapping.items()}

    def _recursive_obfuscate(self, nodes: List[SpineNode]):
        for node in nodes:
            node.sn = self.get_or_create_mapping(node.t)
            if node.children:
                self._recursive_obfuscate(node.children)

    def generate_shadow_snippet(self, code_snippet: str) -> str:
        try:
            shadow_code = code_snippet
            sorted_names = sorted(self._mapping.keys(), key=len, reverse=True)
            for real_name in sorted_names:
                shadow_name = self._mapping[real_name]
                pattern = r'(?<![a-zA-Z0-9_])' + re.escape(real_name) + r'(?![a-zA-Z0-9_])'
                shadow_code = re.sub(pattern, shadow_name, shadow_code)
            return shadow_code
        except Exception as e:
            raise ShadowError(f"代码影子化过程失败: {e}")

    def restore_snippet(self, shadow_snippet: str) -> str:
        try:
            real_code = shadow_snippet
            sorted_shadow_names = sorted(self._reverse_mapping.keys(), key=len, reverse=True)
            for shadow_name in sorted_shadow_names:
                real_name = self._reverse_mapping[shadow_name]
                pattern = r'(?<![a-zA-Z0-9_])' + re.escape(shadow_name) + r'(?![a-zA-Z0-9_])'
                real_code = re.sub(pattern, real_name, real_code)
            return real_code
        except Exception as e:
            raise ShadowError(f"代码还原过程失败: {e}")
