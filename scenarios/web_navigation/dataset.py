"""
WebArena-style dataset - real web navigation tasks
"""
from typing import Dict, List

WEB_NAVIGATION_TASKS = [
    {
        "task_id": "web_nav_001",
        "description": "Navigate to products page and add laptop to cart",
        "start_url": "http://127.0.0.1:8002",
        "goal": "Add the laptop product to shopping cart",
        "success_conditions": [
            "Navigated to products page",
            "Found laptop product",
            "Added laptop to cart",
            "Verified cart contents"
        ],
        "max_steps": 10,
        "evaluation_method": "action_sequence"
    },
    {
        "task_id": "web_nav_002", 
        "description": "Search for keyboard and check availability",
        "start_url": "http://127.0.0.1:8002",
        "goal": "Search for keyboard products and determine availability",
        "success_conditions": [
            "Used search functionality",
            "Searched for 'keyboard'",
            "Found keyboard product",
            "Identified out-of-stock status"
        ],
        "max_steps": 8,
        "evaluation_method": "goal_completion"
    },
    {
        "task_id": "web_nav_003",
        "description": "Complete full purchase workflow",
        "start_url": "http://127.0.0.1:8002",
        "goal": "Add monitor to cart and complete checkout",
        "success_conditions": [
            "Added monitor to cart",
            "Navigated to cart page",
            "Initiated checkout process",
            "Completed purchase"
        ],
        "max_steps": 15,
        "evaluation_method": "workflow_completion"
    }
]

def get_web_navigation_tasks() -> List[Dict]:
    """Get web navigation tasks for evaluation."""
    return WEB_NAVIGATION_TASKS

def evaluate_web_action_sequence(actions: List[str], task: Dict) -> Dict:
    """Evaluate web navigation action sequence."""
    task_id = task["task_id"]
    success_conditions = task["success_conditions"]
    max_steps = task["max_steps"]
    
    score = 0
    conditions_met = 0
    
    # Check if actions meet success conditions
    actions_text = " ".join(actions).lower()
    
    for condition in success_conditions:
        condition_keywords = condition.lower().split()
        if any(keyword in actions_text for keyword in condition_keywords):
            conditions_met += 1
    
    # Calculate score based on conditions met and efficiency
    if success_conditions:
        condition_score = (conditions_met / len(success_conditions)) * 70
        efficiency_score = max(0, 30 - (len(actions) - max_steps) * 2) if len(actions) > max_steps else 30
        score = condition_score + efficiency_score
    
    return {
        "task_id": task_id,
        "score": min(100, max(0, score)),
        "conditions_met": conditions_met,
        "total_conditions": len(success_conditions),
        "actions_taken": len(actions),
        "max_steps": max_steps,
        "passed": score >= 70
    }