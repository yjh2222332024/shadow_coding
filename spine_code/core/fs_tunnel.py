import os
import shutil
import time
import ast # 🏛️ 必须导入 ast 库
from pathlib import Path
from typing import Dict, Set, List
from .analyzer import ASTAnalyzer
from .shadow import ShadowGenerator
from .contract_generator import ContractGenerator

from .dynamic_detector import DynamicFeatureDetector
from .security import SecurityAuditor, SecurityViolation
from .sharder import LogicSharder
import astunparse # 用于将混淆后的 AST 转换回源码

class FileSystemTunnelV2:
    """
    【Shadow-Tunnel V2】：集成 L2 契约、L3 探测、安全审计与逻辑碎片化。
    """
    def __init__(self, real_dir: str, shadow_dir: str):
        self.real_dir = Path(real_dir).resolve()
        self.shadow_dir = Path(shadow_dir).resolve()
        self.shadow_gen = None
        self.contract_engine = None
        self.detector = DynamicFeatureDetector()
        self.auditor = SecurityAuditor()
        self._last_mtime: Dict[str, float] = {}

    def set_engines(self, shadow_gen: ShadowGenerator, contract_engine: ContractGenerator):
        self.shadow_gen = shadow_gen
        self.contract_engine = contract_engine

    def mount(self):
        print(f"🔄 [V2] Mounting {self.real_dir} to {self.shadow_dir}...")
        if self.shadow_dir.exists():
            try:
                shutil.rmtree(self.shadow_dir)
            except Exception as e:
                print(f"⚠️ Warning: Could not fully clear shadow dir: {e}")
        self.shadow_dir.mkdir(parents=True, exist_ok=True)

        # 第一遍扫描：建立全局混淆表
        for root, _, files in os.walk(self.real_dir):
            for file in files:
                if not file.endswith('.py'): continue
                analyzer = ASTAnalyzer(os.path.join(root, file))
                protocol = analyzer.analyze()
                self.shadow_gen.protocol.spine.extend(protocol.spine)
        
        self.shadow_gen.obfuscate_spine()

        # 第二遍扫描：生成文件与影子桩
        for root, _, files in os.walk(self.real_dir):
            for file in files:
                if not file.endswith('.py'): continue
                
                real_path = Path(root) / file
                rel_path = real_path.relative_to(self.real_dir)
                shadow_path = self.shadow_dir / rel_path
                
                self._sync_real_to_shadow(real_path, shadow_path)
                self._generate_stubs_for_file(real_path)

        print(f"✅ [V2] Mount complete.")

    def _generate_stubs_for_file(self, real_path: Path):
        analyzer = ASTAnalyzer(str(real_path))
        analyzer._collect_imports()
        
        for symbol, module in analyzer.imports.items():
            # 🏛️ 修复路径解析：处理相对导入前缀
            clean_module = module.lstrip('.')
            level = len(module) - len(clean_module)
            
            if level > 0:
                # 相对导入查找
                base_dir = real_path.parent
                for _ in range(level - 1):
                    base_dir = base_dir.parent
                potential_real_path = base_dir / (clean_module.replace('.', '/') + ".py")
            else:
                # 绝对/顶层导入查找
                potential_real_path = self.real_dir / (clean_module.replace('.', '/') + ".py")
            
            if potential_real_path.exists():
                contract = self.contract_engine.generate_from_source(str(potential_real_path), symbol)
                if contract:
                    # 🏛️ 结构化桩：保持原有目录深度
                    rel_stub_path = potential_real_path.relative_to(self.real_dir)
                    # 影子名称化文件名 (可选) 或 保持原名但加 _stub
                    shadow_stub_path = self.shadow_dir / rel_stub_path.parent / f"{contract.shadow_name.lower()}_stub.py"
                    
                    shadow_stub_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(shadow_stub_path, 'w', encoding='utf-8') as f:
                        f.write(f"# SEC-CODE L2 SHADOW STUB\n{self.contract_engine.generate_shadow_stub(contract)}")

    def _sync_real_to_shadow(self, real_path: Path, shadow_path: Path):
        shadow_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(real_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 🛡️ L3 级安全哨兵检测
            features = self.detector.detect(content)
            if self.detector.should_reject(features):
                self._write_warning_file(real_path, shadow_path, features)
                return

            # 🏛️ [Logic Sharding] 核心逻辑碎片化
            try:
                tree = ast.parse(content)
                sharder = LogicSharder(self.shadow_gen)
                
                # 对顶层函数和类方法执行碎片化
                new_nodes = []
                for node in tree.body:
                    if isinstance(node, ast.FunctionDef):
                        new_nodes.extend(sharder.shard_function(node))
                    elif isinstance(node, ast.ClassDef):
                        new_class_body = []
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                new_class_body.extend(sharder.shard_function(item))
                            else:
                                new_class_body.append(item)
                        node.body = new_class_body
                        new_nodes.append(node)
                    else:
                        new_nodes.append(node)
                
                tree.body = new_nodes
                # 转换回源码进行最后的语义脱敏
                sharded_source = ast.unparse(tree)
            except Exception as se:
                print(f"⚠️ Sharding bypassed for {real_path.name}: {se}")
                sharded_source = content

            # 🏛️ 执行最终语义脱敏
            shadow_content = self.shadow_gen.generate_shadow_snippet(sharded_source)
            
            # 如果有中危特征，添加源码内警告
            if features:
                shadow_content = "# ⚠️ [L3 Warning] Reflective patterns detected.\n" + shadow_content

            with open(shadow_path, 'w', encoding='utf-8') as f:
                f.write(shadow_content)
            self._last_mtime[str(shadow_path)] = shadow_path.stat().st_mtime
        except Exception as e:
             print(f"⚠️ Sync Error for {real_path.name}: {e}")

    def _write_warning_file(self, real_path, shadow_path, features):
        warning_path = shadow_path.with_suffix(".py.WARNING")
        with open(warning_path, 'w', encoding='utf-8') as f:
            f.write(self.detector.generate_report(features))
            f.write("\n\n💡 SpineCode: File blocked due to L3 Dynamic Features.")
        print(f"🚫 [L3 Sentinel] Rejected: {real_path.name}")

    def _add_jit_symbols(self, nodes: List):
        """递归将新符号注入影子生成器"""
        for node in nodes:
            # 确保 get_or_create_mapping 被调用
            self.shadow_gen.get_or_create_mapping(node.t)
            if node.children:
                self._add_jit_symbols(node.children)

    def _sync_shadow_to_real(self, shadow_path: Path, real_path: Path):
        try:
            with open(shadow_path, 'r', encoding='utf-8') as f:
                shadow_content = f.read()

            # 🛡️ [Security Firewall] 还原前审计 AI 代码意图
            try:
                self.auditor.audit(shadow_content)
            except SecurityViolation as sv:
                print(f"\n❌ {sv}")
                print(f"🚨 [CRITICAL] Blocked malicious attempt in {shadow_path.name}. Real source is PROTECTED.")
                # 记录黑名单，停止当前文件的自动同步，防止重复报错
                self._last_mtime[str(shadow_path)] = shadow_path.stat().st_mtime
                return

            real_content = self.shadow_gen.restore_snippet(shadow_content)
            with open(real_path, 'w', encoding='utf-8') as f:
                f.write(real_content)
            self._last_mtime[str(shadow_path)] = shadow_path.stat().st_mtime
            print(f"📝 [V2] Synced {real_path.name}")
        except Exception as e:
            print(f"⚠️ Reverse Sync Error for {real_path.name}: {e}")

    def listen_and_sync(self):
        try:
            while True:
                time.sleep(1) # 降低延迟至 1 秒
                for root, _, files in os.walk(self.shadow_dir):
                    for file in files:
                        if "_stub" in file or not file.endswith('.py'): continue
                        shadow_path = Path(root) / file
                        real_path = self.real_dir / shadow_path.relative_to(self.shadow_dir)
                        if not real_path.exists(): continue
                        
                        mtime = shadow_path.stat().st_mtime
                        if mtime > self._last_mtime.get(str(shadow_path), 0):
                            self._sync_shadow_to_real(shadow_path, real_path)
        except KeyboardInterrupt:
            pass
