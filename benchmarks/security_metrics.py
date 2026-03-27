import time
import ast
import os
import sys
import asyncio
from pathlib import Path
from typing import List, Dict

# 确保导入路径正确
sys.path.append(os.getcwd())

try:
    from shadow_coding.core.sharder import LogicSharder
    from shadow_coding.core.shadow import ShadowGenerator, AdaptiveNoiseConfig
    from shadow_coding.core.models import SpineProtocol
    from shadow_coding.core.contract_generator import ContractGenerator
except ImportError:
    pass

class SecurityBenchmarker:
    def __init__(self, shadow_gen):
        self.shadow_gen = shadow_gen

    def calculate_metrics(self, original_code: str, shadowed_code: str):
        print("\n" + "📊 " + "V3.2 Security Metrics Report".center(50, "═"))
        
        orig_names = self._extract_names(original_code)
        shadow_names = self._extract_names(shadowed_code)
        
        obfuscated_count = sum(1 for n in orig_names if n in self.shadow_gen.mapping)
        total_symbols = len(orig_names)
        sdr = (obfuscated_count / total_symbols) if total_symbols > 0 else 0
        
        print(f"🔹 语义脱敏率 (SDR): {sdr:.2%}  ({'✅ HIGH' if sdr > 0.8 else '⚠️ MEDIUM'})")
        
        orig_nodes = len(list(ast.walk(ast.parse(original_code))))
        shadow_nodes = len(list(ast.walk(ast.parse(shadowed_code))))
        complexity_gain = (shadow_nodes / orig_nodes) if orig_nodes > 0 else 1
        
        print(f"🔹 逻辑熵增 (Complexity Gain): {complexity_gain:.2f}x")
        
        # 验证是否包含类型锚点
        has_types = ":" in shadowed_code and ("->" in shadowed_code or "Any" in shadowed_code)
        print(f"🔹 类型锚点注入 (Type Anchors): {'✅ ACTIVE' if has_types else '❌ MISSING'}")
        
        # 验证零结构泄露 (检查关键词)
        leaks = [kw for kw in ['complexity', 'loop', 'O(N)', 'nested'] if kw in shadowed_code.lower()]
        print(f"🔹 零结构泄露验证: {'✅ SECURE' if not leaks else f'❌ LEAK DETECTED: {leaks}'}")
        
        reconstruct_cost = (sdr * 0.7) + (complexity_gain * 0.3)
        print(f"🔹 综合复原成本指数 (RCI): {reconstruct_cost:.2f} / 1.0")
        print("═"*54 + "\n")

    def _extract_names(self, code: str) -> set:
        try:
            tree = ast.parse(code)
            return {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        except:
            return set()

def run_enterprise_benchmark():
    print("🚀 Shadow_Coding V3.2 Enterprise-Grade Benchmarking Session...")
    
    # 🏛️ 企业级压测用例：涵盖 async, try-finally, 类型注解
    original_code = """
async def process_user_transaction(user_id: int, amount: float, tags: list) -> dict:
    \"\"\"
    处理用户交易的核心逻辑 (V3.2 压测)。
    Returns:
        result: 处理结果字典 (Dict)
    \"\"\"
    try:
        if amount <= 0:
            raise ValueError("Invalid amount")
            
        # 核心计算
        tax = amount * 0.05
        net_amount = amount - tax
        
        # 嵌套逻辑
        status = "pending"
        if "vip" in tags:
            net_amount *= 1.05
            status = "priority"
            
        result = {
            "id": user_id,
            "net": net_amount,
            "status": status,
            "meta": [t.upper() for t in tags]
        }
        return result
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        # 资源清理模拟
        pass
"""
    
    # 1. 初始化引擎
    AdaptiveNoiseConfig.enable_production_mode()
    protocol = SpineProtocol(project_id="enterprise_bench", file_hash="v3.2", spine=[])
    shadow_gen = ShadowGenerator(protocol)
    sharder = LogicSharder(shadow_gen)
    contract_engine = ContractGenerator(shadow_gen)
    
    # 2. 执行影子化与碎片化
    tree = ast.parse(original_code)
    func_node = tree.body[0]
    
    # 提取契约 (用于验证类型注入)
    contract = contract_engine._build_contract(func_node, "test.py", "hash")
    stub = contract_engine.generate_shadow_stub(contract)
    
    # 执行碎片化 (shard_count=3)
    shards = sharder.shard_function(func_node, shard_count=3)
    
    # 3. 生成最终混淆代码
    import astunparse
    sharded_source = ""
    for s in shards:
        sharded_source += astunparse.unparse(s)
    
    shadowed_code = shadow_gen.generate_shadow_snippet(sharded_source)
    
    # 4. 运行安全评估
    bench = SecurityBenchmarker(shadow_gen)
    bench.calculate_metrics(original_code, shadowed_code)
    
    # 5. 展示影子代码片段 (脱敏版)
    print("📝 Shadow Code Preview (Top 10 lines):")
    print("-" * 40)
    lines = shadowed_code.split('\n')
    for line in lines[:15]:
        if line.strip(): print(f"  {line}")
    print("-" * 40)
    
    print("\n📝 Shadow Stub Preview (Type Anchors):")
    print("-" * 40)
    print(stub)
    print("-" * 40)

if __name__ == "__main__":
    run_enterprise_benchmark()
