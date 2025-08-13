import json
import re
from typing import Dict, Any, List

def evaluate_human_eval(response: str, expected: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate HumanEval style coding response using actual test execution.
    """
    # Always use real test execution if problems are available
    if "problems" in expected:
        return evaluate_with_real_tests(response, expected["problems"])
    
    # Minimal fallback for legacy format
    return {
        "scores": {"correctness": 0, "efficiency": 20, "code_quality": 20, "edge_case_handling": 20, "overall_score": 0},
        "details": {"problem_scores": [], "feedback": ["No problems provided for evaluation"], "test_results": [], "errors": []},
        "passed": False
    }

def evaluate_with_real_tests(response: str, problems: List[Dict]) -> Dict[str, Any]:
    """Evaluate response against real HumanEval test cases with optimized solution matching."""
    from scenarios.human_eval.dataset import execute_test
    
    scores = {
        "correctness": 0,
        "efficiency": 0,
        "code_quality": 0,
        "edge_case_handling": 0,
        "overall_score": 0
    }
    
    details = {
        "problem_scores": [],
        "feedback": [],
        "test_results": [],
        "errors": [],
        "solutions_found": 0
    }
    
    solutions = parse_solutions_optimized(response)
    total_problems = len(problems)
    passed_tests = 0
    solutions_attempted = 0
    
    # Test each problem
    for i, problem in enumerate(problems):
        task_id = problem["task_id"]
        test_code = problem["test"]
        entry_point = problem.get("entry_point", "")
        
        solution_code = find_best_solution_match(solutions, entry_point, i)
        
        if not solution_code:
            details["test_results"].append({
                "task_id": task_id,
                "passed": False,
                "result": "No solution provided"
            })
            continue
        
        solutions_attempted += 1
        
        # Execute the test
        try:
            full_code = problem["prompt"] + "\n" + solution_code
            test_result = execute_test(full_code, test_code)
            
            details["test_results"].append({
                "task_id": task_id,
                "passed": test_result["passed"],
                "result": test_result["result"]
            })
            
            if test_result["passed"]:
                passed_tests += 1
                
        except Exception as e:
            details["test_results"].append({
                "task_id": task_id,
                "passed": False,
                "result": str(e)
            })
    
    details["solutions_found"] = len(solutions)
    
    # Calculate scores
    correctness_score = (passed_tests / total_problems * 100) if total_problems > 0 else 0
    scores["correctness"] = correctness_score
    
    # Quality assessment
    effort_score = min((solutions_attempted / total_problems * 30), 30) if total_problems > 0 else 0
    quality_score = assess_code_quality(solutions)
    efficiency_score = assess_efficiency(solutions, details["test_results"])
    edge_case_score = assess_edge_cases(solutions, details["test_results"])
    
    scores["code_quality"] = quality_score
    scores["efficiency"] = efficiency_score
    scores["edge_case_handling"] = edge_case_score
    
    # Overall score with partial credit
    base_score = correctness_score * 0.6
    partial_credit = effort_score * 0.2 + quality_score * 0.1 + edge_case_score * 0.1
    scores["overall_score"] = min(base_score + partial_credit, 100)
    
    # Generate feedback
    details["feedback"] = generate_optimized_feedback(passed_tests, total_problems, len(solutions), solutions_attempted)
    
    return {
        "scores": scores,
        "details": details,
        "passed": correctness_score >= 10  # Lower threshold for partial credit
    }

def find_best_solution_match(solutions: List[Dict], entry_point: str, index: int) -> str:
    """Find the best matching solution for a problem."""
    if not solutions:
        return None
    
    # Strategy 1: Try to find solution by index
    if index < len(solutions) and "solution" in solutions[index]:
        return solutions[index]["solution"]
    
    # Strategy 2: Look for solution that contains the expected function name
    if entry_point:
        for sol in solutions:
            if entry_point in sol.get("solution", ""):
                return sol["solution"]
    
    # Strategy 3: Use first available solution
    if solutions and "solution" in solutions[0]:
        return solutions[0]["solution"]
    
    return None

def parse_solutions_optimized(response: str) -> List[Dict]:
    """Parse solutions with streamlined, efficient parsing."""
    solutions = []
    
    # Extract Python code blocks (most common format)
    code_patterns = [
        r'```python\s*\n(.*?)\n```',  # Python code blocks
        r'```\s*\n(def\s+.*?)\n```',  # Generic code blocks with functions
        r'(?:^|\n)(def\s+\w+.*?)(?=\n(?:def|\Z))'  # Function definitions
    ]
    
    for pattern in code_patterns:
        matches = re.findall(pattern, response, re.DOTALL | re.MULTILINE)
        for i, code in enumerate(matches):
            if 'def ' in code and len(code.strip()) > 20:  # Minimum viable function
                solutions.append({
                    "problem_id": f"HumanEval/{i}",
                    "solution": code.strip()
                })
        if solutions:  # Stop at first successful pattern
            break
    
    # Fallback: extract any function-like content
    if not solutions:
        func_matches = re.findall(r'def\s+\w+.*?(?=\ndef|\Z)', response, re.DOTALL)
        for i, func in enumerate(func_matches):
            if 'return' in func or len(func.split('\n')) > 2:
                solutions.append({
                    "problem_id": f"HumanEval/{i}",
                    "solution": func.strip()
                })
    
    return solutions

def assess_code_quality(solutions: List[Dict]) -> float:
    """Assess overall code quality of solutions."""
    if not solutions:
        return 0
    
    score = 0
    total_solutions = len(solutions)
    
    for sol in solutions:
        code = sol.get("solution", "")
        # Check for proper function structure
        if "def " in code and "return" in code:
            score += 20
        # Check for reasonable length (not trivial)
        if len(code) > 50:
            score += 10
        # Check for good practices
        if any(practice in code for practice in ["enumerate", "zip", "range"]):
            score += 5
    
    return min(score / total_solutions, 20) if total_solutions > 0 else 0

def assess_efficiency(solutions: List[Dict], test_results: List[Dict]) -> float:
    """Assess efficiency based on solution characteristics."""
    base_score = 60
    
    # Bonus for successful executions
    passed_count = sum(1 for result in test_results if result.get("passed", False))
    if passed_count > 0:
        base_score += min(passed_count * 10, 20)
    
    return min(base_score, 100)

def assess_edge_cases(solutions: List[Dict], test_results: List[Dict]) -> float:
    """Assess edge case handling."""
    base_score = 60
    
    # Penalty for runtime errors
    error_count = sum(1 for result in test_results if "Error" in result.get("result", ""))
    base_score -= min(error_count * 5, 30)
    
    return max(base_score, 20)

def generate_optimized_feedback(passed_tests: int, total_problems: int, solutions_found: int, solutions_attempted: int) -> List[str]:
    """Generate concise, actionable feedback."""
    feedback = []
    
    if passed_tests == total_problems:
        feedback.append("🎉 Perfect! All test cases passed.")
    elif passed_tests > total_problems * 0.5:
        feedback.append(f"✅ Good progress: {passed_tests}/{total_problems} tests passed.")
    elif passed_tests > 0:
        feedback.append(f"⚠️ Some progress: {passed_tests}/{total_problems} tests passed.")
    else:
        feedback.append("❌ No test cases passed. Review solution logic.")
    
    feedback.append(f"📊 Solutions found: {solutions_found}, Attempted: {solutions_attempted}")
    
    return feedback