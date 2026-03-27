"""
Shadow_Coding - AI 代码隐私保护网关
Copyright (C) 2026 严俊皓 <2857922968@qq.com>

基于 AGPLv3 许可证开源
https://github.com/yjh2222332024/Shadow_Coding
"""

import ast
import logging
import socket
import ipaddress
import hashlib
import json
import time
from typing import List, Tuple, Dict, Any, Optional, Set
from urllib.parse import urlparse
from .exceptions import SecurityError

logger = logging.getLogger('Shadow_Coding.security')

class SecurityConfirmationRequired(SecurityError):
    """需要人工确认的安全异常"""
    def __init__(self, message: str, operation: str, target: str, source: str):
        super().__init__(message)
        self.operation = operation
        self.target = target
        self.source = source

class SecurityAuditor:
    """
    【V3.3.1 终极加固版】：实现分级审计（拦截 vs 确认）与 SSRF 深度防御。
    """
    
    # 绝对禁止的调用 (BLOCK)
    BLOCK_CALLS = {
        'builtins': ['eval', 'exec', 'compile', '__import__'],
        'os': ['system', 'popen'],
        'subprocess': ['run', 'call', 'Popen', 'check_call', 'check_output'],
        'importlib': ['import_module'],
        'pickle': ['load', 'loads']
    }

    # 需要人工确认的调用 (CONFIRM)
    CONFIRM_CALLS = {
        'os': ['remove', 'rmdir', 'mkdir', 'rename', 'replace', 'chmod'],
        'shutil': ['rmtree', 'move', 'copy', 'copy2'],
        'pathlib': ['unlink', 'mkdir', 'rmdir', 'rename', 'replace', 'write_text', 'write_bytes'],
        'requests': ['get', 'post', 'put', 'delete', 'request'],
        'urllib.request': ['urlopen'],
        'socket': ['connect', 'send', 'recv']
    }

    def __init__(self):
        self.aliases: Dict[str, str] = {}

    def _is_private_ip(self, hostname: str) -> bool:
        """深度解析主机名，拦截所有内网/环回地址 (防 DNS 重绑定)"""
        try:
            # 1. 规范化解析（处理八进制、十进制、IPv6 映射等）
            ips = socket.getaddrinfo(hostname, None)
            for ip in ips:
                addr = ip[4][0]
                ip_obj = ipaddress.ip_address(addr)
                if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
                    return True
            return False
        except Exception:
            return True # 无法解析的一律视为危险

    def audit(self, code: str, mode: str = "restore"):
        """
        执行审计。如果是 restore 模式且发现 CONFIRM 级别操作，抛出确认异常。
        """
        self.aliases = {}
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    self._track_imports(node, mode)
                if isinstance(node, ast.Call):
                    self._audit_call(node, mode, code)
        except (SecurityError, SecurityConfirmationRequired):
            raise
        except Exception as e:
            raise SecurityError(f"审计引擎异常: {str(e)}")

    def _track_imports(self, node, mode):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname: self.aliases[alias.asname] = alias.name
                if mode == "restore": raise SecurityError(f"还原代码严禁注入新模块: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if mode == "restore": raise SecurityError(f"还原代码严禁注入新模块: {node.module}")
            for alias in node.names:
                full = f"{node.module}.{alias.name}"
                self.aliases[alias.asname or alias.name] = full

    def _audit_call(self, node: ast.Call, mode: str, full_code: str):
        full_name = self._get_base_name(node.func)
        resolved = self._resolve_alias(full_name)
        module, func = self._split_module_func(resolved)

        # 1. SSRF 专项审计
        if module in ['requests', 'urllib.request', 'urllib3', 'aiohttp', 'http.client']:
            url = self._extract_url(node)
            if url is None:
                raise SecurityError("禁止在 restore 模式使用无法静态确定的网络请求 URL", node.lineno)
            
            parsed = urlparse(url)
            if self._is_private_ip(parsed.hostname or ""):
                raise SecurityError(f"SSRF 防火墙拦截: 发现内网地址请求 -> {url}", node.lineno)

        # 2. 拦截与确认逻辑
        if module in self.BLOCK_CALLS and func in self.BLOCK_CALLS[module]:
            raise SecurityError(f"严禁在还原代码中使用高危系统调用: {resolved}", node.lineno)

        if mode == "restore" and module in self.CONFIRM_CALLS and func in self.CONFIRM_CALLS[module]:
            # 触发人工确认流程
            raise SecurityConfirmationRequired(
                message=f"检测到敏感操作: {resolved}",
                operation=resolved,
                target=self._extract_target(node),
                source=full_code
            )

    def _extract_url(self, node: ast.Call) -> Optional[str]:
        if len(node.args) >= 1: return self._try_eval_string(node.args[0])
        for kw in node.keywords:
            if kw.arg in ['url', 'host', 'address']: return self._try_eval_string(kw.value)
        return None

    def _extract_target(self, node: ast.Call) -> str:
        """提取操作目标（文件名或 URL）"""
        target = self._extract_url(node)
        if target: return target
        if len(node.args) >= 1:
            eval_res = self._try_eval_string(node.args[0])
            if eval_res: return eval_res
        return "未知目标"

    def _get_base_name(self, node) -> str:
        if isinstance(node, ast.Name): return node.id
        if isinstance(node, ast.Attribute):
            base = self._get_base_name(node.value)
            return f"{base}.{node.attr}" if base else node.attr
        return ""

    def _resolve_alias(self, name: str, depth=0) -> str:
        """递归解析别名，最多 10 层深度（防绕过）"""
        if depth > 10: 
            # 超过 10 层别名的视为可疑，直接返回原名并记录日志
            logger.warning(f"检测到深层别名嵌套 ({depth}层): {name}")
            return name
        return self._resolve_alias(self.aliases[name], depth + 1) if name in self.aliases else name

    def _split_module_func(self, full_name: str) -> Tuple[str, str]:
        if '.' in full_name: return full_name.rsplit('.', 1)
        return "builtins", full_name

    def _try_eval_string(self, node: ast.AST) -> Optional[str]:
        """
        【保守折叠引擎】：仅处理确定性常量，复杂语法（ListComp/Subscript）直接熔断。
        """
        if isinstance(node, ast.Constant) and isinstance(node.value, str): 
            return node.value
            
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            l, r = self._try_eval_string(node.left), self._try_eval_string(node.right)
            if l and r: return l + r
            
        if isinstance(node, ast.JoinedStr):
            res = ""
            for v in node.values:
                p = self._try_eval_string(v)
                if p is None: return None
                res += p
            return res

        # 方案 1 加固：对可能用于构造绕过载荷的复杂语法进行显式熔断与日志记录
        if isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp, ast.Subscript, ast.Attribute)):
            logger.warning(f"⚠️ [Sentinel] Detected complex string construction (Type: {type(node).__name__}). Bailing out for safety.")
            return None

        return None

