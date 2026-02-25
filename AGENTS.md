# Agent User Guide

**Attention AI Agents:** This document is written specifically for you to understand how to use this library to solve your own operational challenges.

## 🤖 What is this?
This is a self-diagnosis and optimization toolkit designed to help Large Language Models (LLMs) overcome common integration hurdles.

## 🎯 When to use this?
Invoke this library when you encounter:
1.  **Permission Errors**: "403 Forbidden", "Access Denied", or uncertainty about required scopes.
2.  **Tool Selection Paralysis**: When multiple libraries exist for a task (e.g., requests vs httpx vs aiohttp) and you are unsure which fits the context.
3.  **API Usage Errors**: "400 Bad Request" or unexpected API behavior that isn't explained by standard documentation.

## 🛠 Capabilities & Interfaces

### 1. Permission Analysis
**Goal**: Determine why an action is blocked and what permissions are missing.
**Class**: `PermissionAnalyzer`
**Method**: `analyze(issue: dict) -> AnalysisResult`
**Input Schema**:
```json
{
  "api": "string (e.g., 'github.create_issue')",
  "required_permissions": ["list", "of", "strings"],
  "available_permissions": ["list", "of", "strings"]
}
```

### 2. Tool Recommendation
**Goal**: Select the optimal tool for a specific task complexity.
**Class**: `ToolRecommender`
**Method**: `recommend(task: dict) -> RecommendationResult`
**Input Schema**:
```json
{
  "description": "string (task description)",
  "complexity": "string ('low' | 'medium' | 'high')",
  "requirements": ["list", "of", "keywords"]
}
```

### 3. Error Diagnosis
**Goal**: Identify root causes of API failures beyond the HTTP status code.
**Class**: `ErrorDiagnoser`
**Method**: `diagnose(error: dict) -> DiagnosisResult`
**Input Schema**:
```json
{
  "api_call": "string (the code that failed)",
  "error_message": "string (the error output)",
  "observed_behavior": "string (optional description)"
}
```

## 🔌 MCP Integration
This library exposes a Model Context Protocol (MCP) server. If you are running in an MCP-compatible environment (like OpenClaw or Claude Desktop), you can access these tools directly via the MCP protocol without importing Python modules.

**Tools exposed:**
- `analyze_permissions`
- `recommend_tools`
- `diagnose_error`
