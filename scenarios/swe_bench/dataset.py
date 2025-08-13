"""
SWE-bench dataset loader - Direct Hugging Face Hub integration
Replaces manual dataset with authentic SWE-bench from HF
"""
from typing import Dict, List
from hf_dataset_loader import HuggingFaceDatasetLoader

def get_swe_bench_problems(limit: int = None) -> List[Dict]:
    """Get SWE-bench problems directly from Hugging Face."""
    loader = HuggingFaceDatasetLoader()
    dataset = loader.load_benchmark_dataset('swe_bench', limit=limit)
    return dataset['problems']

def get_problem_by_id(instance_id: str) -> Dict:
    """Get a specific problem by instance ID from HF dataset."""
    problems = get_swe_bench_problems()
    for problem in problems:
        if problem["instance_id"] == instance_id:
            return problem
    raise ValueError(f"Problem {instance_id} not found in SWE-bench dataset")

def evaluate_patch(generated_patch: str, expected_patch: str) -> Dict:
    """Evaluate generated patch against expected solution."""
    try:
        # Simple similarity scoring (can be enhanced with more sophisticated metrics)
        generated_lines = set(generated_patch.strip().split('\n'))
        expected_lines = set(expected_patch.strip().split('\n'))
        
        if not expected_lines:
            return {"passed": len(generated_lines) == 0, "similarity": 1.0 if len(generated_lines) == 0 else 0.0}
        
        intersection = generated_lines.intersection(expected_lines)
        union = generated_lines.union(expected_lines)
        
        similarity = len(intersection) / len(union) if union else 0.0
        passed = similarity >= 0.5  # 50% similarity threshold
        
        return {
            "passed": passed,
            "similarity": similarity,
            "result": f"Patch similarity: {similarity:.2f}"
        }
    except Exception as e:
        return {
            "passed": False,
            "similarity": 0.0,
            "result": str(e)
        }

def get_dataset_info() -> Dict:
    """Get information about the SWE-bench dataset."""
    return {
        "name": "SWE-bench",
        "source": "huggingface:princeton-nlp/SWE-bench",
        "description": "Software engineering problems from real GitHub repositories",
        "total_problems": 2294,
        "repositories": ["django", "requests", "sympy", "flask", "matplotlib"],
        "url": "https://huggingface.co/datasets/princeton-nlp/SWE-bench",
        "paper": "https://arxiv.org/abs/2310.06770"
    }

# Legacy compatibility function
def get_swe_bench_dataset() -> Dict:
    """Legacy function for compatibility."""
    return {
        "type": "patch_evaluation", 
        "problems": get_swe_bench_problems(),
        "info": get_dataset_info()
    }