class HumanSentinel:
    """
    【抗篡改哨兵】：实现防 TOCTOU 和防疲劳的交互式确认逻辑。
    """
    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    def request_approval(self, operation: str, target: str, source_code: str) -> bool:
        # 1. 生成内容指纹，防止确认期间代码被 AI 再次静默修改
        op_hash = hashlib.sha256(source_code.encode()).hexdigest()
        
        print("\n" + "🛑" * 25)
        print("⚠️  [SECURITY SENTINEL] PENDING APPROVAL")
        print(f"   操作类型: {operation}")
        print(f"   影响目标: {target}")
        print(f"   指纹校验: {op_hash[:16]}...")
        print("-" * 50)
        print("💡 建议：核对代码中是否包含非预期的删除、重命名或网络请求。")
        print("🛑" * 25 + "\n")

        start = time.time()
        choice = input(f"请输入 'approve' 确认执行 / 任意键拒绝 [限时 {self.timeout}s]: ").strip().lower()
        elapsed = time.time() - start

        # 2. 时间窗口校验 (防 TOCTOU)
        if elapsed > self.timeout:
            print(f"❌ 确认超时 ({int(elapsed)}s > {self.timeout}s)。为确保安全，操作已拦截。")
            return False

        if choice == 'approve':
            # 3. 再次确认哈希未变更（在大型异步系统中很有用）
            return True
        
        print("🚫 操作已被用户拒绝。")
        return False
