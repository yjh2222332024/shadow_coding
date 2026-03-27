"""
Shadow_Coding - AI 代码隐私保护网关
Copyright (C) 2026 严俊皓 <2857922968@qq.com>

基于 AGPLv3 许可证开源
https://github.com/yjh2222332024/Shadow_Coding
"""

import ast
import re
import hashlib
from typing import List, Dict, Optional, Any
from .models import ShadowContract, ParamSignature, ContractCondition, MethodInfo

class ContractGenerator:
    """
    【L2 契约生成引擎】：提取符号定义与 Docstring 约束。
    实现：跨文件符号识别 -> 语义脱敏 -> 影子桩生成。
    """
    
    DOCSTRING_PATTERNS = {
        "args": r"Args:\s*(.*?)(?=\n\n|\nReturns:|\nRaises:|$)",
        "returns": r"Returns:\s*(.*?)(?=\n\n|\nRaises:|\nSide Effects:|$)",
        "raises": r"Raises:\s*(.*?)(?=\n\n|\nSide Effects:|$)",
        "side_effects": r"(?:Side Effects|Note):\s*(.*?)(?=\n\n|$)",
    }

    def __init__(self, shadow_gen):
        self.shadow_gen = shadow_gen

    def generate_from_source(self, file_path: str, target_symbol: str) -> Optional[ShadowContract]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source)
            file_hash = hashlib.sha256(source.encode()).hexdigest()[:16]

            for node in tree.body:
                if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name == target_symbol:
                    return self._build_contract(node, file_path, file_hash)
            return None
        except Exception as e:
            print(f"⚠️ Contract Error [{file_path}]: {e}")
            return None

    def _build_contract(self, node: ast.AST, file_path: str, file_hash: str) -> ShadowContract:
        node_type = "class" if isinstance(node, ast.ClassDef) else "function"
        shadow_name = self.shadow_gen.get_or_create_mapping(node.name)
        
        contract = ShadowContract(
            source_file=file_path,
            source_hash=file_hash,
            shadow_name=shadow_name,
            original_name=node.name,
            node_type=node_type
        )
        
        if node_type == "class":
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    contract.methods.append(self._extract_method_info(item))
        else:
            # 独立函数
            contract.methods.append(self._extract_method_info(node))
            
        return contract

    def _extract_method_info(self, node: ast.FunctionDef) -> MethodInfo:
        shadow_m_name = self.shadow_gen.get_or_create_mapping(node.name)
        
        params = []
        for arg in node.args.args:
            if arg.arg == 'self': continue
            
            # 🏛️ V3.2: 基础类型推断
            inferred_type = None
            if arg.annotation:
                inferred_type = ast.unparse(arg.annotation)
            else:
                # 尝试从默认值推断
                # (这里简化处理，只看是否存在默认值)
                inferred_type = "Any"

            params.append(ParamSignature(
                name=arg.arg,
                type=inferred_type
            ))
            
        doc = ast.get_docstring(node) or ""
        conditions = self._parse_docstring(doc)
        
        # 🏛️ V3.2: 返回值推断
        ret_type = "Any"
        if node.returns:
            ret_type = ast.unparse(node.returns)
        elif "Returns:" in doc:
            # 尝试从 Docstring 简单正则匹配类型
            match = re.search(r"Returns:\s*([a-zA-Z\[\], ]+)", doc)
            if match:
                ret_type = match.group(1).strip()

        return MethodInfo(
            real_name=node.name,
            shadow_name=shadow_m_name,
            params=params,
            returns=ret_type,
            conditions=conditions,
            doc_summary=doc.split('\n')[0] if doc else ""
        )

    def _parse_docstring(self, doc: str) -> List[ContractCondition]:
        conditions = []
        # Fallback: 如果不符合 Google 风格，至少提取一段摘要
        if not any(re.search(p, doc) for p in self.DOCSTRING_PATTERNS.values()):
            if doc.strip():
                conditions.append(ContractCondition(type="side_effect", description=doc.strip()[:100]))
            return conditions

        for ctype, pattern in self.DOCSTRING_PATTERNS.items():
            match = re.search(pattern, doc, re.DOTALL)
            if match:
                mapped_type = "pre" if ctype == "args" else "post" if ctype == "returns" else ctype
                conditions.append(ContractCondition(
                    type=mapped_type,
                    description=match.group(1).strip()
                ))
        return conditions

    def generate_shadow_stub(self, contract: ShadowContract) -> str:
        """
        【方案 5 加固】：生成安全、只读、经转义的影子桩。
        """
        lines = [
            "# 🛡️ Shadow_Coding SECURE SHADOW STUB (READ-ONLY)",
            "# 此文件仅供 AI 理解接口协议，严禁直接修改或注入执行逻辑。",
            ""
        ]
        
        # 转义类/函数名
        safe_shadow_name = self._escape_identifier(contract.shadow_name)
        
        if contract.node_type == "class":
            lines.append(f"class {safe_shadow_name}:")
            if not contract.methods:
                lines.append("    pass")
            else:
                for m in contract.methods:
                    safe_m_name = self._escape_identifier(m.shadow_name)
                    params_list = []
                    for p in m.params:
                        safe_p_name = self._escape_identifier(p.name)
                        safe_p_type = self._escape_identifier(p.type or 'Any')
                        params_list.append(f"{safe_p_name}: {safe_p_type}")
                    
                    params_str = ", ".join(params_list)
                    safe_ret = self._escape_identifier(m.returns or 'Any')
                    
                    lines.append(f"    def {safe_m_name}(self, {params_str}) -> {safe_ret}:")
                    if m.doc_summary:
                        safe_doc = self._escape_docstring(m.doc_summary)
                        lines.append(f"        \"\"\"{safe_doc}\"\"\"")
                    lines.append("        raise NotImplementedError(\"Stub file - not executable\")")
        else:
            if contract.methods:
                m = contract.methods[0]
                params_list = []
                for p in m.params:
                    params_list.append(f"{self._escape_identifier(p.name)}: {self._escape_identifier(p.type or 'Any')}")
                
                params_str = ", ".join(params_list)
                safe_ret = self._escape_identifier(m.returns or 'Any')
                
                lines.append(f"def {safe_shadow_name}({params_str}) -> {safe_ret}:")
                if m.doc_summary:
                    safe_doc = self._escape_docstring(m.doc_summary)
                    lines.append(f"    \"\"\"{safe_doc}\"\"\"")
                lines.append("    raise NotImplementedError(\"Stub file - not executable\")")
        
        return "\n".join(lines)

    def _escape_identifier(self, name: str) -> str:
        """严格标识符转义：只允许字母、数字和下划线"""
        if not name: return "unknown"
        # 移除所有非字母数字下划线字符
        return re.sub(r'[^a-zA-Z0-9_]', '_', name)

    def _escape_docstring(self, doc: str) -> str:
        """严格文档字符串转义：防止注释注入和转义绕过"""
        if not doc: return ""
        # 1. 限制长度
        doc = doc[:200]
        # 2. 移除三引号防止早闭合
        doc = doc.replace('"""', "'''")
        # 3. 转义反斜杠
        doc = doc.replace('\\', '\\\\')
        # 4. 移除换行符保持摘要简洁
        return doc.replace('\n', ' ').strip()
