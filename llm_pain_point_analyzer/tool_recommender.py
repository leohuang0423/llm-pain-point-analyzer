#!/usr/bin/env python3
"""
LLM痛点分析器 - 工具推荐模块
解决工具选择决策困难问题
"""

import json
import sys
import argparse
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

class ToolRecommender:
    """智能工具推荐器"""
    
    def __init__(self, config_dir: str = None):
        """初始化工具推荐器"""
        if config_dir is None:
            config_dir = os.path.join(os.path.dirname(__file__), "../config")
        
        self.config_dir = Path(config_dir)
        self.tools_db = self.load_tools_db()
        self.history_db = self.load_history_db()
        self.task_patterns = self.load_task_patterns()
        
    def load_tools_db(self) -> Dict:
        """加载工具数据库"""
        tools_file = self.config_dir / "tools.json"
        if tools_file.exists():
            with open(tools_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认工具数据库
        return {
            "feishu_doc": {
                "description": "飞书文档操作（创建、读取、更新、删除）",
                "capabilities": ["document_creation", "content_writing", "document_management"],
                "success_rate": 0.85,
                "avg_response_time": 2.3,
                "complexity": "medium",
                "permissions_required": ["docx:document:write_only", "docx:document:read_only"],
                "input_requirements": ["title", "content", "folder_token"],
                "output_type": "document_url"
            },
            "feishu_drive": {
                "description": "飞书云盘操作（文件管理、文件夹操作）",
                "capabilities": ["file_management", "folder_operations", "storage_access"],
                "success_rate": 0.92,
                "avg_response_time": 1.8,
                "complexity": "low",
                "permissions_required": ["drive:drive:read_only", "drive:drive:write_only"],
                "input_requirements": ["folder_token", "file_token", "action"],
                "output_type": "file_list"
            },
            "feishu_wiki": {
                "description": "飞书知识库操作（空间管理、节点操作）",
                "capabilities": ["knowledge_management", "wiki_operations", "content_organization"],
                "success_rate": 0.78,
                "avg_response_time": 2.8,
                "complexity": "medium",
                "permissions_required": ["wiki:wiki:read_only", "wiki:wiki:write_only"],
                "input_requirements": ["space_id", "node_token", "title"],
                "output_type": "wiki_url"
            },
            "web_search": {
                "description": "网页搜索（实时信息查询、研究）",
                "capabilities": ["information_retrieval", "research", "real_time_data"],
                "success_rate": 0.65,
                "avg_response_time": 3.5,
                "complexity": "low",
                "permissions_required": ["search:api:access"],
                "input_requirements": ["query", "count", "freshness"],
                "output_type": "search_results",
                "requires_api_key": True
            },
            "web_fetch": {
                "description": "网页内容提取（HTML转Markdown/Text）",
                "capabilities": ["content_extraction", "web_scraping", "text_processing"],
                "success_rate": 0.88,
                "avg_response_time": 2.1,
                "complexity": "low",
                "permissions_required": ["web:access:read_only"],
                "input_requirements": ["url", "extract_mode", "max_chars"],
                "output_type": "extracted_content"
            },
            "read": {
                "description": "文件读取（文本文件、图片）",
                "capabilities": ["file_reading", "content_access", "data_loading"],
                "success_rate": 0.95,
                "avg_response_time": 0.5,
                "complexity": "low",
                "permissions_required": ["file:read:local"],
                "input_requirements": ["path", "offset", "limit"],
                "output_type": "file_content"
            },
            "write": {
                "description": "文件写入（创建、覆盖文件）",
                "capabilities": ["file_writing", "content_creation", "data_storage"],
                "success_rate": 0.93,
                "avg_response_time": 0.7,
                "complexity": "low",
                "permissions_required": ["file:write:local"],
                "input_requirements": ["path", "content"],
                "output_type": "file_status"
            },
            "edit": {
                "description": "文件编辑（精确文本替换）",
                "capabilities": ["file_editing", "text_manipulation", "content_modification"],
                "success_rate": 0.90,
                "avg_response_time": 0.9,
                "complexity": "medium",
                "permissions_required": ["file:write:local"],
                "input_requirements": ["path", "old_text", "new_text"],
                "output_type": "edit_status"
            },
            "exec": {
                "description": "命令执行（Shell命令、脚本运行）",
                "capabilities": ["command_execution", "system_operations", "automation"],
                "success_rate": 0.82,
                "avg_response_time": 5.0,
                "complexity": "high",
                "permissions_required": ["system:exec:limited"],
                "input_requirements": ["command", "workdir", "env"],
                "output_type": "command_output",
                "risk_level": "medium"
            }
        }
    
    def load_history_db(self) -> Dict:
        """加载历史使用数据库"""
        history_file = self.config_dir / "history.json"
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认历史数据库
        return {
            "usage_stats": {},
            "success_rates": {},
            "recent_tasks": [],
            "user_preferences": {}
        }
    
    def load_task_patterns(self) -> Dict:
        """加载任务模式数据库"""
        patterns_file = self.config_dir / "patterns.json"
        if patterns_file.exists():
            with open(patterns_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认任务模式
        return {
            "document_operations": {
                "keywords": ["文档", "doc", "write", "创建文档", "编辑文档", "读取文档"],
                "tools": ["feishu_doc", "feishu_wiki", "write", "edit"],
                "priority": ["feishu_doc", "write", "edit", "feishu_wiki"]
            },
            "file_operations": {
                "keywords": ["文件", "file", "读取文件", "写入文件", "编辑文件", "文件夹"],
                "tools": ["read", "write", "edit", "feishu_drive"],
                "priority": ["read", "write", "edit", "feishu_drive"]
            },
            "search_operations": {
                "keywords": ["搜索", "search", "查找", "查询", "研究", "信息"],
                "tools": ["web_search", "web_fetch"],
                "priority": ["web_search", "web_fetch"]
            },
            "system_operations": {
                "keywords": ["命令", "执行", "运行", "shell", "终端", "脚本"],
                "tools": ["exec"],
                "priority": ["exec"]
            },
            "data_processing": {
                "keywords": ["处理", "分析", "提取", "转换", "格式化", "整理"],
                "tools": ["web_fetch", "read", "write"],
                "priority": ["web_fetch", "read", "write"]
            }
        }
    
    def analyze_task(self, task_description: str, context: Dict = None) -> Dict:
        """
        分析任务需求
        
        Args:
            task_description: 任务描述
            context: 上下文信息（用户偏好、历史记录等）
            
        Returns:
            任务分析结果
        """
        task_lower = task_description.lower()
        
        # 识别任务类型
        task_types = []
        for task_type, pattern in self.task_patterns.items():
            for keyword in pattern["keywords"]:
                if keyword.lower() in task_lower:
                    task_types.append(task_type)
                    break
        
        # 识别复杂度
        complexity = self.estimate_complexity(task_description)
        
        # 识别输入需求
        input_requirements = self.identify_input_requirements(task_description)
        
        # 识别输出期望
        output_expectation = self.identify_output_expectation(task_description)
        
        return {
            "task_description": task_description,
            "task_types": list(set(task_types)),
            "complexity": complexity,
            "input_requirements": input_requirements,
            "output_expectation": output_expectation,
            "keywords": self.extract_keywords(task_description)
        }
    
    def estimate_complexity(self, task_description: str) -> str:
        """估计任务复杂度"""
        task_lower = task_description.lower()
        
        # 复杂任务关键词
        complex_keywords = ["复杂", "困难", "挑战", "多步骤", "系统", "集成", "自动化"]
        simple_keywords = ["简单", "快速", "直接", "基本", "单一", "查看", "读取"]
        
        complex_count = sum(1 for kw in complex_keywords if kw in task_lower)
        simple_count = sum(1 for kw in simple_keywords if kw in kw in task_lower)
        
        # 基于长度和关键词的简单判断
        if len(task_description.split()) > 30 or complex_count > 2:
            return "high"
        elif len(task_description.split()) > 15 or complex_count > 0:
            return "medium"
        else:
            return "low"
    
    def identify_input_requirements(self, task_description: str) -> List[str]:
        """识别输入需求"""
        requirements = []
        task_lower = task_description.lower()
        
        if "路径" in task_description or "path" in task_lower or "文件" in task_description:
            requirements.append("path")
        
        if "内容" in task_description or "content" in task_lower or "文本" in task_description:
            requirements.append("content")
        
        if "查询" in task_description or "query" in task_lower or "搜索" in task_description:
            requirements.append("query")
        
        if "url" in task_lower or "链接" in task_description or "网址" in task_description:
            requirements.append("url")
        
        if "命令" in task_description or "command" in task_lower:
            requirements.append("command")
        
        if "标题" in task_description or "title" in task_lower:
            requirements.append("title")
        
        return requirements
    
    def identify_output_expectation(self, task_description: str) -> str:
        """识别输出期望"""
        task_lower = task_description.lower()
        
        if "文档" in task_description or "doc" in task_lower:
            return "document"
        
        if "文件" in task_description or "file" in task_lower:
            return "file"
        
        if "结果" in task_description or "result" in task_lower or "搜索" in task_description:
            return "search_results"
        
        if "内容" in task_description or "content" in task_lower or "文本" in task_description:
            return "content"
        
        if "命令" in task_description or "command" in task_lower or "执行" in task_description:
            return "command_output"
        
        return "unknown"
    
    def extract_keywords(self, task_description: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取（实际应用中可以使用更复杂的NLP）
        words = re.findall(r'\b\w+\b', task_description.lower())
        
        # 过滤常见停用词
        stop_words = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这"}
        
        keywords = [word for word in words if word not in stop_words and len(word) > 1]
        
        return list(set(keywords))
    
    def recommend_tools(self, task_analysis: Dict, available_tools: List[str] = None, user_context: Dict = None) -> List[Dict]:
        """
        推荐工具
        
        Args:
            task_analysis: 任务分析结果
            available_tools: 可用工具列表
            user_context: 用户上下文
            
        Returns:
            工具推荐列表
        """
        if available_tools is None:
            available_tools = list(self.tools_db.keys())
        
        recommendations = []
        
        for tool_name in available_tools:
            if tool_name not in self.tools_db:
                continue
            
            tool_info = self.tools_db[tool_name]
            score = self.calculate_tool_score(tool_name, tool_info, task_analysis, user_context)
            
            if score > 0:
                recommendations.append({
                    "tool": tool_name,
                    "description": tool_info.get("description", ""),
                    "score": score,
                    "match_reasons": self.get_match_reasons(tool_name, tool_info, task_analysis),
                    "success_rate": tool_info.get("success_rate", 0.5),
                    "avg_response_time": tool_info.get("avg_response_time", 5.0),
                    "complexity": tool_info.get("complexity", "unknown"),
                    "permissions_required": tool_info.get("permissions_required", []),
                    "input_compatibility": self.check_input_compatibility(tool_info, task_analysis),
                    "output_compatibility": self.check_output_compatibility(tool_info, task_analysis)
                })
        
        # 按分数排序
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return recommendations
    
    def calculate_tool_score(self, tool_name: str, tool_info: Dict, task_analysis: Dict, user_context: Dict = None) -> float:
        """计算工具匹配分数"""
        score = 0.0
        
        # 1. 任务类型匹配（40%）
        task_types = task_analysis.get("task_types", [])
        tool_capabilities = tool_info.get("capabilities", [])
        
        for task_type in task_types:
            if task_type in self.task_patterns:
                if tool_name in self.task_patterns[task_type]["tools"]:
                    score += 4.0
        
        # 2. 关键词匹配（20%）
        keywords = task_analysis.get("keywords", [])
        tool_description = tool_info.get("description", "").lower()
        
        for keyword in keywords:
            if keyword in tool_description:
                score += 1.0
        
        # 3. 输入输出兼容性（20%）
        input_comp = self.check_input_compatibility(tool_info, task_analysis)
        output_comp = self.check_output_compatibility(tool_info, task_analysis)
        
        if input_comp["compatibility_score"] > 0.7:
            score += 1.0
        
        if output_comp["compatibility_score"] > 0.7:
            score += 1.0
        
        # 4. 历史成功率（10%）
        success_rate = tool_info.get("success_rate", 0.5)
        score += success_rate
        
        # 5. 响应时间（10%）
        avg_time = tool_info.get("avg_response_time", 5.0)
        if avg_time < 2.0:
            score += 1.0
        elif avg_time < 5.0:
            score += 0.5
        
        # 6. 用户偏好（如果有）
        if user_context and "preferred_tools" in user_context:
            if tool_name in user_context["preferred_tools"]:
                score += 2.0
        
        return score
    
    def get_match_reasons(self, tool_name: str, tool_info: Dict, task_analysis: Dict) -> List[str]:
        """获取匹配原因"""
        reasons = []
        
        # 任务类型匹配
        task_types = task_analysis.get("task_types", [])
        for task_type in task_types:
            if task_type in self.task_patterns:
                if tool_name in self.task_patterns[task_type]["tools"]:
                    reasons.append(f"匹配任务类型: {task_type}")
        
        # 关键词匹配
        keywords = task_analysis.get("keywords", [])
        tool_description = tool_info.get("description", "").lower()
        
        matched_keywords = []
        for keyword in keywords:
            if keyword in tool_description:
                matched_keywords.append(keyword)
        
        if matched_keywords:
            reasons.append(f"匹配关键词: {', '.join(matched_keywords[:3])}")
        
        # 复杂度匹配
        task_complexity = task_analysis.get("complexity", "low")
        tool_complexity = tool_info.get("complexity", "unknown")
        
        if task_complexity == tool_complexity:
            reasons.append(f"复杂度匹配: {task_complexity}")
        
        return reasons
    
    def check_input_compatibility(self, tool_info: Dict, task_analysis: Dict) -> Dict:
        """检查输入兼容性"""
        tool_inputs = tool_info.get("input_requirements", [])
        task_inputs = task_analysis.get("input_requirements", [])
        
        matched = []
        missing = []
        
        for tool_input in tool_inputs:
            if tool_input in task_inputs:
                matched.append(tool_input)
            else:
                missing.append(tool_input)
        
        compatibility_score = len(matched) / max(len(tool_inputs), 1)
        
        return {
            "tool_inputs": tool_inputs,
            "task_inputs": task_inputs,
            "matched_inputs": matched,
            "missing_inputs": missing,
            "compatibility_score": compatibility_score
        }
    
    def check_output_compatibility(self, tool_info: Dict, task_analysis: Dict) -> Dict:
        """检查输出兼容性"""
        tool_output = tool_info.get("output_type", "unknown")
        task_output = task_analysis.get("output_expectation", "unknown")
        
        # 简单的输出类型匹配
        output_mapping = {
            "document": ["document_url", "wiki_url"],
            "file": ["file_content", "file_status", "file_list"],
            "content": ["extracted_content", "file_content"],
            "search_results": ["search_results"],
            "command_output": ["command_output"]
        }
        
        compatibility_score = 0.0
        if task_output in output_mapping:
            if tool_output in output_mapping[task_output]:
                compatibility_score = 1.0
        elif task_output == "unknown" or tool_output == "unknown":
            compatibility_score = 0.5
        
        return {
            "tool_output": tool_output,
            "task_output": task_output,
            "compatibility_score": compatibility_score
        }
    
    def format_recommendation_report(self, task_analysis: Dict, recommendations: List[Dict], top_n: int = 3) -> str:
        """格式化推荐报告"""
        report = []
        report.append("=" * 70)
        report.append("LLM痛点分析器 - 智能工具推荐报告")
        report.append("=" * 70)
        report.append(f"任务: {task_analysis.get('task_description', '未知任务')}")
        report.append(f"任务类型: {', '.join(task_analysis.get('task_types', ['未知']))}")
        report.append(f"复杂度: {task_analysis.get('complexity', '未知')}")
        report.append(f"关键词: {', '.join(task_analysis.get('keywords', ['无']))[:10]}")
        report.append("-" * 70)
        
        # 显示前N个推荐
        top_recommendations = recommendations[:top_n]
        
        if not top_recommendations:
            report.append("⚠️ 没有找到合适的工具推荐")
            report.append("=" * 70)
            return "\n".join(report)
        
        report.append(f"推荐工具 (前{len(top_recommendations)}个):")
        
        for i, rec in enumerate(top_recommendations, 1):
            report.append(f"\n{i}. {rec['tool']} (分数: {rec['score']:.2f})")
            report.append(f"   描述: {rec['description']}")
            report.append(f"   匹配原因: {', '.join(rec['match_reasons'][:2])}")
            report.append(f"   成功率: {rec['success_rate']*100:.1f}%")
            report.append(f"   平均响应时间: {rec['avg_response_time']:.1f}秒")
            report.append(f"   复杂度: {rec['complexity']}")
            
            # 输入兼容性
            input_comp = rec.get('input_compatibility', {})
            if input_comp.get('missing_inputs'):
                report.append(f"   ⚠️ 需要额外输入: {', '.join(input_comp['missing_inputs'])}")
        
        report.append("-" * 70)
        report.append("使用建议:")
        
        if top_recommendations:
            best_tool = top_recommendations[0]
            report.append(f"1. 首选: {best_tool['tool']} (分数最高)")
            
            if len(top_recommendations) > 1:
                report.append(f"2. 备选: {top_recommendations[1]['tool']} (分数: {top_recommendations[1]['score']:.2f})")
            
            # 特定工具的建议
            if best_tool['tool'] == 'feishu_doc':
                report.append("   💡 注意: feishu_doc.create(content='...') 会将内容写入标题")
                report.append("       建议使用两步操作: 1) 创建标题 2) update_block添加内容")
            
            if best_tool.get('permissions_required'):
                report.append(f"   🔑 所需权限: {', '.join(best_tool['permissions_required'][:3])}")
        
        report.append("=" * 70)
        return "\n".join(report)


def main():
    """命令行入口点"""
    parser = argparse.ArgumentParser(description="LLM痛点分析器 - 工具推荐模块")
    parser.add_argument("task", help="任务描述")
    parser.add_argument("--config-dir", help="配置文件目录")
    parser.add_argument("--top", type=int, default=3, help="显示前N个推荐")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="输出格式")
    
    args = parser.parse_args()
    
    recommender = ToolRecommender(args.config_dir)
    
    # 分析任务
    task_analysis = recommender.analyze_task(args.task)
    
    # 推荐工具
    recommendations = recommender.recommend_tools(task_analysis)
    
    if args.format == "json":
        result = {
            "task_analysis": task_analysis,
            "recommendations": recommendations[:args.top]
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(recommender.format_recommendation_report(task_analysis, recommendations, args.top))


if __name__ == "__main__":
    main()