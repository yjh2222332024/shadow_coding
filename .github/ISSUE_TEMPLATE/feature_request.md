name: ✨ 功能请求
description: 提出一个新功能或改进建议
title: "[Feature]: "
labels: ["enhancement", "triage"]
body:
  - type: markdown
    attributes:
      value: |
        感谢花时间提出新功能建议！请尽可能详细地描述你的想法。

  - type: textarea
    id: problem
    attributes:
      label: 相关的问题
      description: 这个功能解决了什么问题？
      placeholder: 例如：我在使用 Shadow_Coding 时遇到了 XXX 问题...
    validations:
      required: true

  - type: textarea
    id: solution
    attributes:
      label: 建议的解决方案
      description: 你希望如何实现这个功能？
      placeholder: 例如：希望能添加 XXX 功能，可以...
    validations:
      required: true

  - type: textarea
    id: alternatives
    attributes:
      label: 其他方案
      description: 有没有其他替代方案？
    validations:
      required: false

  - type: textarea
    id: context
    attributes:
      label: 补充信息
      description: 任何相关的上下文、截图或使用场景
    validations:
      required: false

  - type: checkboxes
    id: contribution
    attributes:
      label: 贡献意愿
      description: 你是否愿意帮助实现这个功能？
      options:
        - label: 我愿意提交 PR 来实现这个功能
          required: false
