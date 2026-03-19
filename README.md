# 🚀 SpineCode (ShadowCLI)

> **“让云端 AI 成为你的逻辑计件工，而非你的业务合规噩梦。”**

### 🌌 项目愿景 (The Why)
在 **Vibe-Coding** 时代，开发者与 AI 的协作深度达到了前所未有的高度。然而，这也带来了前所未有的**隐私黑洞**：当你调用云端 API（如 Claude, GPT）进行代码补全或重构时，你的核心业务逻辑、架构设计、甚至商业秘密都在公网上明文传输。

**SpineCode** 是为此诞生的企业级安全解决方案。它是连接“人类意图”与“云端算力”的**安全加密网关（Sec-AI Gateway）**。

---

### 核心原理：语义影子 (Semantic Shadowing)
SpineCode 并不简单地通过正则替换变量，而是基于 **SpineDoc** 的核心基因（ISR/SCR/HMAC），对代码进行“手术级”的脱敏与重构：

1.  **逻辑分片 (Logic Sharding)**：利用 AST（抽象语法树）将代码拆解为原子化的“逻辑种子”。
2.  **语义影子化 (Shadowing)**：将敏感的变量名、类名、函数名映射为无语义的影子符号（如 `S_f2`）。
3.  **影子协议注入 (Shadow Stub)**：为 AI 构建一个“虚假的上下文”，让它在“楚门的世界”里进行推演。
4.  **本地自愈还原 (Restoration)**：AI 返回代码后，在本地 CLI 环境中瞬间还原真实语义并进行一致性校验。

---

### 🛠️ MVP v0.1 核心组件

*   **`core/analyzer.py`**: 基于 Python AST 的代码脊梁重构引擎（ISR Engine）。
*   **`core/shadow.py`**: 双向映射的语义影子生成器（Shadow Protocol Generator）。
*   **`core/models.py`**: 结构化代码协议定义（SEC-CODE-1.0）。

### 🚀 快速开始

```bash
# 运行演示脚本，观察“分析 -> 影子化 -> AI 模拟 -> 还原”全流程
python spine_code/main.py
```

---

### 🏛️ 架构演进 (Roadmap)

- [x] **v0.1**: 核心 AST 分析器与影子映射引擎。
- [ ] **v0.2**: **Shadow Stub 自动生成**：当 AI 修改 A 函数时，自动生成 B 函数的影子签名，解决“上下文丢失”。
- [ ] **v0.3**: **HMAC 多智能体协作**：支持将代码碎片分布式分发给多个云端模型（如 BT 种子般的去中心化）。
- [ ] **v1.0**: **Sec-AI OS**：作为本地 Proxy 拦截所有 IDE 的云端流量，实现零侵入的安全防护。
