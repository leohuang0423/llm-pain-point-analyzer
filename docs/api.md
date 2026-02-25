# API Reference

## Core Modules

### PermissionAnalyzer
```python
class PermissionAnalyzer:
    def analyze(self, permission_issue: dict) -> PermissionAnalysis:
        """
        Analyze a permission issue and provide solutions.
        
        Args:
            permission_issue: Dictionary containing:
                - api: API endpoint name
                - required_permissions: List of required permissions
                - available_permissions: List of available permissions
                - context: Additional context (optional)
        
        Returns:
            PermissionAnalysis object with:
                - missing_permissions: List of missing permissions
                - suggested_actions: List of suggested actions
                - workarounds: List of possible workarounds
                - success_probability: Estimated success probability (0-1)
        """
    
    def analyze_feishu_doc_permission(self) -> PermissionAnalysis:
        """
        Specialized analysis for Feishu document API permission issues.
        """
    
    def verify_permissions(self, api: str, action: str) -> VerificationResult:
        """
        Verify if current permissions allow the specified API action.
        """
```

### ToolRecommender
```python
class ToolRecommender:
    def recommend(self, task: dict) -> ToolRecommendation:
        """
        Recommend tools for a specific task.
        
        Args:
            task: Dictionary containing:
                - description: Task description
                - complexity: Task complexity (low/medium/high)
                - requirements: List of requirements
                - constraints: List of constraints (optional)
        
        Returns:
            ToolRecommendation object with:
                - top_tools: List of recommended tools
                - success_probability: Estimated success probability (0-1)
                - implementation_guide: Step-by-step implementation guide
                - alternatives: Alternative tools with pros/cons
        """
    
    def for_task(self, task_type: str, complexity: str = "medium") -> ToolRecommendation:
        """
        Get tool recommendations for a specific task type.
        """
    
    def compare_tools(self, tools: List[str], criteria: List[str]) -> ComparisonResult:
        """
        Compare multiple tools based on specified criteria.
        """
```

### ErrorDiagnoser
```python
class ErrorDiagnoser:
    def diagnose(self, error: dict) -> ErrorDiagnosis:
        """
        Diagnose an error and provide solutions.
        
        Args:
            error: Dictionary containing:
                - api_call: The API call that failed
                - error_message: Error message received
                - observed_behavior: Observed behavior (optional)
                - context: Additional context (optional)
        
        Returns:
            ErrorDiagnosis object with:
                - root_cause: Identified root cause
                - correct_usage: Correct API usage
                - step_by_step_fix: Step-by-step fix instructions
                - prevention_tips: Tips to prevent similar errors
        """
    
    def diagnose_feishu_doc_issue(self) -> ErrorDiagnosis:
        """
        Specialized diagnosis for Feishu document API issue.
        """
    
    def pre_check(self, api_call: str) -> PreCheckResult:
        """
        Pre-check an API call for potential issues.
        """
```

### PermissionVerifier
```python
class PermissionVerifier:
    def verify(self, permissions: List[str], required: List[str]) -> VerificationResult:
        """
        Verify if a set of permissions meets requirements.
        """
    
    def suggest_scopes(self, api: str, action: str) -> List[str]:
        """
        Suggest required scopes for an API action.
        """
```

## Data Models

### PermissionAnalysis
```python
@dataclass
class PermissionAnalysis:
    missing_permissions: List[str]
    suggested_actions: List[str]
    workarounds: List[str]
    success_probability: float
    severity: str  # low/medium/high/critical
```

### ToolRecommendation
```python
@dataclass
class ToolRecommendation:
    top_tools: List[str]
    success_probability: float
    implementation_guide: str
    alternatives: List[dict]
    estimated_time: str  # e.g., "1-2 hours"
```

### ErrorDiagnosis
```python
@dataclass
class ErrorDiagnosis:
    root_cause: str
    correct_usage: str
    step_by_step_fix: str
    prevention_tips: List[str]
    confidence: float  # 0-1
```

### VerificationResult
```python
@dataclass
class VerificationResult:
    has_permission: bool
    missing_permissions: List[str]
    suggested_scopes: List[str]
    can_proceed: bool
```

## Command Line Interface

### Installation
```bash
pip install llm-pain-point-analyzer
```

### Basic Commands
```bash
# Analyze permissions
llm-ppa analyze-permissions --api feishu_doc.create

# Get tool recommendations
llm-ppa recommend-tools --task "Create a document with markdown content"

# Diagnose an error
llm-ppa diagnose-error --api-call "feishu_doc.create(content='...')" --error "400 Bad Request"

# Verify permissions
llm-ppa verify-permissions --api feishu_doc --action create
```

