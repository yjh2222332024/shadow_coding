import ast
from typing import List, Tuple

class SecurityViolation(Exception):
    """安全违规异常"""
    def __init__(self, message, line):
        super().__init__(f"🚫 [Security Violation] Line {line}: {message}")
        self.line = line

class SecurityAuditor:
    """
    【安全审计防火墙】：在还原前拦截 AI 注入的危险指令。
    """
    
    # 危险的模块.函数调用
    DANGEROUS_CALLS = {
        'os': ['system', 'remove', 'rmdir', 'mkdir', 'rename', 'replace', 'chmod'],
        'shutil': ['rmtree', 'move', 'copy', 'copy2', 'make_archive'],
        'subprocess': ['run', 'call', 'Popen', 'check_call'],
        'pathlib': ['unlink', 'mkdir', 'rmdir', 'rename', 'replace', 'write_text', 'write_bytes']
    }

    # 危险的内置函数
    DANGEROUS_BUILTINS = {'eval', 'exec', 'compile', 'globals', 'locals'}

    def audit(self, code: str):
        """执行全量 AST 审计"""
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            # 语法错误由其他层处理，这里跳过
            return

        for node in ast.walk(tree):
            # 1. 拦截内置危险函数
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in self.DANGEROUS_BUILTINS:
                    raise SecurityViolation(f"使用高危内置函数: {node.func.id}", node.lineno)

                # 拦截 open(..., 'w') 写入模式
                if node.func.id == 'open':
                    self._check_open_mode(node)

            # 2. 拦截危险库调用 (如 os.system)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                module_name = self._get_base_name(node.func.value)
                if module_name in self.DANGEROUS_CALLS:
                    if node.func.attr in self.DANGEROUS_CALLS[module_name]:
                        raise SecurityViolation(f"检测到危险的物理层操作: {module_name}.{node.func.attr}", node.lineno)
                
                # 特殊处理 Path('...').write_text()
                if node.func.attr in ['write_text', 'write_bytes', 'unlink']:
                     raise SecurityViolation(f"检测到 pathlib 物理写入/删除操作: {node.func.attr}", node.lineno)

    def _get_base_name(self, node: ast.AST) -> str:
        """递归获取调用链底部的名称"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self._get_base_name(node.value)
        elif isinstance(node, ast.Call):
            return self._get_base_name(node.func)
        return ""

    def _check_open_mode(self, node: ast.Call):
        """检查 open 函数是否包含写入模式"""
        # 查找第二个参数 (mode)
        mode = None
        if len(node.args) >= 2:
            if isinstance(node.args[1], ast.Constant):
                mode = node.args[1].value
        
        # 查找关键字参数 mode='w'
        for kw in node.keywords:
            if kw.arg == 'mode' and isinstance(kw.value, ast.Constant):
                mode = kw.value.value
        
        if mode and any(m in mode for m in ['w', 'a', 'x', '+']):
            raise SecurityViolation(f"检测到尝试写入文件: open(..., mode='{mode}')", node.lineno)
