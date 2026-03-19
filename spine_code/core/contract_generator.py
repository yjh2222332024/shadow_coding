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
            params.append(ParamSignature(
                name=arg.arg,
                type=ast.unparse(arg.annotation) if arg.annotation else None
            ))
            
        doc = ast.get_docstring(node) or ""
        conditions = self._parse_docstring(doc)
        
        return MethodInfo(
            real_name=node.name,
            shadow_name=shadow_m_name,
            params=params,
            returns=ast.unparse(node.returns) if node.returns else "Any",
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
        lines = []
        if contract.node_type == "class":
            lines.append(f"class {contract.shadow_name}:")
            for m in contract.methods:
                params_str = ", ".join([f"{p.name}: {p.type or 'Any'}" for p in m.params])
                lines.append(f"    def {m.shadow_name}(self, {params_str}) -> {m.returns}:")
                if m.doc_summary:
                    lines.append(f"        \"\"\"{m.doc_summary}\"\"\"")
                lines.append("        ...")
        else:
            if contract.methods:
                m = contract.methods[0]
                params_str = ", ".join([f"{p.name}: {p.type or 'Any'}" for p in m.params])
                lines.append(f"def {contract.shadow_name}({params_str}) -> {m.returns}:")
                if m.doc_summary:
                    lines.append(f"    \"\"\"{m.doc_summary}\"\"\"")
                lines.append("    ...")
        return "\n".join(lines)
