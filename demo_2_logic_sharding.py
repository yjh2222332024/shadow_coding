import ast
from spine_code.core.sharder import LogicSharder
from spine_code.core.shadow import ShadowGenerator
from spine_code.core.models import SpineProtocol

def run_demo():
    print("🚀 [Demo 2] Logic Sharding - The Coca-Cola Formula Protection")
    
    # 一个连贯的业务逻辑
    complex_code = """
def secret_pricing_algorithm(base, user_history, market_factor):
    # Step 1: User Profile Scoring
    score = sum(user_history) / len(user_history)
    
    # Step 2: Market Adjustment
    adj_base = base * (1 + market_factor)
    
    # Step 3: Final Computation
    if score > 0.8:
        return adj_base * 0.5
    return adj_base * 0.9
"""
    print("\n📄 Original Continuous Logic (Commercial Secret):")
    print(complex_code)

    # 执行碎片化
    protocol = SpineProtocol(project_id="Demo2", file_hash="X", spine=[])
    shadow_gen = ShadowGenerator(protocol)
    sharder = LogicSharder(shadow_gen)
    
    tree = ast.parse(complex_code)
    func_node = tree.body[0]
    
    # 将逻辑撕碎为 2 个片段
    sharded_nodes = sharder.shard_function(func_node, shard_count=2)
    tree.body = sharded_nodes
    
    sharded_source = ast.unparse(tree)
    print("\n🎭 Sharded & Shadowed Logic (The AI sees fragments):")
    print("-" * 60)
    # 进行语义混淆以便展示最终效果
    final_view = shadow_gen.generate_shadow_snippet(sharded_source)
    print(final_view)
    print("-" * 60)
    
    print("\n💡 Conclusion: AI only sees fragmented math blocks.")
    print("The 'Formula' is physically broken across different logic ghost helpers.")

if __name__ == "__main__":
    run_demo()
