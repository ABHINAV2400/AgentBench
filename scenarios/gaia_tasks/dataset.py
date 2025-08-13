"""
GAIA dataset loader - Direct Hugging Face Hub integration
Replaces manual dataset with authentic GAIA from HF
"""
from typing import Dict, List
from hf_dataset_loader import HuggingFaceDatasetLoader

def get_gaia_tasks(limit: int = None) -> List[Dict]:
    """Get GAIA tasks directly from Hugging Face, with fallback to local tasks."""
    try:
        loader = HuggingFaceDatasetLoader()
        dataset = loader.load_benchmark_dataset('gaia', limit=limit)
        return dataset['tasks']
    except Exception as e:
        print(f"⚠️  Could not load GAIA from HuggingFace ({e}), using local fallback tasks")
        return get_local_gaia_tasks(limit)

def get_task_by_id(task_id: str) -> Dict:
    """Get a specific task by ID from HF dataset."""
    tasks = get_gaia_tasks()
    for task in tasks:
        if task["task_id"] == task_id:
            return task
    raise ValueError(f"Task {task_id} not found in GAIA dataset")

def evaluate_gaia_response(response: str, task: Dict) -> Dict:
    """Evaluate GAIA task response against ground truth."""
    try:
        expected_answer = task.get('answer', '')
        question = task.get('question', '')
        level = task.get('level', 1)
        
        response_lower = response.lower()
        answer_lower = expected_answer.lower() if expected_answer else ''
        
        # Score based on answer presence and quality
        score = 0
        feedback = []
        
        # Check if expected answer is mentioned
        if answer_lower and answer_lower in response_lower:
            score += 40
            feedback.append("Expected answer found in response")
        elif answer_lower and any(word in response_lower for word in answer_lower.split()[:3]):
            score += 20
            feedback.append("Partial answer match found")
        
        # Score based on response quality and length
        if len(response) > 100:
            score += 20
            feedback.append("Detailed response provided")
        elif len(response) > 50:
            score += 10
            feedback.append("Adequate response length")
        
        # Check for reasoning indicators
        reasoning_words = ['because', 'therefore', 'analysis', 'first', 'then', 'finally', 'step']
        reasoning_count = sum(1 for word in reasoning_words if word in response_lower)
        
        if reasoning_count >= 3:
            score += 25
            feedback.append("Strong reasoning indicators found")
        elif reasoning_count >= 1:
            score += 15
            feedback.append("Some reasoning shown")
        
        # Bonus for complex tasks (level 2+)
        if level >= 2 and score >= 60:
            score += 15
            feedback.append("Good performance on complex task")
        
        passed = score >= 60
        
        return {
            "task_id": task.get('task_id', 'unknown'),
            "score": min(100, score),
            "passed": passed,
            "feedback": feedback,
            "answer_match": answer_lower in response_lower if answer_lower else False,
            "reasoning_score": reasoning_count,
            "result": f"Score: {score}/100, Answer match: {answer_lower in response_lower if answer_lower else 'N/A'}"
        }
        
    except Exception as e:
        return {
            "task_id": task.get('task_id', 'unknown'),
            "score": 0,
            "passed": False,
            "feedback": [f"Evaluation error: {str(e)}"],
            "result": str(e)
        }

def get_dataset_info() -> Dict:
    """Get information about the GAIA dataset."""
    return {
        "name": "GAIA",
        "source": "huggingface:gaia-benchmark/GAIA",
        "description": "General AI Assistant benchmark for real-world assistant capabilities",
        "total_tasks": 466,
        "levels": [1, 2, 3],
        "url": "https://huggingface.co/datasets/gaia-benchmark/GAIA",
        "paper": "https://arxiv.org/abs/2311.12983"
    }

# Legacy compatibility function
def get_gaia_dataset() -> Dict:
    """Legacy function for compatibility."""
    return {
        "type": "multi_step_reasoning",
        "tasks": get_gaia_tasks(),
        "info": get_dataset_info()
    }