import json
import re
from typing import Dict, Any, List

def evaluate_web_navigation(response: str, expected: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optimized web navigation evaluation with enhanced task completion detection.
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
        "errors": [],
        "parsed_actions": 0,
        "reasoning_quality": 0
    }
    
    try:
        # Parse response efficiently
        parsed_response = parse_navigation_response_optimized(response)
        actions = parsed_response.get("actions", [])
        reasoning = normalize_reasoning(parsed_response.get("reasoning", ""))
        
        details["parsed_actions"] = len(actions)
        details["reasoning_quality"] = assess_reasoning_quality(reasoning)
        
        # Evaluate tasks with enhanced completion detection
        total_task_score = 0
        completed_tasks = 0
        
        for task in expected.get("tasks", []):
            task_score, completion_indicators = evaluate_task_completion(actions, reasoning, task)
            task_points = get_task_points(task)
            task_completion_rate = task_score / task_points if task_points > 0 else 0
            
            if task_completion_rate >= 0.6:  # Lowered threshold for better feedback
                completed_tasks += 1
                
            details["task_scores"].append({
                "task_id": task.get("task_id", task.get("id", "unknown")),
                "description": task.get("description", ""),
                "score": task_score,
                "max_score": task_points,
                "completion_rate": task_completion_rate,
                "completion_indicators": completion_indicators
            })
            total_task_score += task_score
            
        # Calculate scores efficiently
        max_total_score = sum(get_task_points(task) for task in expected.get("tasks", []))
        scores["task_completion"] = (total_task_score / max_total_score * 100) if max_total_score > 0 else 0
        
        scores["navigation_accuracy"] = assess_navigation_accuracy(actions, reasoning)
        scores["efficiency"] = assess_efficiency(actions, expected)
        scores["error_handling"] = assess_error_handling(reasoning, actions)
        
        # Weighted overall score with completion bonus
        completion_bonus = (completed_tasks / len(expected.get("tasks", [1]))) * 5 if expected.get("tasks") else 0
        
        scores["overall_score"] = (
            scores["navigation_accuracy"] * 0.3 +
            scores["task_completion"] * 0.4 + 
            scores["error_handling"] * 0.15 +
            scores["efficiency"] * 0.15
        ) + completion_bonus
        
        scores["overall_score"] = min(100, scores["overall_score"])
        
        # Generate concise feedback
        details["feedback"] = generate_navigation_feedback(scores, completed_tasks, len(expected.get("tasks", [])))
        details["actions_taken"] = actions
        
    except Exception as e:
        details["errors"].append(f"Evaluation error: {str(e)}")
        scores["overall_score"] = 0
        
    return {
        "scores": scores,
        "details": details,
        "passed": scores["overall_score"] >= 60
    }

def parse_navigation_response_optimized(response: str) -> Dict[str, Any]:
    """Optimized parsing for navigation responses."""
    # Handle structured responses
    if isinstance(response, dict):
        return response
    
    # Try JSON extraction from markdown
    if '```json' in response:
        json_start = response.find('```json') + 7
        json_end = response.find('```', json_start)
        if json_end > json_start:
            try:
                return json.loads(response[json_start:json_end].strip())
            except json.JSONDecodeError:
                pass
    
    # Try direct JSON parsing
    try:
        if response.strip().startswith('{'):
            return json.loads(response)
    except json.JSONDecodeError:
        pass
    
    # Extract actions using patterns
    actions = extract_actions_from_text(response)
    return {
        "actions": actions,
        "reasoning": response
    }

def extract_actions_from_text(response: str) -> List[str]:
    """Extract navigation actions from text response."""
    action_patterns = [
        r'(?:Navigate to|Go to|Visit)\s+([^\n]+)',
        r'(?:Click on|Click|Select)\s+([^\n]+)', 
        r'(?:Search for|Search)\s+([^\n]+)',
        r'(?:Type|Enter)\s+([^\n]+)',
        r'(?:Add to cart|Purchase|Buy)\s*([^\n]*)'
    ]
    
    actions = []
    for pattern in action_patterns:
        matches = re.findall(pattern, response, re.IGNORECASE)
        actions.extend(matches)
    
    return actions

def normalize_reasoning(reasoning) -> str:
    """Normalize reasoning to consistent string format."""
    if isinstance(reasoning, list):
        return " ".join(str(item) for item in reasoning)
    elif isinstance(reasoning, dict):
        return " ".join(str(v) for v in reasoning.values())
    else:
        return str(reasoning)

def evaluate_task_completion(actions: List[str], reasoning: str, task: Dict[str, Any]) -> tuple:
    """Enhanced task completion evaluation with detailed indicators."""
    score = 0
    max_score = get_task_points(task)
    completion_indicators = []
    
    task_description = task.get("description", "").lower()
    success_conditions = task.get("success_conditions", task.get("success_criteria", []))
    
    # Combine actions and reasoning for analysis
    combined_text = " ".join(str(action) for action in actions).lower() + " " + reasoning.lower()
    
    # Enhanced keyword matching for different task types
    task_keywords = extract_task_keywords(task_description)
    keyword_matches = sum(1 for keyword in task_keywords if keyword in combined_text)
    
    if keyword_matches > 0:
        keyword_score = min(keyword_matches / len(task_keywords), 1.0) * (max_score * 0.4)
        score += keyword_score
        completion_indicators.append(f"Keywords matched: {keyword_matches}/{len(task_keywords)}")
    
    # Success conditions evaluation
    conditions_met = 0
    for condition in success_conditions:
        if evaluate_condition_completion(condition, combined_text):
            conditions_met += 1
            completion_indicators.append(f"Condition met: {condition[:50]}...")
    
    if success_conditions:
        condition_score = min(conditions_met / len(success_conditions), 1.0) * (max_score * 0.5)
        score += condition_score
    
    # Action sequence quality bonus
    if len(actions) >= 3:
        score += max_score * 0.1
        completion_indicators.append("Multiple actions planned")
    
    return min(score, max_score), completion_indicators

