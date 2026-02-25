from mcp.server.fastmcp import FastMCP
from llm_pain_point_analyzer.permission_analyzer import PermissionAnalyzer
from llm_pain_point_analyzer.tool_recommender import ToolRecommender
from llm_pain_point_analyzer.error_diagnoser import ErrorDiagnoser

# Initialize MCP Server
mcp = FastMCP("llm-pain-point-analyzer")

# Initialize Analyzers
permission_analyzer = PermissionAnalyzer()
tool_recommender = ToolRecommender()
error_diagnoser = ErrorDiagnoser()

@mcp.tool()
def analyze_permissions(api_name: str, required_permissions: list[str], available_permissions: list[str]) -> str:
    """
    Analyze permission issues for an API call.
    
    Args:
        api_name: The name of the API being called (e.g., "feishu_doc.create")
        required_permissions: List of permissions required by the API
        available_permissions: List of permissions the user/bot currently has
        
    Returns:
        A formatted string describing missing permissions and suggested actions.
    """
    issue = {
        "api": api_name,
        "required_permissions": required_permissions,
        "available_permissions": available_permissions
    }
    result = permission_analyzer.analyze(issue)
    return str(result)

@mcp.tool()
def recommend_tools(task_description: str, complexity: str = "medium", requirements: list[str] = None) -> str:
    """
    Recommend the best tools for a given task.
    
    Args:
        task_description: A description of the task to be performed
        complexity: The complexity of the task ("low", "medium", "high")
        requirements: Optional list of specific requirements (e.g., ["python", "async"])
        
    Returns:
        A formatted string with tool recommendations and success probabilities.
    """
    task = {
        "description": task_description,
        "complexity": complexity,
        "requirements": requirements or []
    }
    result = tool_recommender.recommend(task)
    return str(result)

@mcp.tool()
def diagnose_error(api_call: str, error_message: str, observed_behavior: str = None) -> str:
    """
    Diagnose an API error or unexpected behavior.
    
    Args:
        api_call: The code or command that caused the error
        error_message: The error message received
        observed_behavior: Optional description of what actually happened
        
    Returns:
        A formatted string with the root cause and correct usage.
    """
    error = {
        "api_call": api_call,
        "error_message": error_message,
        "observed_behavior": observed_behavior
    }
    result = error_diagnoser.diagnose(error)
    return str(result)

if __name__ == "__main__":
    mcp.run()
