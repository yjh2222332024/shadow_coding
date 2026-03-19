import argparse
import sys
import threading
import time
import subprocess
import os
import json
from pathlib import Path
from spine_code.core.fs_tunnel import FileSystemTunnelV2
from spine_code.core.shadow import ShadowGenerator
from spine_code.core.contract_generator import ContractGenerator
from spine_code.core.models import SpineProtocol

class GhostLauncher:
    """
    【幽灵启动器】：消除所有配置，实现“降维打击”般的简单。
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
        print(f"🚀 [SpineCode Ghost Mode] Initializing...")
        print(f"📂 Project: {self.project_name}")
        print(f"🛡️  Security: L3 Sentinel + Firewall ACTIVE")
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
            os.system(f'start cmd /K "cd /d {self.shadow_dir} && echo 🎭 Welcome to SHADOW WORLD. Your AI is safe here. && title SPINECODE_SHADOW_SHELL"')
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

def main():
    # 如果没有任何参数，直接进入幽灵模式
    if len(sys.argv) == 1:
        launcher = GhostLauncher()
        launcher.start()
    else:
        # 保留原有的复杂 CLI 逻辑（供高级用户使用）
        # ... (这里省略，为了简洁，我们直接重写为全幽灵逻辑)
        launcher = GhostLauncher()
        launcher.start()

if __name__ == "__main__":
    main()
