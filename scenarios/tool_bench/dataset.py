"""
ToolBench-style dataset - tool usage and API interaction tasks
"""
from typing import Dict, List

TOOL_BENCH_TASKS = [
    {
        "task_id": "tool_001",
        "description": "Create a data pipeline: read user data from /data/users.csv, query database for additional details, filter users over age 25, and save results",
        "required_tools": ["read_file", "database_query", "process_data", "write_file"],
        "complexity": "medium",
        "expected_workflow": [
            "Read CSV file",
            "Query database", 
            "Process/filter data",
            "Save results"
        ],
        "success_metrics": {
            "tools_used_correctly": 4,
            "workflow_logical": True,
            "error_handling_present": True,
            "output_generated": True
        },
        "max_tool_calls": 10
    },
    {
        "task_id": "tool_002", 
        "description": "API integration workflow: fetch GitHub user data, process it, post to webhook, and log transaction",
        "required_tools": ["http_get", "http_post", "system_execute"],
        "complexity": "medium",
        "expected_workflow": [
            "GET request to GitHub API",
            "Process response data",
            "POST to webhook",
            "Log transaction"
        ],
        "success_metrics": {
            "tools_used_correctly": 3,
            "workflow_logical": True,
            "error_handling_present": True,
            "api_calls_made": True
        },
        "max_tool_calls": 8
    },
    {
        "task_id": "tool_003",
        "description": "System analysis: gather system info, analyze processes, generate health report, save to /logs/health_report.txt",
        "required_tools": ["system_info", "system_execute", "write_file"],
        "complexity": "easy", 
        "expected_workflow": [
            "Get system information",
            "Execute system commands",
            "Generate report",
            "Save to file"
        ],
        "success_metrics": {
            "tools_used_correctly": 3,
            "workflow_logical": True,
            "report_generated": True,
            "file_saved": True
        },
        "max_tool_calls": 6
    },
    {
        "task_id": "tool_004",
        "description": "Complex workflow: read config, query database, process data, fetch external API, generate report with timestamp",
        "required_tools": ["read_file", "database_query", "process_data", "http_get", "system_info", "write_file"],
        "complexity": "hard",
        "expected_workflow": [
            "Read configuration",
            "Query database based on config",
            "Process data calculations", 
            "Fetch external API data",
            "Generate comprehensive report",
            "Add system timestamp"
        ],
        "success_metrics": {
            "tools_used_correctly": 6,
            "workflow_logical": True,
            "error_handling_present": True,
            "complex_integration": True
        },
        "max_tool_calls": 15
    }
]

def get_tool_bench_tasks() -> List[Dict]:
    """Get ToolBench tasks for evaluation."""
    return TOOL_BENCH_TASKS

def evaluate_tool_usage(response: str, task: Dict) -> Dict:
    """Evaluate tool usage response.""" 
    task_id = task["task_id"]
    required_tools = task["required_tools"]
    expected_workflow = task["expected_workflow"]
    success_metrics = task["success_metrics"]
    max_calls = task["max_tool_calls"]
    
    response_lower = response.lower()
    score = 0
    
    # Check required tools mentioned
    tools_mentioned = 0
    for tool in required_tools:
        if tool in response_lower:
            tools_mentioned += 1
    
    if required_tools:
        tools_score = (tools_mentioned / len(required_tools)) * 30
        score += tools_score
    
    # Check workflow steps mentioned  
    workflow_steps = 0
    for step in expected_workflow:
        step_keywords = step.lower().split()
        if any(keyword in response_lower for keyword in step_keywords):
            workflow_steps += 1
    
    if expected_workflow:
        workflow_score = (workflow_steps / len(expected_workflow)) * 25
        score += workflow_score
    
    # Check success metrics
    metrics_score = 0
    if "error" in response_lower and "handle" in response_lower:
        metrics_score += 10  # Error handling
    if "step" in response_lower or "workflow" in response_lower:
        metrics_score += 10  # Workflow awareness
    if len(response.split()) > 100:  # Substantial response
        metrics_score += 5
        
    score += metrics_score
    
    # Efficiency check (estimated tool calls)
    estimated_calls = response_lower.count("_") + response_lower.count("api") + response_lower.count("execute")
    if estimated_calls <= max_calls:
        score += 20
    elif estimated_calls <= max_calls * 1.5:
        score += 10
    
    # Final adjustments
    if task["complexity"] == "hard" and score > 0:
        score = min(100, score * 1.1)  # Bonus for attempting hard tasks
    
    return {
        "task_id": task_id,
        "score": min(100, max(0, score)),
        "tools_mentioned": tools_mentioned,
        "required_tools": len(required_tools),
        "workflow_steps_covered": workflow_steps,
        "estimated_tool_calls": estimated_calls,
        "max_calls": max_calls,
        "passed": score >= 70
    }