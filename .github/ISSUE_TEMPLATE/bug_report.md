name: 🐛 Bug 报告
description: 报告一个 Bug 帮助我们改进
title: "[Bug]: "
labels: ["bug", "triage"]
body:
  - type: markdown
    attributes:
      value: |
        感谢花时间报告 Bug！请尽可能详细地填写以下信息。

  - type: input
    id: version
    attributes:
      label: Shadow_Coding 版本
      description: 你使用的是哪个版本？
      placeholder: 例如：3.3.1
    validations:
      required: true

  - type: input
    id: python
    attributes:
      label: Python 版本
      description: 你的 Python 版本
      placeholder: 例如：3.11.5
    validations:
      required: true

  - type: input
    id: os
    attributes:
      label: 操作系统
      description: 你的操作系统
      placeholder: 例如：Windows 11 / Ubuntu 22.04 / macOS 13.0
    validations:
      required: true

  - type: textarea
    id: what-happened
    attributes:
      label: 发生了什么？
      description: 描述问题以及你期望发生什么
      placeholder: 请详细描述...
    validations:
      required: true

  - type: textarea
    id: reproduce
    attributes:
      label: 复现步骤
      description: 如何复现这个 Bug
      placeholder: |
        1. 执行 '...'
        2. 然后 '...'
        3. 看到错误 '...'
    validations:
      required: true

  - type: textarea
    id: logs
    attributes:
      label: 相关日志输出
      description: 请复制粘贴相关的日志输出
      render: shell
    validations:
      required: false

  - type: textarea
    id: context
    attributes:
      label: 补充信息
      description: 任何相关的代码片段、截图或上下文
    validations:
      required: false