### Advanced Options
```bash
# Export results to JSON
llm-ppa analyze-permissions --api feishu_doc.create --output json

# Specify complexity level
llm-ppa recommend-tools --task "web scraping" --complexity high

# Include context
llm-ppa diagnose-error --api-call "feishu_doc.create" --error "400" --context "content_in_title"
```

## Configuration

### Environment Variables
```bash
# Set default API provider
export LLM_PPA_DEFAULT_PROVIDER="feishu"

# Enable debug mode
export LLM_PPA_DEBUG=true

# Set cache directory
export LLM_PPA_CACHE_DIR="/tmp/llm-ppa-cache"
```

### Configuration File
Create `~/.llm-ppa/config.yaml`:
```yaml
defaults:
  provider: feishu
  complexity: medium
  output_format: human

cache:
  enabled: true
  ttl: 3600  # 1 hour

logging:
  level: INFO
  file: /tmp/llm-ppa.log
```

## Error Codes

### Common Error Codes
| Code | Meaning | Solution |
|------|---------|----------|
| PERM-001 | Missing required permission | Request additional scopes |
| TOOL-001 | No suitable tool found | Adjust task requirements |
| API-001 | API design flaw | Use workaround or alternative API |
| CONFIG-001 | Configuration error | Check configuration file |

### Handling Errors
```python
from llm_pain_point_analyzer import ErrorDiagnoser, PermissionAnalyzer

try:
    # Your API call
    result = api_call()
except Exception as e:
    diagnoser = ErrorDiagnoser()
    diagnosis = diagnoser.diagnose({
        "api_call": str(api_call),
        "error_message": str(e)
    })
    
    print(f"Root cause: {diagnosis.root_cause}")
    print(f"Fix: {diagnosis.step_by_step_fix}")
```

## Performance Tips

### Caching
```python
from llm_pain_point_analyzer import ToolRecommender
from functools import lru_cache

@lru_cache(maxsize=100)
def get_tool_recommendation(task_description: str):
    recommender = ToolRecommender()
    return recommender.recommend({"description": task_description})
```

### Batch Operations
```python
from llm_pain_point_analyzer import PermissionAnalyzer

analyzer = PermissionAnalyzer()

# Analyze multiple permission issues at once
issues = [
    {"api": "feishu_doc.create", "required": ["docx:document:create"]},
    {"api": "feishu_doc.write", "required": ["docx:document:write_only"]}
]

results = [analyzer.analyze(issue) for issue in issues]
```

## Best Practices

### 1. Always Pre-Check
```python
from llm_pain_point_analyzer import ErrorDiagnoser

diagnoser = ErrorDiagnoser()
pre_check = diagnoser.pre_check("feishu_doc.create(content='...')")

if not pre_check.can_proceed:
    print(f"Issues found: {pre_check.issues}")
```

### 2. Use Specific Analyzers
```python
# Instead of generic analysis
from llm_pain_point_analyzer import PermissionAnalyzer
analyzer = PermissionAnalyzer()
result = analyzer.analyze_feishu_doc_permission()  # More accurate
```

### 3. Cache Results
```python
import hashlib
from llm_pain_point_analyzer import ToolRecommender

def get_cached_recommendation(task_description: str):
    cache_key = hashlib.md5(task_description.encode()).hexdigest()
    
    if cache_key in recommendation_cache:
        return recommendation_cache[cache_key]
    
    recommender = ToolRecommender()
    result = recommender.recommend({"description": task_description})
    recommendation_cache[cache_key] = result
    return result
```

## Examples

### Complete Example
```python
from llm_pain_point_analyzer import (
    PermissionAnalyzer,
    ToolRecommender,
    ErrorDiagnoser,
    PermissionVerifier
)

# Initialize all components
permission_analyzer = PermissionAnalyzer()
tool_recommender = ToolRecommender()
error_diagnoser = ErrorDiagnoser()
permission_verifier = PermissionVerifier()

# Full workflow
def solve_api_problem(api_call: str, error_message: str = None):
    if error_message:
        # Diagnose the error
        diagnosis = error_diagnoser.diagnose({
            "api_call": api_call,
            "error_message": error_message
        })
        return diagnosis
    
    # Pre-check before making the call
    pre_check = error_diagnoser.pre_check(api_call)
    if not pre_check.can_proceed:
        return pre_check
    
    # Verify permissions
    verification = permission_verifier.verify(api_call)
    if not verification.has_permission:
        analysis = permission_analyzer.analyze({
            "api": api_call,
            "required_permissions": verification.required_permissions
        })
        return analysis
    
    # Get tool recommendations if needed
    task = extract_task_from_api_call(api_call)
    if task:
        recommendation = tool_recommender.recommend(task)
        return recommendation
    
    return {"status": "ready", "message": "API call can proceed"}
```