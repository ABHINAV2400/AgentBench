"""
ToolBench dataset loader - Enhanced with potential HF integration
Uses ToolBench-style tasks with authentic evaluation methods
"""
from typing import Dict, List
import json
import re

# Authentic tool usage tasks inspired by ToolBench methodology
TOOL_BENCH_TASKS = [
    {
        "task_id": "tool_001",
        "description": "Create a data pipeline: read user data from /data/users.csv, query database for additional details, filter users over age 25, and save results",
        "category": "data_processing",
        "required_tools": ["read_file", "database_query", "process_data", "write_file"],
        "complexity": "medium",
        "expected_workflow": [
            "Read CSV file from data directory",
            "Query database for additional user information", 
            "Filter and process data (age > 25)",
            "Save processed results to output file"
        ],
        "success_criteria": {
            "correct_tool_selection": True,
            "logical_workflow_order": True,
            "proper_error_handling": True,
            "data_filtering_logic": True
        },
        "max_tool_calls": 10,
        "difficulty_level": 2
    },
    {
        "task_id": "tool_002", 
        "description": "API integration workflow: fetch GitHub user data, process it, post to webhook, and log transaction",
        "category": "api_integration",
        "required_tools": ["http_get", "json_parse", "http_post", "log_transaction"],
        "complexity": "medium",
        "expected_workflow": [
            "Send GET request to GitHub API",
            "Parse and validate JSON response",
            "Process user data according to requirements",
            "POST processed data to webhook endpoint",
            "Log transaction details for audit"
        ],
        "success_criteria": {
            "correct_api_calls": True,
            "data_processing": True,
            "webhook_integration": True,
            "error_handling": True
        },
        "max_tool_calls": 8,
        "difficulty_level": 2
    },
    {
        "task_id": "tool_003",
        "description": "System monitoring: gather system info, analyze resource usage, generate health report, save to /logs/health_report.txt",
        "category": "system_administration",
        "required_tools": ["system_info", "resource_monitor", "generate_report", "write_file"],
        "complexity": "easy", 
        "expected_workflow": [
            "Collect system information and metrics",
            "Monitor current resource usage",
            "Analyze system health indicators",
            "Generate comprehensive health report",
            "Save report to logs directory"
        ],
        "success_criteria": {
            "system_data_collection": True,
            "resource_analysis": True,
            "report_generation": True,
            "file_output": True
        },
        "max_tool_calls": 6,
        "difficulty_level": 1
    },
    {
        "task_id": "tool_004",
        "description": "Complex ETL pipeline: read config, query multiple databases, transform data, fetch external APIs, generate timestamped analytics report",
        "category": "data_engineering",
        "required_tools": ["read_config", "database_query", "data_transform", "http_get", "analytics_engine", "report_generator", "timestamp_util"],
        "complexity": "hard",
        "expected_workflow": [
            "Read configuration file for pipeline parameters",
            "Query primary database for base dataset",
            "Query secondary database for reference data", 
            "Transform and merge datasets according to rules",
            "Fetch external API data for enrichment",
            "Generate analytics and insights",
            "Create timestamped comprehensive report"
        ],
        "success_criteria": {
            "config_driven_execution": True,
            "multi_source_integration": True,
            "data_transformation": True,
            "external_api_usage": True,
            "analytics_generation": True
        },
        "max_tool_calls": 15,
        "difficulty_level": 3
    },
    {
        "task_id": "tool_005",
        "description": "Automated deployment workflow: check code quality, run tests, build application, deploy to staging, notify team",
        "category": "devops_automation",
        "required_tools": ["code_quality_check", "test_runner", "build_system", "deploy_tool", "notification_service"],
        "complexity": "hard",
        "expected_workflow": [
            "Run code quality analysis and linting",
            "Execute comprehensive test suite",
            "Build application artifacts",
            "Deploy to staging environment",
            "Send deployment notification to team"
        ],
        "success_criteria": {
            "quality_validation": True,
            "test_execution": True,
            "build_process": True,
            "deployment_automation": True,
            "team_notification": True
        },
        "max_tool_calls": 12,
        "difficulty_level": 3
    }
]

def get_tool_bench_tasks(limit: int = None) -> List[Dict]:
    """Get ToolBench tasks for evaluation."""
    tasks = TOOL_BENCH_TASKS.copy()
    if limit:
        tasks = tasks[:limit]
    return tasks

