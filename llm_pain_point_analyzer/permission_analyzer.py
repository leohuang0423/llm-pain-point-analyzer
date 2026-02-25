#!/usr/bin/env python3
"""
LLM痛点分析器 - 权限验证模块
解决权限认知偏差问题
"""

import json
import sys
import argparse
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

class PermissionAnalyzer:
    """权限验证和分析器"""
    
    def __init__(self, config_dir: str = None):
        """初始化权限分析器"""
        if config_dir is None:
            config_dir = os.path.join(os.path.dirname(__file__), "../config")
        
        self.config_dir = Path(config_dir)
        self.permissions_db = self.load_permissions_db()
        self.tools_db = self.load_tools_db()
        
    def load_permissions_db(self) -> Dict:
        """加载权限数据库"""
        permissions_file = self.config_dir / "permissions.json"
        if permissions_file.exists():
            with open(permissions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认权限数据库
        return {
            "feishu_doc": {
                "create": ["docx:document:write_only"],
                "read": ["docx:document:read_only"],
                "update_block": ["docx:document:write_only"],
                "delete_block": ["docx:document:write_only"]
            },
            "feishu_drive": {
                "list": ["drive:drive:read_only"],
                "create_folder": ["drive:drive:write_only"],
                "delete": ["drive:drive:write_only"]
            },
            "feishu_wiki": {
                "get": ["wiki:wiki:read_only"],
                "create": ["wiki:wiki:write_only"]
            }
        }
    
    def load_tools_db(self) -> Dict:
        """加载工具数据库"""
        tools_file = self.config_dir / "tools.json"
        if tools_file.exists():
            with open(tools_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认工具数据库
        return {
            "feishu_doc": {
                "description": "飞书文档操作工具",
                "actions": ["create", "read", "write", "append", "list_blocks", "get_block", "update_block", "delete_block"],
                "category": "document",
                "complexity": "medium"
            },
            "feishu_drive": {
                "description": "飞书云存储管理工具",
                "actions": ["list", "info", "create_folder", "move", "delete"],
                "category": "storage",
                "complexity": "low"
            },
            "feishu_wiki": {
                "description": "飞书知识库操作工具",
                "actions": ["spaces", "nodes", "get", "search", "create", "move", "rename"],
                "category": "wiki",
                "complexity": "medium"
            },
            "web_search": {
                "description": "网页搜索工具",
                "actions": ["search"],
                "category": "search",
                "complexity": "low",
                "requires_api_key": True
            },
            "web_fetch": {
                "description": "网页内容提取工具",
                "actions": ["fetch"],
                "category": "content",
                "complexity": "low"
            }
        }
    
    def analyze_permission_requirements(self, tool_name: str, action: str, params: Dict = None) -> Dict:
        """
        分析权限需求
        
        Args:
            tool_name: 工具名称
            action: 操作名称
            params: 操作参数
            
        Returns:
            权限需求分析结果
        """
        result = {
            "tool": tool_name,
            "action": action,
            "permissions_required": [],
            "permissions_available": [],
            "permission_status": "unknown",
            "recommended_scopes": [],
            "error_message": None,
            "suggestions": []
        }
        
        # 检查工具是否存在
        if tool_name not in self.tools_db:
            result["error_message"] = f"工具 '{tool_name}' 不存在于工具数据库中"
            result["suggestions"].append(f"检查工具名称是否正确")
            result["suggestions"].append(f"可用的工具: {list(self.tools_db.keys())}")
            return result
        
        # 检查操作是否支持
        tool_info = self.tools_db[tool_name]
        if action not in tool_info.get("actions", []):
            result["error_message"] = f"工具 '{tool_name}' 不支持操作 '{action}'"
            result["suggestions"].append(f"支持的操作: {tool_info.get('actions', [])}")
            return result
        
        # 获取所需权限
        if tool_name in self.permissions_db and action in self.permissions_db[tool_name]:
            result["permissions_required"] = self.permissions_db[tool_name][action]
        else:
            result["permissions_required"] = ["unknown:unknown:unknown"]
        
        # 模拟获取当前权限（实际应用中应从OpenClaw获取）
        result["permissions_available"] = self.simulate_current_permissions()
        
        # 检查权限状态
        result["permission_status"] = self.check_permission_status(
            result["permissions_required"], 
            result["permissions_available"]
        )
        
        # 生成建议
        result["suggestions"] = self.generate_suggestions(
            tool_name, action, result["permission_status"], result["permissions_required"]
        )
        
        # 推荐权限范围
        result["recommended_scopes"] = result["permissions_required"]
        
        return result
    
    def simulate_current_permissions(self) -> List[str]:
        """模拟当前权限（实际应用中应从OpenClaw获取）"""
        # 这里模拟一些常见权限
        return [
            "docx:document:read_only",
            "drive:drive:read_only",
            "wiki:wiki:read_only"
        ]
    
    def check_permission_status(self, required: List[str], available: List[str]) -> str:
        """检查权限状态"""
        if "unknown:unknown:unknown" in required:
            return "unknown"
        
        for perm in required:
            if perm not in available:
                return "insufficient"
        
        return "sufficient"
    
    def generate_suggestions(self, tool_name: str, action: str, status: str, required_perms: List[str]) -> List[str]:
        """生成建议"""
        suggestions = []
        
        if status == "unknown":
            suggestions.append(f"权限需求未知，建议查看 {tool_name} 的文档")
            suggestions.append(f"尝试调用 {tool_name}.{action} 看具体错误信息")
        
        elif status == "insufficient":
            suggestions.append(f"权限不足，需要以下权限: {', '.join(required_perms)}")
            suggestions.append(f"建议联系管理员添加以下权限范围: {', '.join(required_perms)}")
            
            # 特定工具的建议
            if tool_name == "feishu_doc" and action == "create":
                suggestions.append("注意: feishu_doc.create(content='...') 会将内容写入标题，需要两步操作")
                suggestions.append("第一步: 创建只有标题的文档")
                suggestions.append("第二步: 使用 update_block 添加正文内容")
        
        elif status == "sufficient":
            suggestions.append(f"权限充足，可以执行 {tool_name}.{action}")
        
        return suggestions
    
    def get_tool_recommendation(self, task_description: str, available_tools: List[str] = None) -> Dict:
        """
        根据任务描述推荐工具
        
        Args:
            task_description: 任务描述
            available_tools: 可用工具列表
            
        Returns:
            工具推荐结果
        """
        if available_tools is None:
            available_tools = list(self.tools_db.keys())
        
        # 简单的关键词匹配（实际应用中可以使用更复杂的NLP）
        recommendations = []
        
        # 分析任务类型
        task_lower = task_description.lower()
        
        for tool_name in available_tools:
            if tool_name not in self.tools_db:
                continue
            
            tool_info = self.tools_db[tool_name]
            score = 0
            
            # 基于类别的匹配
            category = tool_info.get("category", "")
            if "文档" in task_description or "doc" in task_lower or "write" in task_lower:
                if category in ["document", "wiki"]:
                    score += 3
            
            if "搜索" in task_description or "search" in task_lower:
                if category == "search":
                    score += 3
            
            if "文件" in task_description or "file" in task_lower or "storage" in task_lower:
                if category == "storage":
                    score += 3
            
            # 基于工具名称的匹配
            if tool_name.lower() in task_lower:
                score += 2
            
            # 基于描述的关键词匹配
            description = tool_info.get("description", "")
            for keyword in task_lower.split():
                if keyword in description.lower():
                    score += 1
            
            if score > 0:
                recommendations.append({
                    "tool": tool_name,
                    "description": tool_info.get("description", ""),
                    "category": category,
                    "complexity": tool_info.get("complexity", "unknown"),
                    "score": score,
                    "actions": tool_info.get("actions", []),
                    "requires_api_key": tool_info.get("requires_api_key", False)
                })
        
        # 按分数排序
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "task": task_description,
            "recommendations": recommendations[:3],  # 返回前3个推荐
            "total_tools_considered": len(available_tools)
        }
    
    def format_analysis_report(self, analysis_result: Dict) -> str:
        """格式化分析报告"""
        report = []
        report.append("=" * 60)
        report.append("LLM痛点分析器 - 权限验证报告")
        report.append("=" * 60)
        report.append(f"工具: {analysis_result.get('tool', 'unknown')}")
        report.append(f"操作: {analysis_result.get('action', 'unknown')}")
        report.append(f"权限状态: {analysis_result.get('permission_status', 'unknown')}")
        report.append("")
        
        # 权限信息
        report.append("权限需求:")
        for perm in analysis_result.get("permissions_required", []):
            report.append(f"  - {perm}")
        
        report.append("")
        report.append("当前可用权限:")
        for perm in analysis_result.get("permissions_available", []):
            report.append(f"  - {perm}")
        
        # 错误信息
        if analysis_result.get("error_message"):
            report.append("")
            report.append("错误信息:")
            report.append(f"  {analysis_result['error_message']}")
        
        # 建议
        if analysis_result.get("suggestions"):
            report.append("")
            report.append("建议:")
            for suggestion in analysis_result.get("suggestions", []):
                report.append(f"  - {suggestion}")
        
        report.append("=" * 60)
        return "\n".join(report)


def main():
    """命令行入口点"""
    parser = argparse.ArgumentParser(description="LLM痛点分析器 - 权限验证模块")
    parser.add_argument("--tool", help="工具名称")
    parser.add_argument("--action", help="操作名称")
    parser.add_argument("--task", help="任务描述（用于工具推荐）")
    parser.add_argument("--config-dir", help="配置文件目录")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="输出格式")
    
    args = parser.parse_args()
    
    analyzer = PermissionAnalyzer(args.config_dir)
    
    if args.task:
        # 工具推荐模式
        recommendation = analyzer.get_tool_recommendation(args.task)
        if args.format == "json":
            print(json.dumps(recommendation, indent=2, ensure_ascii=False))
        else:
            print(f"任务: {recommendation['task']}")
            print(f"考虑的工具数量: {recommendation['total_tools_considered']}")
            print("\n推荐工具:")
            for i, rec in enumerate(recommendation['recommendations'], 1):
                print(f"{i}. {rec['tool']} (分数: {rec['score']})")
                print(f"   描述: {rec['description']}")
                print(f"   类别: {rec['category']}")
                print(f"   复杂度: {rec['complexity']}")
                print(f"   支持的操作: {', '.join(rec['actions'][:3])}")
                if rec.get('requires_api_key'):
                    print(f"   ⚠️ 需要API密钥")
                print()
    
    elif args.tool and args.action:
        # 权限分析模式
        analysis = analyzer.analyze_permission_requirements(args.tool, args.action)
        if args.format == "json":
            print(json.dumps(analysis, indent=2, ensure_ascii=False))
        else:
            print(analyzer.format_analysis_report(analysis))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()