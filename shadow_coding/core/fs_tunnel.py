"""
Shadow_Coding - AI 代码隐私保护网关
Copyright (C) 2026 严俊皓 <2857922968@qq.com>

基于 AGPLv3 许可证开源
https://github.com/yjh2222332024/Shadow_Coding
"""

import os
import shutil
import time
import ast
import logging
import tempfile
import re
import traceback
import hashlib
import json
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, Set, List, Optional, Any
from .analyzer import ASTAnalyzer
from .shadow import ShadowGenerator, AdaptiveNoiseConfig
from .contract_generator import ContractGenerator
from .dynamic_detector import DynamicFeatureDetector
from .security import SecurityAuditor, HumanSentinel, SecurityConfirmationRequired
from .exceptions import SecurityError, TunnelError
from .sharder import LogicSharder
from .models import SpineProtocol
import astunparse


class SecureLogger:
    """
    【安全日志记录器】：自动脱敏路径和敏感信息。
    """
    def __init__(self, name: str, real_dir: Path, shadow_dir: Path, state_dir: Path = None):
        self.logger = logging.getLogger(name)
        self.real_dir = real_dir
        self.shadow_dir = shadow_dir
        self.state_dir = state_dir

    def _sanitize(self, msg: Any) -> str:
        s = str(msg)
        # 1. 隐藏绝对路径根目录
        s = s.replace(str(self.real_dir), "[REAL_ROOT]")
        s = s.replace(str(self.shadow_dir), "[SHADOW_ROOT]")
        if self.state_dir:
            s = s.replace(str(self.state_dir), "[STATE_ROOT]")

        # 2. 隐藏用户主目录
        home = str(Path.home())
        s = s.replace(home, "~")

        # 3. 正则匹配常见路径模式（Windows & Linux）
        s = re.sub(r'/home/[^/\s]+', '~', s)
        s = re.sub(r'[a-zA-Z]:\\[Uu]sers\\[^\\]+', '~', s)

        # 4. 隐藏敏感环境变量路径可能包含的信息
        if "USERPROFILE" in os.environ:
             s = s.replace(os.environ["USERPROFILE"], "~")

        return s

    def info(self, msg, *args, **kwargs):
        self.logger.info(self._sanitize(msg), *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(self._sanitize(msg), *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        # 自动处理异常堆栈脱敏
        if 'exc_info' in kwargs and kwargs['exc_info']:
            if isinstance(kwargs['exc_info'], bool):
                kwargs['exc_info'] = self._sanitize(traceback.format_exc())
            else:
                try:
                    kwargs['exc_info'] = self._sanitize("".join(traceback.format_exception(*kwargs['exc_info'])))
                except:
                    pass
        self.logger.error(self._sanitize(msg), *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        if 'exc_info' in kwargs and kwargs['exc_info']:
             kwargs['exc_info'] = self._sanitize(traceback.format_exc())
        self.logger.critical(self._sanitize(msg), *args, **kwargs)


class FileSystemTunnelV3:
    """
    【Shadow-Tunnel V3】：重构版 - 支持 real/shadow/.spine_state 分离架构。
    
    目录结构:
        project/
        ├── real/              # 原始代码区（人类可读）
        ├── shadow/            # 影子工作区（AI 看到的混淆代码）
        └── .spine_state/      # 受保护状态（加密映射表）
    """
    
    def __init__(self, real_dir: str, shadow_dir: str, state_dir: str = None):
        self.real_dir = Path(real_dir).resolve()
        self.shadow_dir = Path(shadow_dir).resolve()
        self.state_dir = Path(state_dir).resolve() if state_dir else self.real_dir.parent / ".spine_state"
        
        self.project_name = self.real_dir.parent.name
        self.protocol = SpineProtocol(project_id=self.project_name, file_hash="v3", spine=[])
        self.shadow_gen = ShadowGenerator(self.protocol)
        self.contract_engine = ContractGenerator(self.shadow_gen)
        self.detector = DynamicFeatureDetector()
        self.auditor = SecurityAuditor()
        self.sentinel = HumanSentinel(timeout=15)
        self._last_mtime: Dict[str, float] = {}

        # 初始化安全日志
        self.logger = SecureLogger('Shadow_Coding.tunnel', self.real_dir, self.shadow_dir, self.state_dir)

    def _is_safe_path(self, path: Path, root: Path) -> bool:
        """检查路径是否在允许的根目录内，防止目录穿越"""
        try:
            resolved_path = path.resolve()
            resolved_root = root.resolve()
            return resolved_root in resolved_path.parents or resolved_path == resolved_root
        except Exception:
            return False

    def _init_state_dir(self):
        """初始化受保护状态目录"""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        # 设置目录权限（仅当前用户可访问）
        try:
            os.chmod(str(self.state_dir), 0o700)
        except Exception:
            pass  # Windows 可能不支持

    def mount(self):
        """挂载：real → shadow (影子化)"""
        self.logger.info(f"🔄 [V3] Mounting {self.real_dir} to {self.shadow_dir}...")
        
        # 初始化状态目录
        self._init_state_dir()
        
        # 清理并重建影子目录
        if self.shadow_dir.exists():
            try:
                shutil.rmtree(self.shadow_dir)
            except Exception as e:
                self.logger.warning(f"无法清理影子目录：{e}")

        self.shadow_dir.mkdir(parents=True, exist_ok=True)

        # 检查原始目录是否为空
        if not self.real_dir.exists() or not any(self.real_dir.rglob('*.py')):
            self.logger.warning("⚠️  real/ 目录为空，创建示例文件...")
            self._create_example_files()

        try:
            # 第一遍扫描：建立全局混淆表
            py_files = list(self.real_dir.rglob('*.py'))
            if not py_files:
                self.logger.warning("⚠️  未找到 Python 文件")
            else:
                for real_file_path in py_files:
                    if not self._is_safe_path(real_file_path, self.real_dir):
                        continue

                    analyzer = ASTAnalyzer(str(real_file_path))
                    protocol = analyzer.analyze()
                    self.shadow_gen.protocol.spine.extend(protocol.spine)

            # 生成混淆表
            self.shadow_gen.obfuscate_spine()

            # 保存映射表到受保护目录
            self._save_mapping_table()

            # 第二遍扫描：生成影子文件
            for real_path in self.real_dir.rglob('*.py'):
                if not self._is_safe_path(real_path, self.real_dir):
                    continue

                rel_path = real_path.relative_to(self.real_dir)
                shadow_path = self.shadow_dir / rel_path

                self._sync_real_to_shadow(real_path, shadow_path)

            # 生成符号桩
            for real_path in py_files:
                self._generate_stubs_for_file(real_path)

        except Exception as e:
            self.logger.error(f"挂载过程发生错误：{e}", exc_info=True)
            raise TunnelError(f"挂载失败：{e}")

        self.logger.info(f"✅ [V3] Mount complete.")
        self.logger.info(f"   Real:    {self.real_dir}")
        self.logger.info(f"   Shadow:  {self.shadow_dir}")
        self.logger.info(f"   State:   {self.state_dir}")

    def _create_example_files(self):
        """创建示例文件"""
        example_file = self.real_dir / "hello.py"
        example_file.write_text('''"""示例文件 - 删除此文件并开始编写你的代码"""

def greet(name: str) -> str:
    """问候函数"""
    return f"Hello, {name}!"


def calculate_sum(a: int, b: int) -> int:
    """计算两数之和"""
    return a + b


if __name__ == "__main__":
    print(greet("World"))
    print(f"1 + 2 = {calculate_sum(1, 2)}")
''')
        self.logger.info(f"✅ 创建示例文件：{example_file}")

    def _save_mapping_table(self):
        """保存映射表到受保护目录"""
        mapping_file = self.state_dir / "mapping.json.enc"
        mapping_data = {
            "version": "3.3.1",
            "project": self.project_name,
            "created_at": datetime.now().isoformat(),
            "mapping": dict(self.shadow_gen._mapping.items()),
            "reverse_mapping": dict(self.shadow_gen._reverse_mapping.items())
        }
        # Base64 编码（简单加密，防止直接读取）
        encrypted = base64.b64encode(json.dumps(mapping_data, ensure_ascii=False).encode('utf-8')).decode('utf-8')
        with open(mapping_file, 'w', encoding='utf-8') as f:
            f.write(encrypted)
        self.logger.info(f"🔒 映射表已保存到：{mapping_file}")

    def _load_mapping_table(self) -> bool:
        """从受保护目录加载映射表"""
        mapping_file = self.state_dir / "mapping.json.enc"
        if not mapping_file.exists():
            return False
        
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                encrypted = f.read()
            decoded = base64.b64decode(encoded).decode('utf-8')
            mapping_data = json.loads(decoded)
            
            # 恢复映射表
            for real_name, shadow_name in mapping_data.get("mapping", {}).items():
                self.shadow_gen._mapping[real_name] = shadow_name
                self.shadow_gen._reverse_mapping[shadow_name] = real_name
            
            self.logger.info(f"📖 已加载映射表：{len(mapping_data.get('mapping', {}))} 条记录")
            return True
        except Exception as e:
            self.logger.error(f"加载映射表失败：{e}")
            return False

    def _generate_stubs_for_file(self, real_path: Path):
        """生成符号桩文件"""
        try:
            analyzer = ASTAnalyzer(str(real_path))
            analyzer._collect_imports()

            for symbol, module in analyzer.imports.items():
                clean_module = module.lstrip('.')
                level = len(module) - len(clean_module)

                if level > 0:
                    base_dir = real_path.parent
                    for _ in range(level - 1):
                        if base_dir.parent == base_dir:
                            break
                        base_dir = base_dir.parent
                    potential_real_path = base_dir / (clean_module.replace('.', '/') + ".py")
                else:
                    potential_real_path = self.real_dir / (clean_module.replace('.', '/') + ".py")

                if not self._is_safe_path(potential_real_path, self.real_dir):
                    continue

                if potential_real_path.exists():
                    contract = self.contract_engine.generate_from_source(str(potential_real_path), symbol)
                    if contract:
                        rel_stub_path = potential_real_path.relative_to(self.real_dir)
                        shadow_stub_path = self.shadow_dir / rel_stub_path.parent / f"{contract.shadow_name.lower()}_stub.py"

                        if not self._is_safe_path(shadow_stub_path, self.shadow_dir):
                            continue

                        shadow_stub_path.parent.mkdir(parents=True, exist_ok=True)
                        self._atomic_write(shadow_stub_path, f"# SEC-CODE L2 SHADOW STUB\n{self.contract_engine.generate_shadow_stub(contract)}")
        except Exception as e:
            self.logger.warning(f"生成符号桩失败 ({real_path.name}): {e}")

    def _atomic_write(self, path: Path, content: str):
        """原子化写入：先写临时文件再重命名"""
        dir_path = path.parent
        dir_path.mkdir(parents=True, exist_ok=True)

        temp_fd, temp_path = tempfile.mkstemp(dir=str(dir_path), text=True, suffix=".tmp")
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                f.write(content)
            os.replace(temp_path, str(path))
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            self.logger.error(f"原子写入失败 ({path.name}): {e}")
            raise TunnelError(f"文件写入失败：{e}")

    def _sync_real_to_shadow(self, real_path: Path, shadow_path: Path):
        """原始目录 → 影子目录 (影子化)"""
        try:
            with open(real_path, 'r', encoding='utf-8') as f:
                content = f.read()

            features = self.detector.detect(content)
            if self.detector.should_reject(features):
                self._write_warning_file(real_path, shadow_path, features)
                return

            try:
                tree = ast.parse(content)
                sharder = LogicSharder(self.shadow_gen)

                new_nodes = []
                for node in tree.body:
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        is_sensitive = sharder._is_sensitive_ast(node.body)
                        if is_sensitive:
                            node.body = [
                                ast.Expr(value=ast.Constant(value="[🛡️ SECURE_LOCAL_ONLY_LOGIC]")),
                                ast.Return(value=ast.Constant(value=None))
                            ]
                            new_nodes.append(node)
                            self.logger.info(f"🔒 [V3.1.1] Intercepted sensitive function: {node.name}")
                        else:
                            shards = sharder.shard_function(node)
                            new_nodes.extend(shards)
                    elif isinstance(node, ast.ClassDef):
                        new_class_body = []
                        for item in node.body:
                            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                if sharder._is_sensitive_ast(item.body):
                                    item.body = [
                                        ast.Expr(value=ast.Constant(value="[🛡️ SECURE_LOCAL_ONLY_LOGIC]")),
                                        ast.Return(value=ast.Constant(value=None))
                                    ]
                                    new_class_body.append(item)
                                else:
                                    shards = sharder.shard_function(item)
                                    new_class_body.extend(shards)
                            else:
                                new_class_body.append(item)
                        node.body = new_class_body
                        new_nodes.append(node)
                    else:
                        new_nodes.append(node)

                tree.body = new_nodes
                sharded_source = astunparse.unparse(tree)
            except Exception as se:
                self.logger.error(f"碎片化失败 ({real_path.name}): {se}")
                sharded_source = content

            shadow_content = self.shadow_gen.generate_shadow_snippet(sharded_source)
            if features:
                shadow_content = "# ⚠️ [L3 Warning] Reflective patterns detected.\n" + shadow_content

            self._atomic_write(shadow_path, shadow_content)
            self._last_mtime[str(shadow_path)] = shadow_path.stat().st_mtime
        except Exception as e:
             self.logger.error(f"同步到影子目录失败 ({real_path.name}): {e}")

    def _write_warning_file(self, real_path, shadow_path, features):
        """写入警告文件"""
        warning_path = shadow_path.with_suffix(".py.WARNING")
        try:
            report = self.detector.generate_report(features) + "\n\n💡 Shadow_Coding: File blocked."
            self._atomic_write(warning_path, report)
            self.logger.warning(f"🚫 [L3 Sentinel] Rejected: {real_path.name}")
        except Exception as e:
            self.logger.error(f"写入警告文件失败：{e}")

    def _sync_shadow_to_real(self, shadow_path: Path, real_path: Path):
        """影子目录 → 原始目录 (还原)"""
        try:
            if not shadow_path.exists():
                return

            # 1. 审计前读取并计算指纹
            with open(shadow_path, 'r', encoding='utf-8') as f:
                shadow_content = f.read()
            pre_audit_hash = hashlib.sha256(shadow_content.encode()).hexdigest()

            # 2. 执行安全审计
            try:
                self.auditor.audit(shadow_content, mode="restore")
            except SecurityConfirmationRequired as scr:
                if not self.sentinel.request_approval(scr.operation, scr.target, shadow_content):
                    self.logger.warning(f"🚫 [SENTINEL] User rejected or timeout: {shadow_path.name}")
                    self._last_mtime[str(shadow_path)] = shadow_path.stat().st_mtime
                    return
            except SecurityError as sv:
                self.logger.critical(f"检测到恶意还原尝试 ({shadow_path.name}): {sv}")
                self._last_mtime[str(shadow_path)] = shadow_path.stat().st_mtime
                return

            # 3. 审计后再次校验指纹
            with open(shadow_path, 'r', encoding='utf-8') as f:
                content_post = f.read()
            post_audit_hash = hashlib.sha256(content_post.encode()).hexdigest()

            if pre_audit_hash != post_audit_hash:
                self.logger.critical(f"🚨 [TOCTOU] Detected content modification during audit! Aborting sync: {shadow_path.name}")
                self._last_mtime[str(shadow_path)] = shadow_path.stat().st_mtime
                return

            # 4. 还原并原子化写入
            real_content = self.shadow_gen.restore_snippet(content_post)
            self._atomic_write(real_path, real_content)
            self._last_mtime[str(shadow_path)] = shadow_path.stat().st_mtime
            self.logger.info(f"📝 [V3] Synced {real_path.name}")
        except Exception as e:
            self.logger.error(f"反向同步失败 ({real_path.name}): {e}")

    def listen_and_sync(self):
        """监听 real 目录变化并影子化到 shadow 目录"""
        self.logger.info("📡 启动监听同步服务...")
        try:
            while True:
                time.sleep(1)
                # 监听 real/ 目录变化 → 影子化到 shadow/
                for root, _, files in os.walk(self.real_dir):
                    for file in files:
                        if "_stub" in file or not file.endswith('.py'):
                            continue
                        real_path = Path(root) / file
                        if not self._is_safe_path(real_path, self.real_dir):
                            continue

                        rel_path = real_path.relative_to(self.real_dir)
                        shadow_path = self.shadow_dir / rel_path

                        try:
                            mtime = real_path.stat().st_mtime
                            if mtime > self._last_mtime.get(str(shadow_path), 0):
                                self._sync_real_to_shadow(real_path, shadow_path)
                        except FileNotFoundError:
                            continue
                        except Exception as e:
                            self.logger.error(f"同步轮询异常：{e}")
        except KeyboardInterrupt:
            self.logger.info("🛑 停止监听同步服务.")