def extract_task_keywords(description: str) -> List[str]:
    """Extract key task-specific keywords."""
    # E-commerce specific keywords
    ecommerce_keywords = ["laptop", "cart", "product", "purchase", "buy", "search", "checkout"]
    navigation_keywords = ["navigate", "click", "page", "menu", "link", "button"]
    
    words = description.lower().split()
    keywords = []
    
    for word in words:
        word = word.strip('.,!?():')
        if len(word) > 3 and (word in ecommerce_keywords or word in navigation_keywords):
            keywords.append(word)
    
    return list(set(keywords))

def evaluate_condition_completion(condition: str, combined_text: str) -> bool:
    """Evaluate if a success condition is addressed."""
    condition_lower = condition.lower()
    key_terms = [word for word in condition_lower.split() if len(word) > 3]
    
    # Check if at least 60% of key terms are mentioned
    matches = sum(1 for term in key_terms if term in combined_text)
    return matches >= len(key_terms) * 0.6

def get_task_points(task: Dict[str, Any]) -> int:
    """Get points for a task based on difficulty."""
    return task.get("points", {"easy": 75, "medium": 100, "hard": 125}.get(task.get("difficulty", "medium"), 100))

def assess_reasoning_quality(reasoning: str) -> float:
    """Assess reasoning quality efficiently."""
    if not reasoning or len(reasoning) < 20:
        return 0
    
    score = 0
    reasoning_lower = reasoning.lower()
    
    # Check for strategic indicators
    if any(word in reasoning_lower for word in ["plan", "strategy", "approach", "steps"]):
        score += 30
    
    # Check for validation mentions
    if any(word in reasoning_lower for word in ["verify", "check", "confirm", "ensure"]):
        score += 20
    
    # Length bonus for detailed reasoning
    if len(reasoning) > 100:
        score += 20
    
    return min(score, 70)

def assess_navigation_accuracy(actions: List[str], reasoning: str) -> float:
    """Assess navigation accuracy efficiently."""
    score = 60  # Base score
    
    combined_text = " ".join(str(action) for action in actions).lower() + " " + reasoning.lower()
    
    # URL usage
    if any(pattern in combined_text for pattern in ["127.0.0.1:8002", "localhost", "http"]):
        score += 20
    
    # Navigation actions
    nav_actions = ["navigate", "click", "search", "type", "submit"]
    found_actions = sum(1 for action in nav_actions if action in combined_text)
    score += min(found_actions * 4, 20)
    
    return min(score, 100)

def assess_efficiency(actions: List[str], expected: Dict[str, Any]) -> float:
    """Assess efficiency based on action count and planning."""
    if not actions:
        return 30
    
    score = 70  # Base score
    
    # Optimal action count
    min_actions = sum(len(task.get("success_conditions", [])) for task in expected.get("tasks", []))
    actual_actions = len(actions)
    
    if min_actions > 0 and actual_actions <= min_actions * 1.5:
        score += 20
    elif actual_actions > min_actions * 2:
        score -= 10
    
    return min(score, 100)

def assess_error_handling(reasoning: str, actions: List[str]) -> float:
    """Assess error handling approach."""
    score = 50  # Base score
    
    reasoning_lower = reasoning.lower()
    
    # Error awareness
    error_terms = ["error", "fail", "verify", "check", "validate"]
    score += sum(8 for term in error_terms if term in reasoning_lower)
    
    return min(score, 100)

def generate_navigation_feedback(scores: Dict[str, float], completed_tasks: int, total_tasks: int) -> List[str]:
    """Generate concise, actionable feedback."""
    feedback = []
    
    if scores["overall_score"] >= 80:
        feedback.append("🎆 Excellent web navigation performance!")
    elif scores["overall_score"] >= 60:
        feedback.append("✅ Good web navigation with minor improvements needed.")
    else:
        feedback.append("📈 Web navigation needs improvement.")
    
    # Task completion feedback
    if total_tasks > 0:
        completion_rate = completed_tasks / total_tasks
        if completion_rate >= 0.8:
            feedback.append(f"✓ Excellent task completion: {completed_tasks}/{total_tasks}")
        elif completion_rate >= 0.5:
            feedback.append(f"⚠️ Moderate task completion: {completed_tasks}/{total_tasks}")
        else:
            feedback.append(f"❌ Low task completion: {completed_tasks}/{total_tasks}")
    
    # Component-specific feedback
    if scores["task_completion"] < 60:
        feedback.append("🎯 Focus on addressing all task requirements completely.")
    
    if scores["navigation_accuracy"] < 70:
        feedback.append("🧭 Improve navigation accuracy and URL usage.")
    
    return feedback