"""
Shadow_Coding - AI 代码隐私保护网关
Copyright (C) 2026 严俊皓 <2857922968@qq.com>

基于 AGPLv3 许可证开源
https://github.com/yjh2222332024/Shadow_Coding
"""

import argparse
import sys
import threading
import time
import subprocess
import os
import json
from pathlib import Path
from shadow_coding.core.fs_tunnel import FileSystemTunnelV3
from shadow_coding.core.shadow import ShadowGenerator, AdaptiveNoiseConfig
from shadow_coding.core.contract_generator import ContractGenerator
from shadow_coding.core.models import SpineProtocol


class GhostLauncher:
    """
    【幽灵启动器】：管理 real/shadow/.spine_state 三目录架构。

    目录说明:
    - real/: AI 工作区 + 原始代码（AI 在这里写代码，人类也可运行）← 终端打开这里
    - shadow/: 影子代码（AI 看的混淆代码，只读参考）
    - .spine_state/: 映射表

    工作流程:
    1. AI 在 real/ 写代码（明文）
    2. 自动影子化到 shadow/（混淆后的）
    3. AI 下次看到的是混淆后的代码
    """
    def __init__(self, base_dir: Path = None):
        self.base_dir = Path(base_dir) if base_dir else Path(os.getcwd()).resolve()
        self.project_name = self.base_dir.name

        # V3 目录结构
        self.real_dir = self.base_dir / "real"
        self.shadow_dir = self.base_dir / "shadow"
        self.state_dir = self.base_dir / ".spine_state"
        self.config_file = self.base_dir / "shadow_config.json"

        # 加载或创建配置
        self.config = self._load_or_create_config()

        # 初始化隧道（real → shadow）
        self.tunnel = FileSystemTunnelV3(
            str(self.real_dir),     # 原始目录 = real（AI 在这里写代码）
            str(self.shadow_dir),   # 影子目录 = shadow（只读参考）
            str(self.state_dir)
        )

    def _load_or_create_config(self) -> dict:
        """加载或创建配置文件"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 创建新配置
        config = {
            "version": "3.3.1",
            "project": self.project_name,
            "real_dir": str(self.real_dir),
            "shadow_dir": str(self.shadow_dir),
            "state_dir": str(self.state_dir),
            "noise_mode": "production"
        }
        
        # 保存配置
        self.real_dir.mkdir(parents=True, exist_ok=True)
        self.shadow_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return config

    def start(self):
        """启动 Shadow_Coding"""
        print("\n" + "═" * 60)
        print(f"🚀 [Shadow_Coding V3.3.1] Initializing...")
        print(f"📂 Project: {self.project_name}")
        print(f"   Real:    {self.real_dir}")
        print(f"   Shadow:  {self.shadow_dir}")
        print(f"   State:   {self.state_dir}")
        print("═" * 60)

        # 1. 自动挂载
        self.tunnel.mount()

        # 2. 启动同步监听
        listener_thread = threading.Thread(target=self.tunnel.listen_and_sync, daemon=True)
        listener_thread.start()

        # 3. 打开新终端（针对 Windows 优化）- 终端打开 real/ 目录（AI 工作区）
        print(f"\n✨ Shadow Workspace ready at: {self.real_dir}")
        print(f"💻 Opening a NEW terminal for your AI work...")

        if sys.platform == "win32":
            # Windows: 使用 start 命令打开新终端
            subprocess.Popen(
                f'start "Shadow_Coding AI Workspace" cmd /k cd /d "{self.real_dir}"',
                shell=True
            )
        elif sys.platform == "darwin":
            # macOS: 使用 osascript 打开新终端
            subprocess.Popen([
                'osascript', '-e',
                f'tell app "Terminal" to do script "cd \'{self.real_dir}\'"'
            ])
        else:
            # Linux: 尝试使用 gnome-terminal 或 xterm
            try:
                subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f'cd "{self.real_dir}"; exec bash'])
            except FileNotFoundError:
                subprocess.Popen(['xterm', '-e', 'bash', '-c', f'cd "{self.real_dir}"; exec bash'])

        # 4. 主循环
        print("\n" + "═" * 60)
        print("🟢 TUNNEL ACTIVE. Don't close this window.")
        print("💡 AI should work in the NEW terminal (real directory)")
        print("💡 Changes in real/ will auto-shadow to shadow/ (with Security Audit)")
        print("═" * 60)
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down Shadow_Coding...")


def init_project():
    """初始化新项目"""
    base_dir = Path.cwd()
    
    # 检查是否已初始化
    config_file = base_dir / "shadow_config.json"
    if config_file.exists():
        print("⚠️  项目已初始化，删除 shadow_config.json 后重新初始化")
        print(f"   配置：{config_file}")
        return False
    
    # 创建目录结构
    real_dir = base_dir / "real"
    shadow_dir = base_dir / "shadow"
    state_dir = base_dir / ".spine_state"
    
    real_dir.mkdir(exist_ok=True)
    shadow_dir.mkdir(exist_ok=True)
    state_dir.mkdir(exist_ok=True)
    
    # 创建示例文件
    example_file = real_dir / "hello.py"
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
    
    # 创建配置文件
    config = {
        "version": "3.3.1",
        "project": base_dir.name,
        "real_dir": str(real_dir),
        "shadow_dir": str(shadow_dir),
        "state_dir": str(state_dir),
        "noise_mode": "production"
    }
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    # 创建.gitignore
    gitignore = base_dir / ".gitignore"
    gitignore.write_text('''# Shadow_Coding
shadow/
.spine_state/
shadow_config.json
*_shadow/
__pycache__/
*.pyc
*.pyo
*.log

# Python
env/
venv/
.venv/
build/
dist/
*.egg-info/
''')
    
    # 创建 README
    readme = base_dir / "README.md"
    readme.write_text(f'''# {base_dir.name}

Shadow_Coding 项目

## 目录结构

```
{base_dir.name}/
├── real/              # 原始代码区（人类可读）
├── shadow/            # 影子工作区（AI 用）
└── .spine_state/      # 受保护状态
```

## 使用方法

1. 在 `real/` 目录编写代码
2. 运行 `python shadow_coding_cli.py` 启动
3. 在新打开的终端（`shadow/` 目录）使用 AI 编程
4. AI 修改的代码会自动同步回 `real/`
''')
    
    print("✅ 项目初始化完成!")
    print(f"\n📁 目录结构:")
    print(f"   real/            - 原始代码区")
    print(f"   shadow/          - AI 工作区")
    print(f"   .spine_state/    - 受保护状态")
    print(f"\n📄 已创建文件:")
    print(f"   real/hello.py    - 示例代码")
    print(f"   shadow_config.json - 配置文件")
    print(f"   .gitignore       - Git 忽略规则")
    print(f"   README.md        - 项目说明")
    print(f"\n💡 下一步:")
    print(f"   1. 在 real/ 目录创建你的代码")
    print(f"   2. 运行 python shadow_coding_cli.py 启动")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Shadow_Coding - AI 代码隐私保护网关',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  shadow_coding init     初始化新项目
  shadow_coding start    启动 Shadow_Coding
  shadow_coding          等同于 start
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # init 命令
    init_parser = subparsers.add_parser('init', help='初始化新项目')
    
    # start 命令
    start_parser = subparsers.add_parser('start', help='启动 Shadow_Coding')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        init_project()
    elif args.command == 'start' or args.command is None:
        # 检查是否已初始化
        config_file = Path.cwd() / "shadow_config.json"
        if not config_file.exists():
            print("⚠️  项目未初始化，请先运行:")
            print(f"   shadow_coding init")
            print(f"\n或者从零开始:")
            print(f"   1. 在 real/ 目录创建代码")
            print(f"   2. 运行 shadow_coding start")
            # 自动初始化
            if input("\n是否现在初始化？[y/N]: ").lower() == 'y':
                init_project()
            else:
                sys.exit(1)
        
        launcher = GhostLauncher()
        launcher.start()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
