from typing import List, Optional, Type
from pydantic import BaseModel, Field

try:
    from langchain_core.tools import BaseTool, StructuredTool
except ImportError:
    raise ImportError(
        "LangChain is not installed. Please install it with `pip install langchain-core` "
        "or `pip install llm-pain-point-analyzer[langchain]`"
    )

from llm_pain_point_analyzer.permission_analyzer import PermissionAnalyzer
from llm_pain_point_analyzer.tool_recommender import ToolRecommender
from llm_pain_point_analyzer.error_diagnoser import ErrorDiagnoser

# Input Schemas
class PermissionAnalysisInput(BaseModel):
    api: str = Field(description="The name of the API being called (e.g., 'feishu_doc.create')")
    required_permissions: List[str] = Field(description="List of permissions required by the API")
    available_permissions: List[str] = Field(description="List of permissions the user/bot currently has")

class ToolRecommendationInput(BaseModel):
    description: str = Field(description="A description of the task to be performed")
    complexity: str = Field(default="medium", description="The complexity of the task ('low', 'medium', 'high')")
    requirements: List[str] = Field(default_factory=list, description="Optional list of specific requirements")

class ErrorDiagnosisInput(BaseModel):
    api_call: str = Field(description="The code or command that caused the error")
    error_message: str = Field(description="The error message received")
    observed_behavior: Optional[str] = Field(default=None, description="Optional description of what actually happened")

# Tool Factory
def get_langchain_tools() -> List[BaseTool]:
    """
    Returns a list of LangChain-compatible tools for LLM Pain Point Analysis.
    """
    
    # Initialize analyzers
    perm_analyzer = PermissionAnalyzer()
    tool_recommender = ToolRecommender()
    err_diagnoser = ErrorDiagnoser()

    def analyze_permissions_wrapper(api: str, required_permissions: List[str], available_permissions: List[str]) -> str:
        issue = {
            "api": api,
            "required_permissions": required_permissions,
            "available_permissions": available_permissions
        }
        return str(perm_analyzer.analyze(issue))

    def recommend_tools_wrapper(description: str, complexity: str = "medium", requirements: List[str] = None) -> str:
        task = {
            "description": description,
            "complexity": complexity,
            "requirements": requirements or []
        }
        return str(tool_recommender.recommend(task))

    def diagnose_error_wrapper(api_call: str, error_message: str, observed_behavior: str = None) -> str:
        error = {
            "api_call": api_call,
            "error_message": error_message,
            "observed_behavior": observed_behavior
        }
        return str(err_diagnoser.diagnose(error))

    return [
        StructuredTool.from_function(
            func=analyze_permissions_wrapper,
            name="analyze_permissions",
            description="Analyze permission issues when an API call fails with Access Denied or Forbidden errors.",
            args_schema=PermissionAnalysisInput
        ),
        StructuredTool.from_function(
            func=recommend_tools_wrapper,
            name="recommend_tools",
            description="Recommend the best software libraries or tools for a specific coding task.",
            args_schema=ToolRecommendationInput
        ),
        StructuredTool.from_function(
            func=diagnose_error_wrapper,
            name="diagnose_error",
            description="Diagnose the root cause of an API error or unexpected behavior and get fix suggestions.",
            args_schema=ErrorDiagnosisInput
        )
    ]
