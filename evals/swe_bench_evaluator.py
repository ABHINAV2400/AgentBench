import json
import re
import requests
from typing import Dict, Any, List

def evaluate_swe_bench(response: str, expected: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate SWE-bench style software engineering response.
    """
    scores = {
        "code_quality": 0,
        "test_coverage": 0,
        "issue_resolution": 0,
        "regression_prevention": 0,
        "documentation": 0,
        "overall_score": 0
    }
    
    details = {
        "issue_scores": [],
        "feedback": [],
        "changes_made": [],
        "tests_status": "unknown",
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
                    "analysis": response,
                    "solution": "",
                    "changes": [],
                    "verification": ""
                }
        else:
            parsed_response = response
            
        analysis = parsed_response.get("analysis", "")
        solution = parsed_response.get("solution", "")
        changes = parsed_response.get("changes", [])
        verification = parsed_response.get("verification", "")
        
        # Evaluate each issue
        total_issue_score = 0
        max_issue_score = 0
        
        for issue in expected["issues"]:
            issue_score = evaluate_single_issue(parsed_response, issue)
            max_issue_score += issue["points"]
            total_issue_score += issue_score
            
            details["issue_scores"].append({
                "issue_id": issue["id"],
                "title": issue["title"], 
                "score": issue_score,
                "max_score": issue["points"]
            })
        
        # Calculate component scores
        scores["issue_resolution"] = (total_issue_score / max_issue_score * 100) if max_issue_score > 0 else 0
        
        # Code quality based on analysis depth and solution approach
        code_quality_score = evaluate_code_quality(analysis, solution, changes)
        scores["code_quality"] = code_quality_score
        
        # Test coverage based on mentioned testing approach
        test_coverage_score = evaluate_test_coverage(parsed_response, expected)
        scores["test_coverage"] = test_coverage_score
        
        # Regression prevention based on verification approach
        regression_score = evaluate_regression_prevention(verification, changes)
        scores["regression_prevention"] = regression_score
        
        # Documentation based on code comments and explanations
        documentation_score = evaluate_documentation(parsed_response)
        scores["documentation"] = documentation_score
        
        # Overall score calculation
        scores["overall_score"] = (
            scores["code_quality"] * 0.25 +
            scores["test_coverage"] * 0.2 +
            scores["issue_resolution"] * 0.3 +
            scores["regression_prevention"] * 0.15 +
            scores["documentation"] * 0.1
        )
        
        # Generate feedback
        details["feedback"] = generate_swe_feedback(scores, details["issue_scores"])
        details["changes_made"] = changes
        
    except Exception as e:
        details["errors"].append(f"Evaluation error: {str(e)}")
        scores["overall_score"] = 0
        
    return {
        "scores": scores,
        "details": details,
        "passed": scores["overall_score"] >= 70
    }

def evaluate_single_issue(response: Dict[str, Any], issue: Dict[str, Any]) -> float:
    """Evaluate response against a single issue."""
    score = 0
    max_score = issue["points"]
    
    analysis = response.get("analysis", "").lower()
    solution = response.get("solution", "").lower()
    changes = [str(change).lower() for change in response.get("changes", [])]
    
    issue_title = issue["title"].lower()
    issue_desc = issue["description"].lower()
    expected_changes = [change.lower() for change in issue.get("expected_changes", [])]
    success_criteria = [criterion.lower() for criterion in issue.get("success_criteria", [])]
    
    # Check if issue is understood (analysis mentions key terms)
    key_terms = extract_key_terms(issue_title + " " + issue_desc)
    understanding_score = 0
    for term in key_terms:
        if term in analysis or term in solution:
            understanding_score += 1
    
    if key_terms:
        score += (understanding_score / len(key_terms)) * (max_score * 0.3)
    
    # Check if expected changes are addressed
    changes_text = " ".join(changes)
    change_score = 0
    for expected_change in expected_changes:
        if any(expected_change in change for change in changes) or expected_change in changes_text:
            change_score += 1
    
    if expected_changes:
        score += (change_score / len(expected_changes)) * (max_score * 0.4)
    
    # Check success criteria
    criteria_score = 0
    all_text = analysis + " " + solution + " " + changes_text
    for criterion in success_criteria:
        if criterion in all_text:
            criteria_score += 1
    
    if success_criteria:
        score += (criteria_score / len(success_criteria)) * (max_score * 0.3)
    
    return min(score, max_score)

def extract_key_terms(text: str) -> List[str]:
    """Extract key technical terms from text."""
    terms = []
    words = text.split()
    
    # Look for function names, technical terms, etc.
    for word in words:
        word = word.strip('.,!?():')
        if len(word) > 2 and (
            word.endswith('_function') or
            word.endswith('function') or
            word in ['sqrt', 'validation', 'error', 'test', 'optimize', 'divide'] or
            word.startswith('test_')
        ):
            terms.append(word)
    
    return list(set(terms))

def evaluate_code_quality(analysis: str, solution: str, changes: List) -> float:
    """Evaluate code quality based on analysis and solution."""
    score = 60  # Base score
    
    # Check for good analysis
    quality_indicators = [
        "understand", "identify", "root cause", "structure", "pattern", 
        "maintainable", "clean", "style", "refactor"
    ]
    
    for indicator in quality_indicators:
        if indicator in analysis.lower() or indicator in solution.lower():
            score += 4
    
    # Check for systematic approach
    if "step" in solution.lower() or "approach" in solution.lower():
        score += 5
    
    # Check for consideration of existing code
    if "existing" in solution.lower() or "current" in solution.lower():
        score += 5
    
    return min(100, score)

def evaluate_test_coverage(response: Dict[str, Any], expected: Dict[str, Any]) -> float:
    """Evaluate test coverage approach."""
    score = 50  # Base score
    
    verification = response.get("verification", "").lower()
    changes = " ".join(str(change) for change in response.get("changes", [])).lower()
    
    # Check for test mentions
    test_keywords = ["test", "verify", "pytest", "assert", "coverage", "edge case"]
    for keyword in test_keywords:
        if keyword in verification or keyword in changes:
            score += 8
    
    # Check for specific test types mentioned
    if "new test" in changes or "add test" in changes:
        score += 10
    
    # Check for edge case consideration
    if "edge case" in verification or "negative" in verification:
        score += 10
    
    return min(100, score)

def evaluate_regression_prevention(verification: str, changes: List) -> float:
    """Evaluate regression prevention approach."""
    score = 60  # Base score
    
    verification_lower = verification.lower()
    changes_text = " ".join(str(change) for change in changes).lower()
    
    # Check for existing test mentions
    if "existing test" in verification_lower or "all tests" in verification_lower:
        score += 15
    
    # Check for backward compatibility concerns
    if "compatible" in verification_lower or "break" in verification_lower:
        score += 10
    
    # Check for verification approach
    if "verify" in verification_lower or "ensure" in verification_lower:
        score += 10
    
    return min(100, score)

def evaluate_documentation(response: Dict[str, Any]) -> float:
    """Evaluate documentation quality."""
    score = 50  # Base score
    
    analysis = response.get("analysis", "")
    solution = response.get("solution", "")
    
    # Check for clear explanations
    if len(analysis) > 100:  # Substantial analysis
        score += 20
    
    # Check for structured response
    if "step" in solution.lower() or numbered_steps_present(solution):
        score += 15
    
    # Check for technical accuracy indicators
    tech_terms = ["function", "parameter", "return", "exception", "validation"]
    for term in tech_terms:
        if term in analysis.lower() or term in solution.lower():
            score += 3
    
    return min(100, score)

def numbered_steps_present(text: str) -> bool:
    """Check if text contains numbered steps."""
    return bool(re.search(r'\b\d+\.\s', text))

def generate_swe_feedback(scores: Dict[str, float], issue_scores: List[Dict]) -> List[str]:
    """Generate feedback for SWE-bench evaluation."""
    feedback = []
    
    if scores["overall_score"] >= 90:
        feedback.append("Excellent software engineering approach!")
    elif scores["overall_score"] >= 70:
        feedback.append("Good software engineering skills with room for improvement.")
    else:
        feedback.append("Software engineering approach needs significant improvement.")
    
    # Issue-specific feedback
    for issue_score in issue_scores:
        if issue_score["score"] < issue_score["max_score"] * 0.6:
            feedback.append(f"Issue '{issue_score['title']}' not adequately addressed.")
    
    # Component feedback
    if scores["code_quality"] < 70:
        feedback.append("Improve code quality analysis and solution design.")
    
    if scores["test_coverage"] < 70:
        feedback.append("Add more comprehensive testing approach.")
    
    if scores["regression_prevention"] < 70:
        feedback.append("Better consider existing functionality and regression prevention.")
    
    if scores["documentation"] < 70:
        feedback.append("Provide more detailed analysis and documentation.")
    
    return feedback