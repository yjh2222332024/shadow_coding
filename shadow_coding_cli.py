"""
Shadow_Coding - AI 代码隐私保护网关
Copyright (C) 2026 严俊皓 <2857922968@qq.com>

基于 AGPLv3 许可证开源
https://github.com/yjh2222332024/shadow_coding
"""

import argparse
import sys
import threading
import time
import subprocess
import os
import json
from pathlib import Path
from shadow_coding.core.fs_tunnel import FileSystemTunnelV2
from shadow_coding.core.shadow import ShadowGenerator, AdaptiveNoiseConfig
from shadow_coding.core.contract_generator import ContractGenerator
from shadow_coding.core.models import SpineProtocol

class GhostLauncher:
    """
    【幽灵启动器】：消除所有配置，实现"降维打击"般的简单。
    """
    def __init__(self):
        self.real_dir = Path(os.getcwd()).resolve()
        self.project_name = self.real_dir.name
        self.shadow_dir = self.real_dir.parent / f"{self.project_name}_shadow"

        # 初始化核心引擎
        self.protocol = SpineProtocol(project_id=self.project_name, file_hash="v2", spine=[])
        self.shadow_gen = ShadowGenerator(self.protocol)
        self.contract_engine = ContractGenerator(self.shadow_gen)
        self.tunnel = FileSystemTunnelV2(str(self.real_dir), str(self.shadow_dir))
        self.tunnel.set_engines(self.shadow_gen, self.contract_engine)

    def start(self):
        print("\n" + "═"*60)
        print(f"🚀 [Shadow_Coding Ghost Mode] Initializing...")
        print(f"📂 Project: {self.project_name}")
        print(f"🛡️  Security: L3 Sentinel + Firewall ACTIVE")

        # 🛡️ V3.1: 打印安全模式提示（增强版）
        print(f"\n{AdaptiveNoiseConfig.get_status_info()}")

        print("═"*60)

        # 1. 自动挂载
        self.tunnel.mount()

        # 2. 启动同步监听
        listener_thread = threading.Thread(target=self.tunnel.listen_and_sync, daemon=True)
        listener_thread.start()

        # 3. 自动弹出一个新的终端（针对 Windows 优化）
        print(f"\n✨ Shadow Workspace ready at: {self.shadow_dir}")
        print(f"💻 Opening a NEW terminal for your AI work...")

        if sys.platform == "win32":
            # 自动在影子目录打开一个新的 cmd 窗口
            os.system(f'start cmd /K "cd /d {self.shadow_dir} && echo 🎭 Welcome to SHADOW WORLD. Your AI is safe here. && title SHADOW_CODING_SHADOW_SHELL"')
        else:
            # macOS/Linux 逻辑
            print(f"👉 Please open your IDE/Terminal in: {self.shadow_dir}")

        print("\n" + "═"*60)
        print("🟢 TUNNEL ACTIVE. Don't close this window.")
        print("💡 Any changes in Shadow will auto-sync back to Real (with Security Audit).")
        print("═"*60 + "\n")

        try:
            while True: time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Ghost Mode Stopped. Securely unmounting...")


class ConfigManager:
    """
    【配置管理器】：管理 API Key 和噪声配置
    """
    def __init__(self):
        self.config_dir = Path.home() / ".shadow_coding"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load_config(self) -> dict:
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"api_keys": {}, "noise_enabled": False, "noise_ratio": 0.0}

    def save_config(self, config: dict):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def add_key(self, vendor: str, key: str):
        config = self.load_config()
        config["api_keys"][vendor] = key
        self.save_config(config)
        print(f"✅ API Key for '{vendor}' added.")

    def remove_key(self, vendor: str):
        config = self.load_config()
        if vendor in config["api_keys"]:
            del config["api_keys"][vendor]
            self.save_config(config)
            print(f"✅ API Key for '{vendor}' removed.")
        else:
            print(f"⚠️  No API Key found for '{vendor}'.")

    def list_keys(self):
        config = self.load_config()
        print("\n📋 Shadow_Coding Configuration:")
        print("-" * 40)
        print(f"Noise Injection: {'Enabled' if config.get('noise_enabled') else 'Disabled'}")
        if config.get('noise_enabled'):
            print(f"Noise Ratio: {config.get('noise_ratio', 0.0):.0%}")
        print(f"\nAPI Keys:")
        if config["api_keys"]:
            for vendor, key in config["api_keys"].items():
                masked = key[:5] + "..." + key[-3:] if len(key) > 8 else "***"
                print(f"  • {vendor}: {masked}")
        else:
            print("  (No API Keys configured)")
        print()

    def set_noise(self, enabled: bool, ratio: float = 0.0):
        config = self.load_config()
        config["noise_enabled"] = enabled
        config["noise_ratio"] = ratio
        self.save_config(config)

        # 应用到运行时配置
        if enabled:
            AdaptiveNoiseConfig.enable_developer_mode(ratio)
            print(f"✅ Noise injection enabled: {ratio:.0%}")
        else:
            AdaptiveNoiseConfig.enable_production_mode()
            print(f"✅ Noise injection disabled (Production Mode)")


def main():
    parser = argparse.ArgumentParser(
        description="Shadow_Coding - Secure AI Gateway",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  shadow_coding                 # Start Ghost Mode
  shadow_coding --version       # Show version
  shadow_coding config --list   # List configuration
  shadow_coding config --add-key openai sk-xxx
        """
    )

    parser.add_argument(
        '--version',
        action='version',
        version='Shadow_Coding 3.1.0-alpha'
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # config 命令
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_parser.add_argument('--list', action='store_true', help='List current configuration')
    config_parser.add_argument('--add-key', nargs=2, metavar=('VENDOR', 'KEY'), help='Add API Key')
    config_parser.add_argument('--remove-key', metavar='VENDOR', help='Remove API Key')
    config_parser.add_argument('--noise', action='store_true', help='Configure noise injection')
    config_parser.add_argument('--enable', action='store_true', help='Enable noise')
    config_parser.add_argument('--disable', action='store_true', help='Disable noise')
    config_parser.add_argument('--ratio', type=float, default=0.2, help='Noise ratio (default: 0.2)')

    args = parser.parse_args()

    # 处理 config 命令
    if args.command == 'config':
        manager = ConfigManager()

        if args.list:
            manager.list_keys()
        elif args.add_key:
            manager.add_key(args.add_key[0], args.add_key[1])
        elif args.remove_key:
            manager.remove_key(args.remove_key)
        elif args.noise:
            if args.disable:
                manager.set_noise(False, 0.0)
            elif args.enable:
                manager.set_noise(True, args.ratio)
            else:
                print("⚠️  Use --enable or --disable with --noise")
        else:
            config_parser.print_help()
    else:
        # 幽灵模式
        launcher = GhostLauncher()
        launcher.start()

if __name__ == "__main__":
    main()
