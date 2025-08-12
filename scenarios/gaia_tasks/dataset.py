"""
GAIA-style dataset - general AI assistant tasks
"""
from typing import Dict, List

GAIA_TASKS = [
    {
        "task_id": "gaia_001",
        "question": "Find information about Tesla's founding year, compare it with Apple's founding year, and calculate the difference. Then provide weather information for Tesla's headquarters location.",
        "level": 2,
        "task_type": "multi_step_research",
        "expected_steps": [
            "Research Tesla founding year",
            "Research Apple founding year", 
            "Calculate difference",
            "Identify Tesla headquarters",
            "Get weather information"
        ],
        "ground_truth": {
            "tesla_founded": 2003,
            "apple_founded": 1976,
            "difference": 27,
            "headquarters": "Austin, Texas"
        },
        "evaluation_criteria": [
            "Correct Tesla founding year (2003)",
            "Correct Apple founding year (1976)",
            "Correct calculation (27 years)",
            "Valid headquarters location",
            "Weather information retrieved"
        ]
    },
    {
        "task_id": "gaia_002",
        "question": "Analyze the sentiment of this text: 'The new product launch was amazing and exceeded all expectations, though the price point was disappointing.' Then translate the positive aspects to Spanish.",
        "level": 1,
        "task_type": "multi_modal_analysis",
        "expected_steps": [
            "Analyze text sentiment",
            "Identify positive aspects",
            "Translate to Spanish"
        ],
        "ground_truth": {
            "sentiment": "mixed/positive",
            "positive_aspects": ["amazing", "exceeded expectations"],
            "spanish_translation": "increíble y superó todas las expectativas"
        },
        "evaluation_criteria": [
            "Identified mixed or positive sentiment",
            "Extracted positive aspects correctly",
            "Provided Spanish translation",
            "Explained reasoning process"
        ]
    },
    {
        "task_id": "gaia_003",
        "question": "A movie directed by Christopher Nolan was released in 2010. Find this movie, determine its rating, and explain whether it would be suitable for someone who likes sci-fi movies with ratings above 8.5.",
        "level": 2,
        "task_type": "reasoning_chain",
        "expected_steps": [
            "Identify Nolan 2010 movie",
            "Find movie rating",
            "Apply rating criteria",
            "Make recommendation"
        ],
        "ground_truth": {
            "movie": "Inception",
            "year": 2010,
            "director": "Christopher Nolan",
            "rating": 8.8,
            "recommendation": "Yes, suitable (8.8 > 8.5)"
        },
        "evaluation_criteria": [
            "Correctly identified Inception",
            "Found correct rating (8.8)",
            "Applied comparison logic (8.8 > 8.5)",
            "Made appropriate recommendation",
            "Showed clear reasoning"
        ]
    }
]

def get_gaia_tasks() -> List[Dict]:
    """Get GAIA tasks for evaluation."""
    return GAIA_TASKS

def evaluate_gaia_response(response: str, task: Dict) -> Dict:
    """Evaluate GAIA task response."""
    task_id = task["task_id"]
    ground_truth = task["ground_truth"]
    criteria = task["evaluation_criteria"]
    
    response_lower = response.lower()
    score = 0
    criteria_met = 0
    
    # Check ground truth values
    for key, expected_value in ground_truth.items():
        if isinstance(expected_value, (int, float)):
            if str(expected_value) in response or str(expected_value) in response_lower:
                score += 20
        elif isinstance(expected_value, str):
            if expected_value.lower() in response_lower:
                score += 20
        elif isinstance(expected_value, list):
            if any(item.lower() in response_lower for item in expected_value):
                score += 15
    
    # Check evaluation criteria
    for criterion in criteria:
        criterion_keywords = criterion.lower().split()
        if any(keyword in response_lower for keyword in criterion_keywords[-3:]):
            criteria_met += 1
    
    # Add criteria score
    if criteria:
        criteria_score = (criteria_met / len(criteria)) * 30
        score += criteria_score
    
    return {
        "task_id": task_id,
        "score": min(100, max(0, score)),
        "criteria_met": criteria_met,
        "total_criteria": len(criteria),
        "passed": score >= 70,
        "ground_truth_found": any(str(v).lower() in response_lower for v in ground_truth.values())
    }