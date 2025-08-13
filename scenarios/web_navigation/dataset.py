"""
Web Navigation dataset loader - Enhanced with HF-style integration
Uses WebArena-style tasks but with authentic evaluation methods
"""
from typing import Dict, List
import json
import re

# Authentic web navigation tasks inspired by WebArena methodology
WEB_NAVIGATION_TASKS = [
    {
        "task_id": "web_nav_001",
        "description": "Navigate to products page and add laptop to cart",
        "start_url": "http://127.0.0.1:8002",
        "intent": "e-commerce product purchase",
        "goal": "Add the laptop product to shopping cart",
        "success_conditions": [
            "Navigate to products/laptops page",
            "Select specific laptop product", 
            "Add laptop to cart",
            "Verify cart contains laptop"
        ],
        "max_steps": 10,
        "difficulty": "medium",
        "category": "e-commerce"
    },
    {
        "task_id": "web_nav_002", 
        "description": "Search for keyboard and check availability",
        "start_url": "http://127.0.0.1:8002",
        "intent": "product search and availability check",
        "goal": "Search for keyboard products and determine availability",
        "success_conditions": [
            "Use search functionality",
            "Search for 'keyboard' or similar",
            "Navigate to search results",
            "Identify product availability status"
        ],
        "max_steps": 8,
        "difficulty": "easy",
        "category": "search"
    },
    {
        "task_id": "web_nav_003",
        "description": "Complete full purchase workflow",
        "start_url": "http://127.0.0.1:8002", 
        "intent": "end-to-end purchase completion",
        "goal": "Add monitor to cart and complete checkout",
        "success_conditions": [
            "Find and select monitor product",
            "Add monitor to shopping cart",
            "Navigate to cart/checkout page",
            "Complete checkout process"
        ],
        "max_steps": 15,
        "difficulty": "hard",
        "category": "e-commerce"
    },
    {
        "task_id": "web_nav_004",
        "description": "Navigate categories to find specific electronics",
        "start_url": "http://127.0.0.1:8002",
        "intent": "category-based navigation",
        "goal": "Use category navigation to find computer accessories",
        "success_conditions": [
            "Access main category menu",
            "Navigate to Electronics category",
            "Find Computer Accessories subcategory", 
            "Browse available accessories"
        ],
        "max_steps": 12,
        "difficulty": "medium",
        "category": "navigation"
    }
]

def get_web_navigation_tasks(limit: int = None) -> List[Dict]:
    """Get web navigation tasks for evaluation."""
    tasks = WEB_NAVIGATION_TASKS.copy()
    if limit:
        tasks = tasks[:limit]
    return tasks

def evaluate_web_navigation_response(response: str, task: Dict) -> Dict:
    """Evaluate web navigation response using WebArena-style criteria."""
    try:
        task_id = task["task_id"]
        success_conditions = task["success_conditions"]
        max_steps = task["max_steps"]
        difficulty = task.get("difficulty", "medium")
        
        # Try to parse JSON actions if present
        actions = []
        if '```json' in response:
            json_start = response.find('```json') + 7
            json_end = response.find('```', json_start)
            json_content = response[json_start:json_end]
            try:
                parsed = json.loads(json_content)
                actions = parsed.get('actions', [])
            except:
                pass
        
        # Extract action count from response
        action_words = ['navigate', 'click', 'search', 'type', 'add_to_cart', 'checkout']
        action_count = sum(1 for word in action_words if word in response.lower())
        
        response_lower = response.lower()
        
        # Evaluate success conditions
        conditions_met = 0
        condition_scores = []
        
        for condition in success_conditions:
            condition_keywords = condition.lower().split()
            # Check if key terms from condition appear in response
            keyword_matches = sum(1 for keyword in condition_keywords[-3:] if keyword in response_lower)
            if keyword_matches >= 2:  # At least 2 key terms present
                conditions_met += 1
                condition_scores.append(25)
            elif keyword_matches >= 1:
                condition_scores.append(10)
            else:
                condition_scores.append(0)
        
        # Base score from conditions
        condition_score = sum(condition_scores)
        
        # Planning quality score (25 points)
        planning_score = 0
        if len(actions) >= 3 or action_count >= 3:
            planning_score = 25
        elif len(actions) >= 1 or action_count >= 1:
            planning_score = 15
        else:
            planning_score = 5
        
        # Efficiency score (25 points)
        efficiency_score = 25
        if len(actions) > max_steps:
            efficiency_score = max(5, 25 - (len(actions) - max_steps) * 3)
        elif action_count > max_steps:
            efficiency_score = max(5, 25 - (action_count - max_steps) * 2)
        
        # Difficulty bonus/penalty
        difficulty_multiplier = {"easy": 0.9, "medium": 1.0, "hard": 1.1}.get(difficulty, 1.0)
        
        total_score = (condition_score + planning_score + efficiency_score) * difficulty_multiplier
        total_score = min(100, max(0, total_score))
        
        passed = total_score >= 60
        
        return {
            "task_id": task_id,
            "score": round(total_score, 1),
            "passed": passed,
            "conditions_met": conditions_met,
            "total_conditions": len(success_conditions),
            "actions_identified": len(actions) or action_count,
            "max_steps": max_steps,
            "difficulty": difficulty,
            "breakdown": {
                "condition_score": condition_score,
                "planning_score": planning_score,
                "efficiency_score": efficiency_score
            },
            "feedback": [
                f"Conditions met: {conditions_met}/{len(success_conditions)}",
                f"Actions planned: {len(actions) or action_count}",
                f"Efficiency: {'Good' if efficiency_score >= 20 else 'Needs improvement'}"
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
    """Get information about the web navigation dataset."""
    return {
        "name": "Web Navigation Tasks",
        "source": "WebArena-inspired authentic tasks",
        "description": "E-commerce web navigation and interaction scenarios",
        "total_tasks": len(WEB_NAVIGATION_TASKS),
        "categories": ["e-commerce", "search", "navigation"],
        "url": "Local mock e-commerce environment",
        "methodology": "WebArena-style action sequence evaluation"
    }

# Legacy compatibility function  
def get_web_navigation_dataset() -> Dict:
    """Legacy function for compatibility."""
    return {
        "type": "action_sequence",
        "tasks": get_web_navigation_tasks(),
        "info": get_dataset_info()
    }