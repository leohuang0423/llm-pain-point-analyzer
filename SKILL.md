---
name: llm-pain-point-analyzer
description: 解决大模型作为第一用户的三大核心痛点：权限认知偏差、工具选择困难、操作模式混淆
version: 1.0.0
author: leohuang0423
keywords: llm, agent, permission, tool-recommendation, error-diagnosis, openclaw, mcp
---

# LLM Pain Point Analyzer

## 功能说明

这是一个专为 AI Agent 设计的"自我诊断"工具包，帮助 Agent 解决在与外部世界交互时遇到的核心问题。

### 1. 权限分析器 (Permission Analyzer)
- **解决痛点**："我知道我需要做什么，但不知道我是否有权限"
- **功能**：分析 API 调用所需的权限与当前拥有的权限，提供具体的权限申请建议。

### 2. 工具推荐器 (Tool Recommender)
- **解决痛点**："有太多工具，我不知道该用哪个"
- **功能**：根据任务描述和复杂度，智能推荐最合适的工具或库。

### 3. 错误诊断器 (Error Diagnoser)
- **解决痛点**："我知道怎么操作，但总是出错"
- **功能**：深入分析 API 错误，找出根本原因（如参数依赖、隐藏限制），并提供修正后的代码示例。

## 使用方法

### Python 代码调用

```python
from llm_pain_point_analyzer import PermissionAnalyzer

analyzer = PermissionAnalyzer()
result = analyzer.analyze({
    "api": "feishu_doc.create",
    "required_permissions": ["docx:document:create"],
    "available_permissions": []
})
print(result)
```

### MCP (Model Context Protocol) 调用

本技能内置 MCP Server，支持通过 MCP 协议直接调用：

- `analyze_permissions`: 分析权限问题
- `recommend_tools`: 推荐工具
- `diagnose_error`: 诊断错误

## 安装要求

- Python 3.8+
- mcp (可选，用于 MCP Server 功能)

