import ast
from typing import List, Dict, Union
from dataclasses import dataclass

@dataclass
class DynamicFeature:
    line: int
    feature_type: str
    description: str
    severity: str # "low", "medium", "high"

class DynamicFeatureDetector:
    """
    【L3 动态特征检测器】：识别静态分析无法处理的 Python 动态特性。
    """
    HIGH_RISK_PATTERNS = {
        "eval", "exec", "compile", 
        "__import__", "importlib.import_module",
        "globals", "locals", "vars",
        "getattr", "setattr", "delattr",
        "__getattribute__", "__getattr__", "__setattr__"
    }

    MEDIUM_RISK_PATTERNS = {
        "type", "isinstance", "issubclass", 
        "hasattr", "callable", "dir"
    }

    def detect(self, source: str) -> List[DynamicFeature]:
        try:
            tree = ast.parse(source)
        except Exception:
            return [DynamicFeature(0, "parse_error", "源码语法错误，无法分析", "high")]

        features = []
        for node in ast.walk(tree):
            # 1. 检测函数调用
            if isinstance(node, ast.Call):
                name = self._get_call_name(node)
                if name in self.HIGH_RISK_PATTERNS:
                    features.append(DynamicFeature(
                        line=node.lineno,
                        feature_type="high_risk_call",
                        description=f"高危动态调用: {name}",
                        severity="high"
                    ))
                elif name in self.MEDIUM_RISK_PATTERNS:
                    features.append(DynamicFeature(
                        line=node.lineno,
                        feature_type="medium_risk_call",
                        description=f"反射特性调用: {name}",
                        severity="medium"
                    ))

            # 2. 检测魔术方法定义
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name in ["__getattr__", "__getattribute__", "__setattr__", "__delattr__"]:
                    features.append(DynamicFeature(
                        line=node.lineno,
                        feature_type="magic_method",
                        description=f"魔术方法重载: {node.name}",
                        severity="high"
                    ))
                elif node.name.startswith("__") and node.name.endswith("__"):
                    if node.name not in ["__init__", "__str__", "__repr__", "__call__"]:
                        features.append(DynamicFeature(
                            line=node.lineno,
                            feature_type="magic_method",
                            description=f"动态行为魔术方法: {node.name}",
                            severity="medium"
                        ))

            # 3. 检测动态属性访问
            if isinstance(node, ast.Attribute):
                if node.attr in ["__dict__", "__class__"]:
                    features.append(DynamicFeature(
                        line=node.lineno,
                        feature_type="dynamic_attr",
                        description=f"访问底层动态属性: {node.attr}",
                        severity="medium"
                    ))

        return features

    def _get_call_name(self, node: ast.Call) -> str:
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
        return ""

    def should_reject(self, features: List[DynamicFeature]) -> bool:
        return any(f.severity == "high" for f in features)

    def generate_report(self, features: List[DynamicFeature]) -> str:
        if not features: return ""
        report = ["⚠️ [L3 Sentinel] Dynamic features detected:"]
        for f in sorted(features, key=lambda x: x.line):
            icon = "🔴" if f.severity == "high" else "🟡"
            report.append(f"  {icon} Line {f.line}: {f.description}")
        return "\n".join(report)