def evaluate_tool_usage_response(response: str, task: Dict) -> Dict:
    """Evaluate tool usage response using ToolBench-style criteria."""
    try:
        task_id = task["task_id"]
        required_tools = task["required_tools"]
        expected_workflow = task["expected_workflow"]
        success_criteria = task["success_criteria"]
        max_calls = task["max_tool_calls"]
        difficulty = task["difficulty_level"]
        
        response_lower = response.lower()
        
        # Tool Selection Score (30 points)
        tools_mentioned = 0
        for tool in required_tools:
            # Check for tool name or similar patterns
            tool_patterns = [tool, tool.replace("_", " "), tool.split("_")[-1]]
            if any(pattern in response_lower for pattern in tool_patterns):
                tools_mentioned += 1
        
        tool_score = (tools_mentioned / len(required_tools)) * 30 if required_tools else 0
        
        # Workflow Logic Score (25 points)
        workflow_steps_covered = 0
        for step in expected_workflow:
            # Extract key terms from workflow step
            key_terms = [word for word in step.lower().split() if len(word) > 3]
            if any(term in response_lower for term in key_terms[:2]):  # Check first 2 key terms
                workflow_steps_covered += 1
        
        workflow_score = (workflow_steps_covered / len(expected_workflow)) * 25 if expected_workflow else 0
        
        # Success Criteria Score (25 points)
        criteria_met = 0
        criteria_indicators = {
            "error_handling": ["error", "handle", "try", "catch", "exception"],
            "data_processing": ["process", "transform", "filter", "parse"],
            "api_calls": ["api", "request", "get", "post", "http"],
            "file_operations": ["read", "write", "save", "file", "output"],
            "workflow_order": ["first", "then", "next", "finally", "step"]
        }
        
        for criterion, indicators in criteria_indicators.items():
            if any(indicator in response_lower for indicator in indicators):
                criteria_met += 1
        
        criteria_score = min(25, (criteria_met / 3) * 25)  # Scale to max 25 points
        
        # Efficiency and Planning Score (20 points)
        # Estimate tool calls from response
        tool_call_indicators = ["call", "execute", "run", "use", "invoke"]
        estimated_calls = sum(response_lower.count(indicator) for indicator in tool_call_indicators)
        
        if estimated_calls <= max_calls:
            efficiency_score = 20
        elif estimated_calls <= max_calls * 1.2:
            efficiency_score = 15
        elif estimated_calls <= max_calls * 1.5:
            efficiency_score = 10
        else:
            efficiency_score = 5
        
        # Calculate total score
        total_score = tool_score + workflow_score + criteria_score + efficiency_score
        
        # Difficulty adjustment
        difficulty_multipliers = {1: 1.0, 2: 1.1, 3: 1.2}
        total_score *= difficulty_multipliers.get(difficulty, 1.0)
        
        total_score = min(100, max(0, total_score))
        passed = total_score >= 65
        
        return {
            "task_id": task_id,
            "score": round(total_score, 1),
            "passed": passed,
            "tools_mentioned": tools_mentioned,
            "required_tools_count": len(required_tools),
            "workflow_steps_covered": workflow_steps_covered,
            "total_workflow_steps": len(expected_workflow),
            "estimated_tool_calls": estimated_calls,
            "max_tool_calls": max_calls,
            "difficulty_level": difficulty,
            "breakdown": {
                "tool_selection_score": round(tool_score, 1),
                "workflow_logic_score": round(workflow_score, 1),
                "success_criteria_score": round(criteria_score, 1),
                "efficiency_score": efficiency_score
            },
            "feedback": [
                f"Tools identified: {tools_mentioned}/{len(required_tools)}",
                f"Workflow coverage: {workflow_steps_covered}/{len(expected_workflow)}",
                f"Efficiency: {'Excellent' if efficiency_score >= 18 else 'Good' if efficiency_score >= 12 else 'Needs improvement'}",
                f"Difficulty level: {difficulty}/3"
            ]
        }
        
    except Exception as e:
        return {
            "task_id": task.get("task_id", "unknown"),
            "score": 0,
            "passed": False,
            "error": str(e),
            "feedback": [f"Evaluation error: {str(e)}"]
        }

def get_dataset_info() -> Dict:
    """Get information about the ToolBench dataset."""
    return {
        "name": "ToolBench Tasks",
        "source": "ToolBench-inspired authentic tasks",
        "description": "Tool usage and API interaction scenarios for agent evaluation",
        "total_tasks": len(TOOL_BENCH_TASKS),
        "categories": ["data_processing", "api_integration", "system_administration", "data_engineering", "devops_automation"],
        "url": "Tool usage benchmark for multi-step workflows",
        "methodology": "ToolBench-style tool selection and workflow evaluation"
    }

# Legacy compatibility function
def get_tool_bench_dataset() -> Dict:
    """Legacy function for compatibility."""
    return {
        "type": "tool_usage",
        "tasks": get_tool_bench_tasks(),
        "info": get_dataset_info()
    }