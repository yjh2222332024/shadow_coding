"""
Shadow_Coding - AI 代码隐私保护网关
Copyright (C) 2026 严俊皓 <2857922968@qq.com>

基于 AGPLv3 许可证开源
https://github.com/yjh2222332024/Shadow_Coding
"""

class Shadow_CodingError(Exception):
    """Shadow_Coding 核心异常基类"""
    def __init__(self, message: str, code: int = 1000):
        super().__init__(f"[ERROR-{code}] {message}")
        self.message = message
        self.code = code

class SecurityError(Shadow_CodingError):
    """安全检查/违反异常"""
    def __init__(self, message: str, line: int = 0):
        super().__init__(message, code=2000)
        self.line = line

# 别名：为了向后兼容
SecurityViolation = SecurityError

class TunnelError(Shadow_CodingError):
    """同步隧道异常"""
    def __init__(self, message: str):
        super().__init__(message, code=3000)

class ShadowError(Shadow_CodingError):
    """混淆引擎异常"""
    def __init__(self, message: str):
        super().__init__(message, code=4000)

class ConfigError(Shadow_CodingError):
    """配置管理异常"""
    def __init__(self, message: str):
        super().__init__(message, code=5000)

class StructureError(Shadow_CodingError):
    """AST/代码结构分析异常"""
    def __init__(self, message: str):
        super().__init__(message, code=6000)
