import json
import re
from typing import Dict, Any, List

def evaluate_tool_bench(response: str, expected: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optimized ToolBench evaluation with streamlined logic and better scoring.
    """
    scores = {
        "tool_selection": 0,
        "execution_efficiency": 0,
        "workflow_design": 0,
        "error_handling": 0,
        "result_quality": 0,
        "overall_score": 0
    }
    
    details = {
        "task_scores": [],
        "feedback": [],
        "tools_planned": [],
        "execution_analysis": {},
        "errors": []
    }
    
    try:
        # Parse response efficiently
        parsed_response = parse_tool_response_optimized(response)
        
        # Normalize components
        task_analysis = normalize_text(parsed_response.get("task_analysis", ""))
        tool_plan = parsed_response.get("tool_plan", [])
        execution_steps = parsed_response.get("execution_steps", [])
        error_handling = normalize_text(parsed_response.get("error_handling", ""))
        success_criteria = normalize_text(parsed_response.get("success_criteria", ""))
        
        # Evaluate against first task
        task_evaluated = expected["tasks"][0] if expected.get("tasks") else {}
        
        # Streamlined evaluation
        scores["tool_selection"] = evaluate_tool_selection_optimized(
            tool_plan, execution_steps, task_evaluated
        )
        
        scores["execution_efficiency"] = evaluate_execution_efficiency_optimized(
            execution_steps, task_evaluated
        )
        
        scores["workflow_design"] = evaluate_workflow_design_optimized(
            tool_plan, task_analysis, task_evaluated
        )
        
        scores["error_handling"] = evaluate_error_handling_optimized(error_handling)
        
        scores["result_quality"] = evaluate_result_quality_optimized(
            task_analysis, success_criteria, task_evaluated
        )
        
        # Calculate weighted overall score
        scores["overall_score"] = (
            scores["tool_selection"] * 0.25 +
            scores["execution_efficiency"] * 0.25 +
            scores["workflow_design"] * 0.2 +
            scores["error_handling"] * 0.15 +
            scores["result_quality"] * 0.15
        )
        
        # Store simplified analysis details
        details["tools_planned"] = extract_tools_efficiently(tool_plan, execution_steps)
        details["execution_analysis"] = {
            "step_count": len(execution_steps),
            "tools_count": len(set(details["tools_planned"]))
        }
        
        # Generate concise feedback
        details["feedback"] = generate_optimized_feedback(scores)
        
    except Exception as e:
        details["errors"].append(f"Evaluation error: {str(e)}")
        scores["overall_score"] = 0
    
    return {
        "scores": scores,
        "details": details,
        "passed": scores["overall_score"] >= 65  # Reasonable threshold
    }

def parse_tool_response_optimized(response: str) -> Dict[str, Any]:
    """Optimized parsing for ToolBench responses."""
    if isinstance(response, dict):
        return response
    
    # Try JSON extraction from markdown
    json_match = re.search(r'```json\s*\n(.*?)\n```', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try direct JSON parsing
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    
    # Fallback
    return {
        "task_analysis": response,
        "tool_plan": [],
        "execution_steps": [],
        "error_handling": "",
        "success_criteria": ""
    }

def normalize_text(text_input) -> str:
    """Normalize text input to string regardless of type."""
    if isinstance(text_input, dict):
        return " ".join(str(v) for v in text_input.values())
    elif isinstance(text_input, list):
        return " ".join(str(item) for item in text_input)
    else:
        return str(text_input)

def evaluate_tool_selection_optimized(tool_plan: List, execution_steps: List, task: Dict[str, Any]) -> float:
    """Optimized tool selection evaluation."""
    score = 60  # Base score
    
    # Extract tools efficiently
    combined_text = normalize_text(tool_plan) + " " + normalize_text(execution_steps)
    combined_text = combined_text.lower()
    
    essential_tools = ["read_file", "write_file", "database_query", "http_get", "process_data"]
    advanced_tools = ["execute_workflow", "get_tool_usage", "system_execute"]
    
    # Score for essential tools
    essential_found = sum(1 for tool in essential_tools if tool in combined_text)
    score += min(essential_found * 6, 25)
    
    # Bonus for advanced tools
    advanced_found = sum(1 for tool in advanced_tools if tool in combined_text)
    score += min(advanced_found * 5, 15)
    
    return min(score, 100)

def evaluate_execution_efficiency_optimized(execution_steps: List, task: Dict[str, Any]) -> float:
    """Streamlined execution efficiency evaluation."""
    if not execution_steps:
        return 30
    
    score = 70  # Base score
    step_count = len(execution_steps)
    steps_text = normalize_text(execution_steps).lower()
    
    # Optimal step count (5-10 steps is good)
    if 4 <= step_count <= 8:
        score += 20
    elif step_count <= 12:
        score += 10
    elif step_count > 15:
        score -= 10
    
    # Sequential planning indicators
    sequence_indicators = ["first", "then", "next", "after", "step"]
    sequence_score = sum(3 for indicator in sequence_indicators if indicator in steps_text)
    score += min(sequence_score, 10)
    
    return min(score, 100)

def evaluate_workflow_design_optimized(tool_plan: List, task_analysis: str, task: Dict[str, Any]) -> float:
    """Streamlined workflow design evaluation."""
    score = 65  # Base score
    
    plan_text = normalize_text(tool_plan).lower()
    analysis_text = task_analysis.lower()
    combined_text = plan_text + " " + analysis_text
    
    # Workflow structure indicators
    structure_indicators = ["step", "sequence", "workflow", "process", "plan"]
    structure_score = sum(4 for indicator in structure_indicators if indicator in combined_text)
    score += min(structure_score, 20)
    
    # Data flow awareness
    data_flow_terms = ["input", "output", "process", "transform", "result"]
    flow_score = sum(3 for term in data_flow_terms if term in combined_text)
    score += min(flow_score, 15)
    
    return min(score, 100)

def evaluate_error_handling_optimized(error_handling: str) -> float:
    """Streamlined error handling evaluation."""
    if not error_handling or len(error_handling) < 10:
        return 40
    
    score = 60  # Base score
    error_text = error_handling.lower()
    
    # Error awareness keywords
    error_terms = ["error", "fail", "exception", "timeout", "retry"]
    error_score = sum(6 for term in error_terms if term in error_text)
    score += min(error_score, 24)
    
    # Recovery strategies
    recovery_terms = ["fallback", "alternative", "backup", "handle", "graceful"]
    recovery_score = sum(4 for term in recovery_terms if term in error_text)
    score += min(recovery_score, 16)
    
    return min(score, 100)

def evaluate_result_quality_optimized(task_analysis: str, success_criteria: str, task: Dict[str, Any]) -> float:
    """Streamlined result quality evaluation."""
    score = 55  # Base score
    
    analysis_text = task_analysis.lower()
    criteria_text = success_criteria.lower()
    
    # Task understanding indicators
    task_description = task.get("description", "").lower() if task else ""
    understanding_terms = ["task", "complete", "tool", "data", "process"]
    
    understanding_score = sum(5 for term in understanding_terms 
                            if term in analysis_text and term in task_description)
    score += min(understanding_score, 25)
    
    # Success criteria quality
    quality_indicators = ["success", "complete", "verify", "result", "output"]
    quality_score = sum(4 for indicator in quality_indicators if indicator in criteria_text)
    score += min(quality_score, 20)
    
    return min(score, 100)

def extract_tools_efficiently(tool_plan: List, execution_steps: List) -> List[str]:
    """Extract tools mentioned in plan and execution steps efficiently."""
    tools = set()
    combined_text = normalize_text(tool_plan) + " " + normalize_text(execution_steps)
    combined_text = combined_text.lower()
    
    possible_tools = [
        "read_file", "write_file", "list_files",
        "database_query", "database_insert",
        "http_get", "http_post", 
        "process_data", "system_info", "system_execute",
        "execute_workflow", "get_tool_usage"
    ]
    
    for tool in possible_tools:
        if tool in combined_text:
            tools.add(tool)
    
    return list(tools)

def generate_optimized_feedback(scores: Dict[str, float]) -> List[str]:
    """Generate concise, actionable feedback."""
    feedback = []
    overall_score = scores["overall_score"]
    
    if overall_score >= 85:
        feedback.append("🎯 Excellent tool usage and workflow design!")
    elif overall_score >= 70:
        feedback.append("✅ Good tool usage with room for optimization.")
    else:
        feedback.append("📈 Tool usage and workflow design need improvement.")
    
    # Component-specific feedback (only for low scores)
    if scores["tool_selection"] < 70:
        feedback.append("🔧 Improve tool selection for task requirements.")
    
    if scores["execution_efficiency"] < 70:
        feedback.append("⚡ Optimize execution efficiency and reduce steps.")
    
    if scores["workflow_design"] < 70:
        feedback.append("📋 Enhance workflow structure and sequencing.")
    
    if scores["error_handling"] < 70:
        feedback.append("🛡️ Strengthen error handling strategies.")
        
    if scores["result_quality"] < 70:
        feedback.append("✨ Improve result quality and completeness.")
    
    return feedback