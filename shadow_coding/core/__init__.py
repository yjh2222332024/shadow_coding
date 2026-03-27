"""
Shadow_Coding - AI 代码隐私保护网关
Copyright (C) 2026 严俊皓 <2857922968@qq.com>

基于 AGPLv3 许可证开源
https://github.com/yjh2222332024/shadow_coding
"""

# Shadow_Coding Core Modules
from .security import SecurityAuditor
from .exceptions import SecurityError, SecurityViolation
from .shadow import ShadowGenerator, AdaptiveNoiseConfig
from .sharder import LogicSharder
from .analyzer import ASTAnalyzer
from .models import SpineProtocol, SpineNode
from .dynamic_detector import DynamicFeatureDetector
from .contract_generator import ContractGenerator

__all__ = [
    'SecurityAuditor',
    'SecurityViolation',
    'SecurityError',
    'ShadowGenerator',
    'AdaptiveNoiseConfig',
    'LogicSharder',
    'ASTAnalyzer',
    'SpineProtocol',
    'SpineNode',
    'DynamicFeatureDetector',
    'ContractGenerator',
]
