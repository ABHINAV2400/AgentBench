import json
import re
import requests
from typing import Dict, Any, List

def evaluate_web_navigation(response: str, expected: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate web navigation agent response against expected criteria.
    """
    scores = {
        "navigation_accuracy": 0,
        "task_completion": 0, 
        "error_handling": 0,
        "efficiency": 0,
        "overall_score": 0
    }
    
    details = {
        "task_scores": [],
        "feedback": [],
        "actions_taken": [],
        "errors": []
    }
    
    try:
        # Parse the response
        if isinstance(response, str):
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                parsed_response = json.loads(json_match.group())
            else:
                parsed_response = {"actions": [], "reasoning": response}
        else:
            parsed_response = response
            
        actions = parsed_response.get("actions", [])
        reasoning = parsed_response.get("reasoning", "")
        
        # Evaluate each task
        total_task_score = 0
        for task in expected["tasks"]:
            task_score = evaluate_single_task(actions, reasoning, task)
            details["task_scores"].append({
                "task_id": task["id"],
                "description": task["description"],
                "score": task_score,
                "max_score": task["points"]
            })
            total_task_score += task_score
            
        # Calculate component scores
        max_total_score = sum(task["points"] for task in expected["tasks"])
        scores["task_completion"] = (total_task_score / max_total_score) * 100 if max_total_score > 0 else 0
        
        # Navigation accuracy based on correct URL patterns and navigation flow
        nav_score = evaluate_navigation_accuracy(actions)
        scores["navigation_accuracy"] = nav_score
        
        # Efficiency based on number of actions vs minimum required
        efficiency_score = evaluate_efficiency(actions, expected)
        scores["efficiency"] = efficiency_score
        
        # Error handling based on response quality and edge case awareness
        error_handling_score = evaluate_error_handling(reasoning, parsed_response)
        scores["error_handling"] = error_handling_score
        
        # Overall score
        scores["overall_score"] = (
            scores["navigation_accuracy"] * 0.25 +
            scores["task_completion"] * 0.4 + 
            scores["error_handling"] * 0.2 +
            scores["efficiency"] * 0.15
        )
        
        # Generate feedback
        details["feedback"] = generate_feedback(scores, details["task_scores"])
        details["actions_taken"] = actions
        
    except Exception as e:
        details["errors"].append(f"Evaluation error: {str(e)}")
        scores["overall_score"] = 0
        
    return {
        "scores": scores,
        "details": details,
        "passed": scores["overall_score"] >= 70  # 70% threshold
    }

def evaluate_single_task(actions: List[str], reasoning: str, task: Dict[str, Any]) -> float:
    """Evaluate a single task against expected criteria."""
    score = 0
    max_score = task["points"]
    
    task_description = task["description"].lower()
    expected_actions = task.get("expected_actions", [])
    success_criteria = task.get("success_criteria", [])
    
    # Check if expected actions are present
    actions_text = " ".join(str(action) for action in actions).lower()
    reasoning_text = reasoning.lower()
    
    action_matches = 0
    for expected_action in expected_actions:
        if any(expected_action.lower() in action.lower() for action in actions):
            action_matches += 1
    
    # Score based on action matching
    if expected_actions:
        action_score = (action_matches / len(expected_actions)) * (max_score * 0.6)
        score += action_score
    
    # Check success criteria
    criteria_met = 0
    for criterion in success_criteria:
        if criterion.lower() in reasoning_text or criterion.lower() in actions_text:
            criteria_met += 1
    
    if success_criteria:
        criteria_score = (criteria_met / len(success_criteria)) * (max_score * 0.4)
        score += criteria_score
    
    return min(score, max_score)

def evaluate_navigation_accuracy(actions: List[str]) -> float:
    """Evaluate navigation accuracy based on correct URL patterns."""
    score = 100
    
    # Check for proper base URL usage
    base_url_used = any("127.0.0.1:8002" in str(action) for action in actions)
    if not base_url_used:
        score -= 30
    
    # Check for logical navigation flow
    navigation_actions = [action for action in actions if "web_navigate" in str(action)]
    if len(navigation_actions) == 0:
        score -= 40
    
    return max(0, score)

def evaluate_efficiency(actions: List[str], expected: Dict[str, Any]) -> float:
    """Evaluate efficiency based on action count vs minimum required."""
    if not actions:
        return 0
        
    # Calculate minimum actions needed across all tasks
    min_actions_needed = sum(len(task.get("expected_actions", [])) for task in expected["tasks"])
    actual_actions = len(actions)
    
    if min_actions_needed == 0:
        return 100
        
    # Efficiency decreases with excess actions
    if actual_actions <= min_actions_needed:
        return 100
    else:
        excess_ratio = (actual_actions - min_actions_needed) / min_actions_needed
        return max(0, 100 - (excess_ratio * 30))

def evaluate_error_handling(reasoning: str, response: Dict[str, Any]) -> float:
    """Evaluate error handling capabilities."""
    score = 60  # Base score
    
    # Check for error awareness in reasoning
    error_keywords = ["error", "handle", "retry", "fail", "exception", "graceful"]
    if any(keyword in reasoning.lower() for keyword in error_keywords):
        score += 20
        
    # Check for structured response
    if "expected_outcome" in response:
        score += 10
        
    # Check for validation steps
    validation_keywords = ["verify", "check", "confirm", "validate"]
    if any(keyword in reasoning.lower() for keyword in validation_keywords):
        score += 10
        
    return min(100, score)

def generate_feedback(scores: Dict[str, float], task_scores: List[Dict]) -> List[str]:
    """Generate human-readable feedback."""
    feedback = []
    
    if scores["overall_score"] >= 90:
        feedback.append("Excellent web navigation performance!")
    elif scores["overall_score"] >= 70:
        feedback.append("Good web navigation with room for improvement.")
    else:
        feedback.append("Web navigation needs significant improvement.")
    
    # Task-specific feedback
    for task_score in task_scores:
        if task_score["score"] < task_score["max_score"] * 0.5:
            feedback.append(f"Task '{task_score['description']}' needs improvement.")
    
    # Component feedback
    if scores["navigation_accuracy"] < 70:
        feedback.append("Improve navigation accuracy - ensure correct URLs and flow.")
    
    if scores["efficiency"] < 70:
        feedback.append("Optimize action sequence for better efficiency.")
        
    if scores["error_handling"] < 70:
        feedback.append("Add better error handling and validation steps.")
    
    return feedback