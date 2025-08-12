import json
import re
import requests
from typing import Dict, Any, List

def evaluate_with_real_tests(response: str, problems: List[Dict]) -> Dict[str, Any]:
    """Evaluate response against real HumanEval test cases."""
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
        "errors": []
    }
    
    solutions = parse_solutions(response)
    total_problems = len(problems)
    passed_tests = 0
    
    for i, problem in enumerate(problems):
        task_id = problem["task_id"]
        test_code = problem["test"]
        
        # Find corresponding solution
        solution_code = None
        if i < len(solutions) and "solution" in solutions[i]:
            solution_code = solutions[i]["solution"]
        elif len(solutions) == 1 and "solution" in solutions[0]:
            # Single solution for all problems
            solution_code = solutions[0]["solution"]
        
        if not solution_code:
            details["test_results"].append({
                "task_id": task_id,
                "passed": False,
                "error": "No solution provided"
            })
            continue
            
        # Execute the test
        try:
            # Combine problem prompt with solution
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
                "error": str(e)
            })
    
    # Calculate scores based on test results
    correctness_score = (passed_tests / total_problems * 100) if total_problems > 0 else 0
    scores["correctness"] = correctness_score
    scores["overall_score"] = correctness_score * 0.8 + 10  # Base score for attempt
    
    # Add feedback
    if passed_tests == total_problems:
        details["feedback"].append("Perfect! All test cases passed.")
    elif passed_tests > 0:
        details["feedback"].append(f"Good progress: {passed_tests}/{total_problems} tests passed.")
    else:
        details["feedback"].append("No test cases passed. Review the solution logic.")
    
    return {
        "scores": scores,
        "details": details,
        "passed": correctness_score >= 70
    }

