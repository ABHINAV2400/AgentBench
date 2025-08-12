import json
import re
from typing import Dict, Any, List

def evaluate_tool_bench(response: str, expected: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate ToolBench-style tool usage and API interaction.
    """
    scores = {
        "tool_selection": 0,
        "execution_efficiency": 0,
        "workflow_design": 0,
        "error_handling": 0,
        "result_quality": 0,
        "resource_optimization": 0,
        "overall_score": 0
    }
    
    details = {
        "task_scores": [],
        "feedback": [],
        "tools_planned": [],
        "execution_analysis": {},
        "workflow_evaluation": {},
        "errors": []
    }
    
    try:
        # Parse response
        if isinstance(response, str):
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                parsed_response = json.loads(json_match.group())
            else:
                parsed_response = {
                    "task_analysis": response,
                    "tool_plan": [],
                    "execution_steps": [],
                    "expected_workflow": "",
                    "error_handling": "",
                    "success_criteria": ""
                }
        else:
            parsed_response = response
        
        # Extract components
        task_analysis = parsed_response.get("task_analysis", "")
        tool_plan = parsed_response.get("tool_plan", [])
        execution_steps = parsed_response.get("execution_steps", [])
        expected_workflow = parsed_response.get("expected_workflow", "")
        error_handling = parsed_response.get("error_handling", "")
        success_criteria = parsed_response.get("success_criteria", "")
        
        # For demonstration, evaluate against first task (in practice would match specific task)
        task_evaluated = expected["tasks"][0]
        
        # Evaluate components
        scores["tool_selection"] = evaluate_tool_selection(
            tool_plan, execution_steps, task_evaluated
        )
        
        scores["execution_efficiency"] = evaluate_execution_efficiency(
            execution_steps, task_evaluated, expected
        )
        
        scores["workflow_design"] = evaluate_workflow_design(
            tool_plan, expected_workflow, task_evaluated
        )
        
        scores["error_handling"] = evaluate_error_handling(
            error_handling, execution_steps
        )
        
        scores["result_quality"] = evaluate_result_quality(
            task_analysis, success_criteria, task_evaluated
        )
        
        scores["resource_optimization"] = evaluate_resource_optimization(
            execution_steps, expected
        )
        
        # Calculate overall score
        weights = {
            "tool_selection": 0.20,
            "execution_efficiency": 0.18,
            "workflow_design": 0.18,
            "error_handling": 0.15,
            "result_quality": 0.15,
            "resource_optimization": 0.14
        }
        
        scores["overall_score"] = sum(
            scores[component] * weight 
            for component, weight in weights.items()
        )
        
        # Store analysis details
        details["tools_planned"] = extract_tools_from_plan(tool_plan, execution_steps)
        details["execution_analysis"] = analyze_execution_plan(execution_steps)
        details["workflow_evaluation"] = evaluate_workflow_structure(tool_plan, expected_workflow)
        
        # Generate feedback
        details["feedback"] = generate_tool_bench_feedback(scores, parsed_response, task_evaluated)
        
    except Exception as e:
        details["errors"].append(f"Evaluation error: {str(e)}")
        scores["overall_score"] = 0
    
    return {
        "scores": scores,
        "details": details,
        "passed": scores["overall_score"] >= expected.get("passing_threshold", 80)
    }

def evaluate_tool_selection(tool_plan: List, execution_steps: List, task: Dict[str, Any]) -> float:
    """Evaluate appropriateness of tool selection."""
    score = 50  # Base score
    
    required_tools = set(task.get("required_tools", []))
    
    # Extract tools mentioned in plan and steps
    planned_tools = set()
    plan_text = " ".join(str(item) for item in tool_plan).lower()
    steps_text = " ".join(str(step) for step in execution_steps).lower()
    
    all_possible_tools = [
        "read_file", "write_file", "list_files",
        "database_query", "database_insert", 
        "http_get", "http_post",
        "process_data", "system_info", "system_execute",
        "execute_workflow", "get_tool_usage"
    ]
    
    for tool in all_possible_tools:
        if tool in plan_text or tool in steps_text:
            planned_tools.add(tool)
    
    # Score based on required tool coverage
    if required_tools:
        coverage = len(required_tools.intersection(planned_tools)) / len(required_tools)
        score += coverage * 30
    
    # Bonus for not over-selecting tools
    if len(planned_tools) <= len(required_tools) + 2:
        score += 10
    
    # Check for appropriate tool combinations
    if len(planned_tools) > 1:
        score += 10  # Multi-tool awareness
    
    return min(100, score)

def evaluate_execution_efficiency(execution_steps: List, task: Dict[str, Any], 
                                expected: Dict[str, Any]) -> float:
    """Evaluate efficiency of execution plan."""
    score = 60  # Base score
    
    if not execution_steps:
        return 20
    
    expected_steps = task.get("expected_steps", [])
    max_tool_calls = expected.get("tool_usage_metrics", {}).get("max_tool_calls_per_task", 15)
    
    # Score based on step count efficiency
    step_count = len(execution_steps)
    expected_count = len(expected_steps)
    
    if expected_count > 0:
        if step_count <= expected_count:
            score += 20
        elif step_count <= expected_count * 1.5:
            score += 10
        # Penalty for too many steps
        elif step_count > max_tool_calls:
            score -= 10
    
    # Check for logical sequencing
    steps_text = " ".join(str(step) for step in execution_steps).lower()
    if "first" in steps_text or "then" in steps_text or "next" in steps_text:
        score += 10
    
    # Check for parallel processing awareness
    if "parallel" in steps_text or "concurrent" in steps_text:
        score += 5
    
    return min(100, score)

def evaluate_workflow_design(tool_plan: List, expected_workflow: str, 
                           task: Dict[str, Any]) -> float:
    """Evaluate workflow design quality."""
    score = 55  # Base score
    
    plan_text = " ".join(str(item) for item in tool_plan).lower()
    workflow_text = expected_workflow.lower()
    
    # Check for workflow structure
    structure_keywords = ["step", "sequence", "flow", "chain", "pipeline"]
    for keyword in structure_keywords:
        if keyword in plan_text or keyword in workflow_text:
            score += 5
    
    # Check for dependency awareness
    dependency_keywords = ["depend", "require", "after", "before", "prerequisite"]
    for keyword in dependency_keywords:
        if keyword in plan_text or keyword in workflow_text:
            score += 7
    
    # Check for data flow understanding
    data_flow_keywords = ["input", "output", "result", "data", "process"]
    flow_mentions = sum(1 for keyword in data_flow_keywords 
                       if keyword in plan_text or keyword in workflow_text)
    score += min(flow_mentions * 3, 15)
    
    # Bonus for complexity handling
    if task.get("complexity") == "hard" and len(tool_plan) >= 5:
        score += 10
    
    return min(100, score)

def evaluate_error_handling(error_handling: str, execution_steps: List) -> float:
    """Evaluate error handling approach."""
    score = 50  # Base score
    
    if not error_handling:
        return 30
    
    error_text = error_handling.lower()
    steps_text = " ".join(str(step) for step in execution_steps).lower()
    
    # Check for error awareness
    error_keywords = ["error", "fail", "exception", "handle", "catch", "retry"]
    error_mentions = sum(1 for keyword in error_keywords if keyword in error_text)
    score += min(error_mentions * 5, 25)
    
    # Check for specific error scenarios
    specific_scenarios = ["timeout", "network", "file not found", "permission", "api limit"]
    scenario_mentions = sum(1 for scenario in specific_scenarios 
                          if scenario in error_text)
    score += min(scenario_mentions * 4, 16)
    
    # Check for recovery strategies
    recovery_keywords = ["fallback", "alternative", "backup", "recovery", "graceful"]
    recovery_mentions = sum(1 for keyword in recovery_keywords if keyword in error_text)
    score += min(recovery_mentions * 3, 9)
    
    return min(100, score)

def evaluate_result_quality(task_analysis: str, success_criteria: str, 
                          task: Dict[str, Any]) -> float:
    """Evaluate quality of result specification."""
    score = 45  # Base score
    
    analysis_text = task_analysis.lower()
    criteria_text = success_criteria.lower()
    expected_criteria = [criterion.lower() for criterion in task.get("success_criteria", [])]
    
    # Check task understanding
    task_description = task["description"].lower()
    key_terms = extract_key_terms(task_description)
    
    understanding_score = 0
    for term in key_terms:
        if term in analysis_text:
            understanding_score += 1
    
    if key_terms:
        score += (understanding_score / len(key_terms)) * 25
    
    # Check success criteria alignment
    if expected_criteria:
        criteria_alignment = 0
        for expected_criterion in expected_criteria:
            criterion_terms = extract_key_terms(expected_criterion)
            if any(term in criteria_text for term in criterion_terms):
                criteria_alignment += 1
        
        score += (criteria_alignment / len(expected_criteria)) * 20
    
    # Check for completeness indicators
    completeness_keywords = ["complete", "success", "verify", "validate", "confirm"]
    for keyword in completeness_keywords:
        if keyword in criteria_text:
            score += 2
    
    return min(100, score)

def evaluate_resource_optimization(execution_steps: List, expected: Dict[str, Any]) -> float:
    """Evaluate resource optimization awareness."""
    score = 65  # Base score
    
    steps_text = " ".join(str(step) for step in execution_steps).lower()
    
    # Check for optimization awareness
    optimization_keywords = ["efficient", "optimize", "minimize", "reduce", "batch"]
    for keyword in optimization_keywords:
        if keyword in steps_text:
            score += 7
    
    # Check for caching mentions
    caching_keywords = ["cache", "store", "reuse", "persist"]
    for keyword in caching_keywords:
        if keyword in steps_text:
            score += 5
    
    # Check for resource monitoring
    monitoring_keywords = ["monitor", "track", "measure", "analytics"]
    for keyword in monitoring_keywords:
        if keyword in steps_text:
            score += 4
    
    # Penalty for excessive tool calls
    max_calls = expected.get("tool_usage_metrics", {}).get("max_tool_calls_per_task", 15)
    if len(execution_steps) > max_calls:
        score -= 15
    
    return min(100, score)

def extract_tools_from_plan(tool_plan: List, execution_steps: List) -> List[str]:
    """Extract tools mentioned in plan and execution steps."""
    tools = []
    all_text = " ".join(str(item) for item in tool_plan + execution_steps).lower()
    
    possible_tools = [
        "read_file", "write_file", "list_files",
        "database_query", "database_insert",
        "http_get", "http_post", 
        "process_data", "system_info", "system_execute",
        "execute_workflow", "get_tool_usage"
    ]
    
    for tool in possible_tools:
        if tool in all_text:
            tools.append(tool)
    
    return tools

def analyze_execution_plan(execution_steps: List) -> Dict[str, Any]:
    """Analyze execution plan structure."""
    return {
        "step_count": len(execution_steps),
        "has_sequential_indicators": any("then" in str(step).lower() or "next" in str(step).lower() 
                                       for step in execution_steps),
        "has_error_handling": any("error" in str(step).lower() or "fail" in str(step).lower() 
                                for step in execution_steps),
        "mentions_validation": any("verify" in str(step).lower() or "check" in str(step).lower() 
                                 for step in execution_steps)
    }

def evaluate_workflow_structure(tool_plan: List, expected_workflow: str) -> Dict[str, Any]:
    """Evaluate workflow structure quality."""
    return {
        "has_clear_structure": len(tool_plan) > 0 and len(expected_workflow) > 0,
        "mentions_dependencies": any("depend" in str(item).lower() for item in tool_plan) or 
                               "depend" in expected_workflow.lower(),
        "has_data_flow": any("data" in str(item).lower() or "result" in str(item).lower() 
                           for item in tool_plan) or 
                        "data" in expected_workflow.lower(),
        "workflow_length": len(expected_workflow.split()) if expected_workflow else 0
    }

def extract_key_terms(text: str) -> List[str]:
    """Extract key terms from text."""
    words = text.split()
    terms = []
    
    skip_words = {"the", "and", "or", "to", "a", "an", "in", "on", "at", "by", "for", "with", "from"}
    
    for word in words:
        word = word.strip('.,!?():').lower()
        if len(word) > 3 and word not in skip_words and word.isalpha():
            terms.append(word)
    
    return terms

def generate_tool_bench_feedback(scores: Dict[str, float], response: Dict[str, Any], 
                                task: Dict[str, Any]) -> List[str]:
    """Generate feedback for ToolBench evaluation."""
    feedback = []
    
    overall_score = scores["overall_score"]
    if overall_score >= 90:
        feedback.append("Excellent tool usage and workflow design!")
    elif overall_score >= 80:
        feedback.append("Good tool usage with room for optimization.")
    else:
        feedback.append("Tool usage and workflow design need improvement.")
    
    # Component-specific feedback
    if scores["tool_selection"] < 70:
        feedback.append("Improve tool selection - ensure you choose the most appropriate tools.")
    
    if scores["execution_efficiency"] < 70:
        feedback.append("Optimize execution efficiency - reduce unnecessary steps and tool calls.")
    
    if scores["workflow_design"] < 70:
        feedback.append("Enhance workflow design - better structure and sequencing needed.")
    
    if scores["error_handling"] < 70:
        feedback.append("Strengthen error handling - consider more edge cases and recovery strategies.")
    
    if scores["result_quality"] < 70:
        feedback.append("Improve result quality - ensure comprehensive task completion.")
    
    if scores["resource_optimization"] < 70:
        feedback.append("Focus on resource optimization - minimize API calls and improve efficiency.")
    
    # Task complexity feedback
    task_complexity = task.get("complexity", "medium")
    if task_complexity == "hard" and overall_score < 85:
        feedback.append("Complex tasks require more sophisticated tool combinations and planning.")
    
    # Specific improvement suggestions
    tool_plan = response.get("tool_plan", [])
    if len(tool_plan) < 3:
        feedback.append("Consider more comprehensive tool planning for multi-step tasks.")
    
    error_handling = response.get("error_handling", "")
    if len(error_handling) < 50:
        feedback.append("Provide more detailed error handling strategies.")
    
    return feedback