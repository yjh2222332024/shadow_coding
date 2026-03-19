import json
import os
from core.analyzer import ASTAnalyzer
from core.shadow import ShadowGenerator
from core.contract_generator import ContractGenerator
from core.models import NodeStatus

class SpineCodeCLI:
    """
    【SpineCode V2 总控中心】：支持 L2 跨文件影子契约。
    """
    def __init__(self, target_file: str):
        self.target_file = target_file
        self.analyzer = ASTAnalyzer(target_file)
        self.protocol = self.analyzer.analyze()
        self.shadow = ShadowGenerator(self.protocol)
        
        # 1. 预执行：生成核心映射表
        self.shadow.obfuscate_spine()
        
        # 2. L2 契约生成引擎初始化
        self.contract_engine = ContractGenerator(self.shadow)

    def resolve_contracts(self):
        """核心演示：解析当前文件的所有导入依赖，并生成影子契约"""
        print("\n🔍 [L2 Engine] Resolving Cross-File Dependencies...")
        for symbol, module in self.analyzer.imports.items():
            # 简化逻辑：尝试在核心目录下寻找对应的 py 文件
            potential_file = f"spine_code/core/{symbol.lower()}.py"
            if not os.path.exists(potential_file):
                 potential_file = f"spine_code/core/{module.split('.')[-1]}.py"

            if os.path.exists(potential_file):
                print(f"📄 Found dependency: {symbol} in {potential_file}")
                contract = self.contract_engine.generate_from_source(potential_file, symbol)
                if contract:
                    self.protocol.contracts[symbol] = contract
                    print(f"✅ Generated Shadow Contract for '{symbol}'")

    def get_shadow_stubs(self) -> str:
        """获取所有依赖的影子桩代码"""
        stubs = []
        for symbol, contract in self.protocol.contracts.items():
            stubs.append(f"# --- Shadow Stub for {symbol} ---")
            stubs.append(self.contract_engine.generate_shadow_stub(contract))
            stubs.append("\n")
        return "\n".join(stubs)

    def extract_shadow_snippet(self, node_id: str) -> str:
        """根据 ID 提取特定代码块，并进行影子化"""
        node = self.protocol.get_node_by_id(node_id)
        if not node:
            return "Node not found."
        
        # 🏛️ 物理切片
        lines = self.analyzer.source.splitlines()
        # 注意：ast 行号从 1 开始
        snippet_lines = lines[node.lines[0]-1 : node.lines[1]]
        raw_code = "\n".join(snippet_lines)
        
        # 🏛️ 语义影子化
        return self.shadow.generate_shadow_snippet(raw_code)

if __name__ == "__main__":
    # --- 演示 V2 跨文件契约功能 ---
    demo_file = "spine_code/main.py"
    print(f"🚀 [SpineCode V2] Starting secure orchestration for: {demo_file}")
    
    cli = SpineCodeCLI(demo_file)
    
    # 解析并生成影子契约
    cli.resolve_contracts()
    
    print("\n" + "="*50)
    print("🎭 SHADOW STUBS (What the AI sees for dependencies):")
    print("="*50)
    print(cli.get_shadow_stubs())
    
    # 模拟提取 main.py 的一段代码
    # 查找 SpineCodeCLI 类的 ID
    target_node = None
    for n in cli.protocol.spine:
        if n.t == "SpineCodeCLI":
            target_node = n
            break
            
    if target_node:
        print("\n[Step 2] Shadowed Main Logic (Referencing Shadowed Dependencies):")
        shadow_snippet = cli.extract_shadow_snippet(target_node.id)
        print("-" * 40)
        print(shadow_snippet[:300] + "...")
        print("-" * 40)
