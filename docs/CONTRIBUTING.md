# 贡献指南

感谢你对 Shadow_Coding 感兴趣！我们欢迎各种形式的贡献。

## 🚀 快速开始

### 开发环境设置

```bash
# 1. Fork 项目
git clone https://github.com/your-username/Shadow_Coding.git
cd Shadow_Coding

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装开发依赖
pip install -r requirements.txt
pip install -e ".[dev]"

# 4. 运行测试
python run_lab.py
pytest
```

## 🧩 可以贡献什么

### 代码相关
- 🐛 修复 Bug
- ✨ 新功能实现
- 🚀 性能优化
- 🧪 补充测试用例

### 非代码相关
- 📝 文档改进
- 💬 问题讨论
- 📢 项目推广
- 🐞 提交 Issue

## 📋 提交指南

### 1. 创建分支

```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/issue-123
```

### 2. 提交代码

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```bash
# 新功能
git commit -m "feat: 添加 XXX 功能"

# Bug 修复
git commit -m "fix: 修复 XXX 问题"

# 文档
git commit -m "docs: 更新 README"

# 测试
git commit -m "test: 添加 XXX 测试用例"

# 重构
git commit -m "refactor: 重构 XXX 模块"
```

### 3. 运行测试

```bash
# 确保所有测试通过
python run_lab.py
pytest --cov=shadow_coding
```

### 4. 推送并创建 PR

```bash
git push origin feature/your-feature-name
```

然后在 GitHub 上创建 Pull Request。

## 🔍 PR 审核流程

1. **自动化检查** - CI/CD 会自动运行测试和代码检查
2. **代码审查** - 维护者会审查代码质量
3. **反馈修改** - 根据审查意见进行修改
4. **合并** - 审核通过后合并到主分支

## 📖 代码规范

### Python 风格

遵循 [PEP 8](https://pep8.org/)：

```python
# ✅ 好的命名
def calculate_user_balance():
    pass

# ❌ 避免
def calc():
    pass
```

### 类型注解

鼓励使用类型注解：

```python
def greet(name: str, times: int = 1) -> str:
    return name * times
```

### 文档字符串

公共函数/类需要文档字符串：

```python
def process_data(data: dict) -> list:
    """
    处理输入数据并返回结果列表。
    
    Args:
        data: 包含处理参数的字典
        
    Returns:
        处理后的结果列表
        
    Raises:
        ValueError: 当输入数据无效时
    """
    pass
```

## 🧪 测试指南

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_security.py

# 查看覆盖率
pytest --cov=shadow_coding --cov-report=html
```

### 编写测试

测试文件放在 `tests/` 目录，命名格式 `test_*.py`：

```python
def test_security_audit():
    auditor = SecurityAuditor()
    assert auditor.audit("safe_code()") is None
```

## 💬 沟通渠道

- **GitHub Issues** - Bug 报告和功能请求
- **GitHub Discussions** - 问题讨论
- **Email** - 2857922968@qq.com

## 🏆 贡献者权益

- 在 README 中列出所有贡献者
- 达到一定贡献量可获得 Committer 权限
- 参与项目决策讨论

## ❓ 常见问题

### Q: 我不知道从哪里开始
**A:** 查看标记为 `good first issue` 的 Issue，这些适合新手。

### Q: 我的 PR 多久会被审核
**A:** 通常 1-3 个工作日，如果超过一周可以 @ 维护者。

### Q: 可以同时提交多个 PR 吗
**A:** 可以，但建议每个 PR 专注于一个功能/修复。

---

感谢你的贡献！🎉