def evaluate_human_eval(response: str, expected: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate HumanEval style coding response using actual test execution.
    """
    scores = {
        "correctness": 0,
        "efficiency": 0,
        "code_quality": 0,
        "edge_case_handling": 0,
        "overall_score": 0
    }
    
    # Try to execute against real HumanEval problems if available
    if "problems" in expected:
        try:
            from scenarios.human_eval.dataset import execute_test
            return evaluate_with_real_tests(response, expected["problems"])
        except ImportError:
            pass
    
    details = {
        "problem_scores": [],
        "feedback": [],
        "solutions_submitted": [],
        "test_results": [],
        "errors": []
    }
    
    try:
        # Parse response - could be single solution or multiple
        solutions = parse_solutions(response)
        
        if not solutions:
            details["errors"].append("No valid solutions found in response")
            return {
                "scores": scores,
                "details": details,
                "passed": False
            }
        
        # Evaluate each solution
        total_score = 0
        max_total_score = 0
        
        for solution in solutions:
            problem_id = solution.get("problem_id")
            if not problem_id:
                continue
                
            # Find expected criteria for this problem
            problem_expected = next(
                (p for p in expected["problems"] if p["id"] == problem_id), 
                None
            )
            
            if not problem_expected:
                continue
                
            problem_score = evaluate_single_solution(solution, problem_expected)
            max_problem_score = problem_expected["max_score"]
            
            total_score += problem_score
            max_total_score += max_problem_score
            
            details["problem_scores"].append({
                "problem_id": problem_id,
                "title": problem_expected["title"],
                "score": problem_score,
                "max_score": max_problem_score,
                "solution_submitted": bool(solution.get("solution"))
            })
            
            details["solutions_submitted"].append(solution)
        
        # Calculate component scores
        if max_total_score > 0:
            score_ratio = total_score / max_total_score
            
            # Distribute score across components based on expected scoring
            scoring_weights = expected.get("scoring", {
                "correctness": 60,
                "efficiency": 20, 
                "code_quality": 10,
                "edge_case_handling": 10
            })
            
            total_weight = sum(scoring_weights.values())
            for component, weight in scoring_weights.items():
                scores[component] = score_ratio * 100 * (weight / total_weight)
        
        # Overall score
        scores["overall_score"] = (
            scores["correctness"] * 0.6 +
            scores["efficiency"] * 0.2 +
            scores["code_quality"] * 0.1 +
            scores["edge_case_handling"] * 0.1
        )
        
        # Generate feedback
        details["feedback"] = generate_coding_feedback(scores, details["problem_scores"])
        
    except Exception as e:
        details["errors"].append(f"Evaluation error: {str(e)}")
        scores["overall_score"] = 0
        
    return {
        "scores": scores,
        "details": details,
        "passed": scores["overall_score"] >= expected.get("passing_threshold", 70)
    }

def parse_solutions(response: str) -> List[Dict[str, Any]]:
    """Parse solutions from response text."""
    solutions = []
    
    # Try to parse as JSON first
    try:
        if response.strip().startswith('['):
            # Multiple solutions
            solutions = json.loads(response)
        elif response.strip().startswith('{'):
            # Single solution
            solutions = [json.loads(response)]
    except json.JSONDecodeError:
        pass
    
    # If JSON parsing failed, try to extract JSON objects from text
    if not solutions:
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, response, re.DOTALL)
        
        for match in matches:
            try:
                solution = json.loads(match)
                if "problem_id" in solution:
                    solutions.append(solution)
            except json.JSONDecodeError:
                continue
    
    # If still no solutions, try to extract code blocks
    if not solutions:
        code_blocks = re.findall(r'```python\n(.*?)\n```', response, re.DOTALL)
        for i, code in enumerate(code_blocks):
            solutions.append({
                "problem_id": f"problem_{i+1}",
                "solution": code,
                "analysis": "Code extracted from markdown",
                "approach": "Code block"
            })
    
    return solutions

def evaluate_single_solution(solution: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """Evaluate a single solution against expected criteria."""
    score = 0
    max_score = expected["max_score"]
    
    # Check if solution code is provided
    solution_code = solution.get("solution", "")
    if not solution_code:
        return 0
    
    # Evaluate different aspects
    correctness_score = evaluate_correctness(solution_code, solution, expected)
    efficiency_score = evaluate_efficiency(solution, expected)
    quality_score = evaluate_code_quality(solution_code, solution)
    edge_case_score = evaluate_edge_cases(solution, expected)
    
    # Weight the scores
    score = (
        correctness_score * 0.6 +
        efficiency_score * 0.2 +
        quality_score * 0.1 +
        edge_case_score * 0.1
    ) * max_score / 100
    
    return min(score, max_score)

def evaluate_correctness(code: str, solution: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """Evaluate correctness of the solution."""
    score = 50  # Base score for having a solution
    
    problem_id = expected["id"]
    
    # Check if function signature is correct
    expected_func_name = extract_function_name(expected.get("expected_approach", ""))
    if expected_func_name and expected_func_name in code:
        score += 20
    
    # Check for key algorithmic elements
    if problem_id == "problem_1":  # Two Sum
        if "dict" in code or "{" in code or "hash" in code.lower():
            score += 20
        if "enumerate" in code or "range" in code:
            score += 10
    elif problem_id == "problem_2":  # Palindrome
        if "lower" in code or "upper" in code:
            score += 15
        if "reverse" in code or "[::-1]" in code or "two" in solution.get("approach", "").lower():
            score += 15
    elif problem_id == "problem_3":  # Fibonacci  
        if "for" in code or "while" in code:
            score += 15
        if not "recursion" in solution.get("approach", "").lower():  # Prefer iterative
            score += 15
    elif problem_id == "problem_4":  # Binary Search
        if "left" in code and "right" in code and "mid" in code:
            score += 20
        if "while" in code:
            score += 10
    elif problem_id == "problem_5":  # Valid Parentheses
        if "stack" in code.lower() or "[]" in code:
            score += 20
        if "push" in code.lower() or "pop" in code.lower() or "append" in code:
            score += 10
    
    return min(100, score)

def evaluate_efficiency(solution: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """Evaluate efficiency of the solution."""
    score = 60  # Base score
    
    time_complexity = solution.get("time_complexity", "").lower()
    space_complexity = solution.get("space_complexity", "").lower()
    expected_time = expected.get("optimal_complexity", {}).get("time", "").lower()
    
    # Check time complexity
    if expected_time and expected_time in time_complexity:
        score += 30
    elif "o(n)" in time_complexity and ("o(n^2)" not in time_complexity):
        score += 20
    elif "o(log" in time_complexity:
        score += 25
    
    # Check space complexity awareness
    if space_complexity:
        score += 10
    
    return min(100, score)

def evaluate_code_quality(code: str, solution: Dict[str, Any]) -> float:
    """Evaluate code quality."""
    score = 50  # Base score
    
    # Check for good variable names
    if any(name in code for name in ["left", "right", "target", "result", "stack"]):
        score += 10
    
    # Check for proper structure
    if "def " in code and "return" in code:
        score += 15
    
    # Check for comments or documentation
    if "#" in code or '"""' in code or "'''" in code:
        score += 10
    
    # Check analysis quality
    analysis = solution.get("analysis", "")
    if len(analysis) > 50:
        score += 10
    
    # Check approach explanation
    approach = solution.get("approach", "")
    if len(approach) > 50:
        score += 5
    
    return min(100, score)

def evaluate_edge_cases(solution: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """Evaluate edge case handling."""
    score = 60  # Base score
    
    code = solution.get("solution", "")
    analysis = solution.get("analysis", "").lower()
    approach = solution.get("approach", "").lower()
    
    # Check for edge case awareness in text
    edge_keywords = ["edge", "empty", "null", "zero", "single", "boundary"]
    for keyword in edge_keywords:
        if keyword in analysis or keyword in approach:
            score += 5
    
    # Problem-specific edge case checks
    problem_id = expected["id"]
    
    if problem_id == "problem_2":  # Palindrome
        if "empty" in analysis or "case" in analysis:
            score += 10
    elif problem_id == "problem_4":  # Binary Search
        if "empty" in analysis or "not found" in analysis:
            score += 10
    elif problem_id == "problem_5":  # Valid Parentheses
        if "empty" in analysis or "unmatched" in analysis:
            score += 10
    
    return min(100, score)

def extract_function_name(text: str) -> str:
    """Extract function name from text."""
    words = text.split()
    for word in words:
        if "_" in word and word.islower():
            return word
    return ""

def generate_coding_feedback(scores: Dict[str, float], problem_scores: List[Dict]) -> List[str]:
    """Generate feedback for coding evaluation."""
    feedback = []
    
    if scores["overall_score"] >= 90:
        feedback.append("Excellent coding performance!")
    elif scores["overall_score"] >= 70:
        feedback.append("Good coding skills with room for improvement.")
    else:
        feedback.append("Coding skills need significant improvement.")
    
    # Problem-specific feedback
    for problem_score in problem_scores:
        if not problem_score["solution_submitted"]:
            feedback.append(f"No solution provided for {problem_score['title']}")
        elif problem_score["score"] < problem_score["max_score"] * 0.6:
            feedback.append(f"Solution for {problem_score['title']} needs improvement")
    
    # Component feedback
    if scores["correctness"] < 70:
        feedback.append("Focus on correctness - ensure solutions work for all test cases.")
    
    if scores["efficiency"] < 70:
        feedback.append("Improve algorithmic efficiency - consider time and space complexity.")
    
    if scores["code_quality"] < 70:
        feedback.append("Enhance code quality - use better variable names and structure.")
    
    if scores["edge_case_handling"] < 70:
        feedback.append("Better handle edge cases and boundary conditions.")
    
    return feedback