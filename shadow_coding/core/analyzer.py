"""
Shadow_Coding - AI 代码隐私保护网关
Copyright (C) 2026 严俊皓 <2857922968@qq.com>

基于 AGPLv3 许可证开源
https://github.com/yjh2222332024/Shadow_Coding
"""

import ast
import hashlib
from typing import List, Dict, Any, Optional
from .models import SpineNode, SpineProtocol, NodeType

class ASTAnalyzer:
    """
    【ISR 引擎】：代码骨架重构。
    通过 Python AST 提取结构，并优化了 METHOD 识别逻辑与性能。
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        with open(file_path, "r", encoding="utf-8") as f:
            self.source = f.read()
        self.tree = ast.parse(self.source)
        self.file_hash = hashlib.sha256(self.source.encode()).hexdigest()[:16]
        self.imports = {}

    def analyze(self) -> SpineProtocol:
        # 直接遍历顶层，不再使用 ast.walk 提高效率
        self._collect_imports()
        spine = self._extract_nodes(self.tree.body, level=1, parent_type=NodeType.MODULE)
        return SpineProtocol(
            project_id=self.file_path,
            file_hash=self.file_hash,
            spine=spine
        )

    def _collect_imports(self):
        """扫描并记录跨文件依赖符号"""
        for node in self.tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports[alias.name] = alias.name
            elif isinstance(node, ast.ImportFrom):
                level = node.level
                prefix = "." * level
                module = f"{prefix}{node.module if node.module else ''}"
                for alias in node.names:
                    self.imports[alias.name] = module

    def _extract_nodes(self, body: List[ast.AST], level: int, parent_type: NodeType) -> List[SpineNode]:
        nodes = []
        for item in body:
            node = None
            # 增强防御：处理可能不存在 end_lineno 的情况
            start_line = getattr(item, 'lineno', 0)
            end_line = getattr(item, 'end_lineno', start_line)
            
            if isinstance(item, ast.ClassDef):
                node = SpineNode(
                    title=item.name,
                    level=level,
                    line_range=[start_line, end_line],
                    type=NodeType.CLASS
                )
                node.children = self._extract_nodes(item.body, level + 1, NodeType.CLASS)
            elif isinstance(item, ast.FunctionDef):
                # 精准判断：如果父级是 CLASS，则是 METHOD
                ntype = NodeType.METHOD if parent_type == NodeType.CLASS else NodeType.FUNCTION
                node = SpineNode(
                    title=item.name,
                    level=level,
                    line_range=[start_line, end_line],
                    type=ntype
                )
                node.children = self._extract_nodes(item.body, level + 1, ntype)

            if node:
                nodes.append(node)
        return nodes

if __name__ == "__main__":
    import os
    target_file = "shadow_coding/main.py"
    if os.path.exists(target_file):
        analyzer = ASTAnalyzer(target_file)
        protocol = analyzer.analyze()
        for node in protocol.spine:
            print(f"[{node.type.value}] {node.t} | Lines: {node.lines}")
