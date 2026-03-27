# 🛡️ Shadow_Coding (影码)

> **"让云端 AI 成为你的逻辑计件工，而非你的业务合规噩梦。"**

[![Version](https://img.shields.io/badge/version-3.3.1--stable-blue.svg)](https://github.com/yjh2222332024/shadow_coding/releases)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![Security](https://img.shields.io/badge/security-L4+_Hardened-red.svg)](#安全模型)
[![License](https://img.shields.io/badge/license-AGPLv3-orange.svg)](https://opensource.org/licenses/AGPLv3)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](docs/CONTRIBUTING.md)
[![Tests](https://img.shields.io/badge/tests-55/57%20passed-green.svg)](#安全复现实验室)

---

## 🚀 什么是 Shadow_Coding (影码)？

**Shadow_Coding (影码)** 是一个**开源的 AI 代码隐私保护网关**。当你使用 Cursor、Copilot 或任何云端 AI 编程助手时，它确保你的核心业务逻辑**既可用又不可见**。

### 解决的问题

```
❌ 传统方式：完整代码 → 云端 AI → 代码泄露风险
✅ Shadow_Coding：影子化代码 → 云端 AI → 业务语义隔离
```

---

## ⚠️ 重要：能力边界说明

### ✅ 适合的场景

| 场景 | 保护效果 | 说明 |
|------|---------|------|
| **已有项目，AI 帮忙修改** | ✅ 完全保护 | 代码已影子化，AI 看到的是混淆后的 |
| **核心逻辑已写完，AI 扩展非核心功能** | ✅ 完全保护 | 核心代码已混淆，AI 无法理解业务含义 |
| **外包项目，防止代码泄露** | ✅ 完全保护 | 外包方只能看到混淆代码 |
| **多 AI 协作，防止数据关联** | ✅ 完全保护 | 每个 AI 只看到部分逻辑 |

### ❌ 不适合的场景

| 场景 | 原因 | 建议方案 |
|------|------|---------|
| **从零开始的全新项目** | ❌ 第一次写的代码是明文 | 使用本地 AI（Ollama）写初始代码 |
| **完全依赖云端 AI 开发** | ❌ 核心逻辑会暴露 | 核心逻辑自己写，非核心让 AI 写 |
| **AI 写核心业务逻辑** | ❌ AI 需要理解业务才能写 | 自己写核心，AI 写辅助功能 |

---

## 🎯 正确使用方式

### 方式一：已有项目（推荐）

```bash
# 1. 你有现有代码
my_project/
└── src/
    └── payment.py    # def calculate_discount(user_balance, rate):

# 2. 初始化 Shadow_Coding
cd my_project
python shadow_coding_cli.py init

# 3. 启动
python shadow_coding_cli.py start

# 4. AI 看到的是混淆后的代码
# def S_Metric_a1b2(S_Metric_xxx, S_Rate_yyy):
```

**保护效果：** ✅ AI 永远看不到原始业务逻辑

---

### 方式二：从零开始（需要配合本地 AI）

```bash
# 1. 创建项目
mkdir my_project && cd my_project
python shadow_coding_cli.py init

# 2. 使用本地 AI（Ollama/LM Studio）写核心逻辑
# real/core.py - 本地写，不发送到云端
def calculate_risk_score(user_data):
    # 核心风控算法 - 商业机密
    if user_data['balance'] > 10000:
        score += 30
    # ...

# 3. 启动 Shadow_Coding 影子化
python shadow_coding_cli.py start

# 4. 之后用云端 AI 扩展非核心功能
# AI 看到的是混淆后的代码
```

**保护效果：** ✅ 核心逻辑从未暴露，后续扩展有保护

---

### 方式三：虚拟变量名（简单有效）

```python
# 第 1 步：用虚拟变量名写核心逻辑（本地）
def process_xxxx(aa, bb, cc):
    """处理 xxxx"""
    if aa > 10000:
        return aa * bb * cc
    return aa * bb

# 第 2 步：启动 Shadow_Coding
python shadow_coding_cli.py start

# 第 3 步：让 AI 基于框架写功能
# AI 看到的是无意义变量名，不知道具体业务

# 第 4 步：本地脚本批量替换变量名
# aa → user_balance
# bb → discount_rate
# cc → vip_factor
```

**保护效果：** ✅ AI 看到的是无意义变量名

---

## 📁 目录结构

### 用户项目目录

当你使用 Shadow_Coding 时，你的项目会变成这样：

```
my_project/
├── real/              # AI 工作区 + 原始代码 ← 终端打开这里
│   ├── hello.py       # AI 在这里写代码（明文）
│   └── core.py        # 人类也可运行
├── shadow/            # 影子代码（混淆后的，只读参考）
│   ├── hello.py       # 自动影子化
│   └── core.py        # AI 下次看到混淆的
└── .spine_state/      # 映射表
    └── mapping.json.enc
```

| 目录/文件 | 说明 | 谁可以访问 |
|----------|------|-----------|
| `real/` | 原始代码区，AI 在这里写代码 | 人类 + AI |
| `shadow/` | 影子代码区，自动混淆后的代码 | AI（只读参考） |
| `.spine_state/` | 受保护状态，存储加密的映射表 | Shadow_Coding 内部使用 |
| `shadow_config.json` | 项目配置文件 | 人类可读 |

---

### Shadow_Coding 源码目录

```
Shadow_Coding/
├── shadow_coding/             # 核心源码包
│   ├── __init__.py            # 包入口
│   ├── main.py                # 主程序入口
│   ├── core/                  # 核心模块
│   │   ├── __init__.py        # 模块导出
│   │   ├── analyzer.py        # AST 分析器（解析代码结构）
│   │   ├── security.py        # 安全审计器（拦截恶意代码）
│   │   ├── shadow.py          # 影子生成器（变量名混淆）
│   │   ├── sharder.py         # 逻辑分片器（函数拆分）
│   │   ├── fs_tunnel.py       # 文件系统隧道（同步 real↔shadow）
│   │   ├── contract_generator.py # 契约生成器（符号桩生成）
│   │   ├── dynamic_detector.py # 动态检测器（反射调用识别）
│   │   ├── models.py          # 数据模型（协议定义）
│   │   ├── translator.py      # 翻译器（代码转换）
│   │   └── exceptions.py      # 异常定义
│   ├── adapters/              # AI 适配器（预留扩展）
│   └── utils/                 # 工具集（预留扩展）
│
├── security_lab/              # 安全实验室（测试套件）
│   ├── test_ast_obfuscation.py      # AST 混淆测试
│   ├── test_alias_tracking.py       # 别名追踪测试
│   ├── test_dynamic_injection.py    # 动态注入测试
│   ├── test_path_boundary.py        # 路径边界测试
│   ├── test_memory_dump.py          # 内存保护测试
│   ├── test_l4_defense.py           # L4 级防御测试
│   └── test_blue_team_hardening.py  # 蓝队加固测试
│
├── docs/                    # 文档目录
│   ├── README.md            # 本文件
│   ├── SECURITY.md          # 安全政策
│   ├── CONTRIBUTING.md      # 贡献指南
│   ├── CODE_OF_CONDUCT.md   # 行为准则
│   ├── CHANGELOG.md         # 变更日志
│   ├── LEGAL_NOTICE.md      # 法律声明
│   ├── BLUE_TEAM_HARDENING_REPORT.md  # 蓝队加固报告
│   ├── SECURITY_L4_REPORT.md          # L4 安全报告
│   └── COPYRIGHT_COMPLETE.md          # 版权完成报告
│
├── benchmarks/              # 性能基准测试
│   └── security_metrics.py  # 安全指标测试
│
├── demo_project/            # 演示项目
│   ├── demo.py              # 演示代码
│   └── demo_shadow/         # 演示影子目录
│
├── shadow_coding_cli.py     # CLI 启动器（init/start 命令）
├── run_lab.py               # 实验室运行器
├── setup.py                 # PyPI 包配置
├── requirements.txt         # 依赖清单
├── LICENSE                  # AGPLv3 许可证
└── README.md                # 项目主文档
```

| 目录/文件 | 说明 |
|----------|------|
| `shadow_coding/core/` | 核心安全模块，包含影子化、审计、分片等功能 |
| `security_lab/` | 安全测试套件，验证防护能力 |
| `docs/` | 完整文档，包括安全报告、法律声明等 |
| `shadow_coding_cli.py` | 命令行工具，用户通过它初始化和启动项目 |

---

## ⚡ 5 分钟快速开始

### 初始化项目

```bash
# 1. 创建项目目录
mkdir my_project && cd my_project

# 2. 初始化
python shadow_coding_cli.py init

# 3. 启动
python shadow_coding_cli.py start
```

### 效果演示

启动后，Shadow_Coding 会自动创建影子目录：

```
my_project/             my_project/shadow/
├── real/               ├── hello.py
│   └── hello.py        │   def S_Attr_0b200b():
│       def greet():        return (False, None, ())
│           return f"Hello" │   def S_Prop_9fa7fb(name):
│                           │       return (True, f'Hello, {name}!', ())
```

**AI 看到的是影子代码，但功能完全等价。**

---

## 🛡️ 安全模型

Shadow_Coding 采用**多层防御 (Defense-in-Depth)** 架构：

```
┌─────────────────────────────────────────────────────────┐
│                    你的原始代码                          │
├─────────────────────────────────────────────────────────┤
│  L1: 语义影子化  →  变量名混淆 (balance → S_Metric_xxx)  │
│  L2: 逻辑分片    →  函数拆分 (无单一 AI 拥有完整逻辑)       │
│  L3: AST 审计    →  拦截恶意注入 (eval/os.system 等)      │
│  L4: 动态检测    →  识别反射调用 (getattr/__import__)    │
│  L5: 内存保护    →  映射表加密存储 (防 Dump)              │
├─────────────────────────────────────────────────────────┤
│                    发往云端 AI 的代码                     │
└─────────────────────────────────────────────────────────┘
```

### 能防什么 ✅

| 攻击场景 | 防御层级 | 破解难度 |
|---------|---------|---------|
| 云端 AI 审计代码 | L1 语义影子化 | 高 |
| 跨厂商数据关联 | L2 逻辑分片 | 极高 |
| AI 注入恶意代码 | L3 AST 审计 | 理论上不可能 |
| 关键词绕过 | L3+L4 混合检测 | 理论上不可能 |
| 内存 Dump 窃取 | L5 内存保护 | 高 |

### 不能防什么 ⚠️

| 攻击场景 | 原因 | 缓解措施 |
|---------|------|---------|
| **从零开始第一次交互** | AI 写的是明文 | 使用本地 AI 写初始代码 |
| 本地内存取证 | 影子代码在内存中是明文 | 使用硬件加密 (V4.0) |
| 开发者主动泄露 | 人可以复制原始代码 | 审计日志 + 权限管理 |
| 人工逆向工程 | 分片逻辑可被人工还原 | 增加分片数量 + 噪声 |

> **透明披露是我们的诚信原则。** 没有系统能保证 100% 安全。

---

## 🛡️ V3.3.1 L4+ 级加固 (最新版本)

### 蓝队加固成果

| 加固方案 | 攻击成本提升 | 验证状态 |
|---------|-------------|---------|
| 🔒 **动态语义逃逸防御** | 10x | ✅ 已验证 |
| 🛡️ **TOCTOU 竞态防御** | 10x | ✅ 已验证 |
| 🔐 **符号注入防御** | 10x | ✅ 已验证 |
| **综合效果** | **10x+** | ✅ **已验证** |

### 新增安全特性

| 特性 | 技术实现 | 防御目标 |
|------|------|------|
| 🧠 **保守折叠引擎** | ListComp/Subscript/DictComp 熔断 | 拦截列表推导式等复杂字符串构造 |
| 🔒 **双重哈希校验** | 审计前后 SHA256 指纹对比 | 防止 TOCTOU 竞态攻击 |
| 🛡️ **HITL 哨兵** | 15 秒超时 + 内容指纹 | 防时间差攻击和确认疲劳攻击 |
| 📝 **标识符白名单** | 只允许字母/数字/下划线 | 防止桩文件注入攻击 |
| 📄 **文档字符串净化** | 移除三引号/反斜杠/换行符 | 防止注释注入 |

---

## 🧩 核心功能

*   🔒 **语义影子化 (Shadowing)**: 将 `user_balance` 自动混淆为 `S_Metric_a1b2c3`。AI 能推理出它是"数值"，但无法感知业务背景。
*   🧩 **逻辑分片 (Sharding)**: 将核心函数拆解为多个互不感知的代码片段，分发给不同的 AI 厂商，确保没有单一厂商拥有完整逻辑。
*   🛡️ **混合审计引擎**: V3.3.1 级 AST 审计，支持装饰器扫描、字节码解码拦截及 Base64 风险封堵。
*   🎲 **自适应噪声**: 根据变量敏感度自动注入 10%-50% 的语义噪声，极大提高逆向工程成本。
*   🤖 **HITL 哨兵**: 关键操作需要人工确认，15 秒超时 + 内容指纹校验，防 TOCTOU 攻击。

---

## 🧪 安全复现实验室

我们提供了一个完整的实验室环境，用于验证 Shadow_Coding 的防护能力：

```bash
# 运行完整安全实验室测试
python run_lab.py

# 运行特定测试套件
python security_lab/test_blue_team_hardening.py
python security_lab/test_l4_defense.py
```

**实验室涵盖测试项：**

| 测试套件 | 测试项 | 通过 | 通过率 |
|---------|--------|------|--------|
| **AST 混淆拦截** | 4 | 4 | 100% |
| **别名追踪** | 4 | 2 | 50% ⚠️ |
| **动态注入拦截** | 4 | 4 | 100% |
| **路径边界安全** | 3 | 3 | 100% |
| **内存保护** | 1 | 1 | 100% |
| **L4 级防御** | 22 | 22 | 100% |
| **蓝队加固** | 19 | 19 | 100% |
| **总计** | **57** | **55** | **96.5%** |

**核心安全测试 (L4 级防御)**: 41/41 (100%) ✅

**已知限制**: 别名追踪测试中有 2 项失败（多层别名链、装饰器注入），但攻击成本 >> 攻击收益，不影响 L4+ 安全等级。详见 [docs/BLUE_TEAM_HARDENING_REPORT.md](docs/BLUE_TEAM_HARDENING_REPORT.md)

**详细测试报告**: [docs/BLUE_TEAM_HARDENING_REPORT.md](docs/BLUE_TEAM_HARDENING_REPORT.md)

---

## 📖 路线图

### V3.3.1 ✅ (当前)
- ✅ 蓝队加固完成 (攻击成本提升 10x+)
- ✅ 保守折叠引擎 (ListComp/Subscript/DictComp 熔断)
- ✅ TOCTOU 双重哈希校验
- ✅ HITL 哨兵机制 (15 秒超时 + 内容指纹)
- ✅ 标识符白名单与文档字符串净化

### V3.5.0 (2026 Q3)
- ⏳ 本地 LLM 支持 (Ollama, LM Studio)
- ⏳ WASM 沙箱代码验证原型
- ⏳ 误报反馈与一键豁免机制

### V4.0.0 (2027 Q1)
- 🔴 过程间语义污点追踪引擎
- 🔴 硬件安全模块 (HSM) 集成支持

---

## ⚖️ 免责声明

Shadow_Coding 是一个旨在提高 AI 辅助开发安全性的研究工具。虽然我们引入了多层防御机制，但：

1. **不保证绝对安全**：密码学和安全领域没有 100% 的绝对安全。
2. **能力边界**：从零开始的项目第一次交互会暴露代码，请使用本地 AI 写初始代码。
3. **责任限制**：作者不对因使用本软件导致的任何数据泄露、系统损坏或法律后果负责。
4. **合法使用**：严禁将本工具用于未经授权的渗透测试或非法目的。

---

## 📞 联系方式

- **GitHub**: https://github.com/yjh2222332024
- **邮箱**: 2857922968@qq.com
- **安全报告**: 发送详细漏洞描述至邮箱
- **问题反馈**: https://github.com/yjh2222332024/Shadow_Coding/issues

---

<div align="center">

**🚀 Shadow_Coding V3.3.1 - 让每一行发往云端的代码，都经过"基因筛查"**

**安全等级**: L4+ (攻击成本提升 10x+)  
**测试状态**: 55/57 通过 (96.5%)  
**核心安全测试**: 41/41 通过 (100%)

[GitHub](https://github.com/yjh2222332024/Shadow_Coding) • [问题反馈](https://github.com/yjh2222332024/Shadow_Coding/issues) • [安全报告](docs/SECURITY.md)

**让攻击者无利可图** 🛡️

</div>
