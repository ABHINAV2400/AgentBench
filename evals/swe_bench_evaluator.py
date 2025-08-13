import json
import re
from typing import Dict, Any, List

def evaluate_swe_bench(response: str, expected: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optimized SWE-bench evaluation with streamlined logic.
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
        # Parse response with flexible handling
        parsed_response = parse_response_flexible(response)
        
        # Extract and normalize text components
        analysis = normalize_text(parsed_response.get("analysis", ""))
        solution = normalize_text(parsed_response.get("solution", ""))
        changes = parsed_response.get("changes", [])
        verification = normalize_text(parsed_response.get("verification", ""))
        
        # Evaluate single SWE-bench problem
        if "instance_id" in expected:
            issue_score = evaluate_swe_problem(parsed_response, expected, analysis, solution)
            
            details["issue_scores"].append({
                "issue_id": expected["instance_id"],
                "title": f"SWE-bench problem {expected['instance_id']}", 
                "score": issue_score,
                "max_score": 100
            })
            
            scores["issue_resolution"] = issue_score
        
        # Assess component scores efficiently
        scores["code_quality"] = assess_code_quality(analysis, solution, changes)
        scores["test_coverage"] = assess_test_coverage(verification, changes)
        scores["regression_prevention"] = assess_regression_prevention(verification)
        scores["documentation"] = assess_documentation(analysis, solution)
        
        # Calculate weighted overall score
        scores["overall_score"] = (
            scores["code_quality"] * 0.25 +
            scores["test_coverage"] * 0.2 +
            scores["issue_resolution"] * 0.3 +
            scores["regression_prevention"] * 0.15 +
            scores["documentation"] * 0.1
        )
        
        # Store changes for details
        details["changes_made"] = changes if isinstance(changes, list) else [str(changes)]
        
        # Generate concise feedback
        details["feedback"] = generate_feedback(scores)
        
    except Exception as e:
        details["errors"].append(f"Evaluation error: {str(e)}")
        scores["overall_score"] = 0
        
    return {
        "scores": scores,
        "details": details,
        "passed": scores["overall_score"] >= 50  # Reasonable threshold
    }

def parse_response_flexible(response: str) -> Dict[str, Any]:
    """Parse response with flexible JSON extraction."""
    if isinstance(response, dict):
        return response
    
    # Try direct JSON parsing
    try:
        if response.strip().startswith('{'):
            return json.loads(response)
    except json.JSONDecodeError:
        pass
    
    # Extract JSON from markdown or text
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    
    # Fallback to treating entire response as analysis
    return {
        "analysis": response,
        "solution": "",
        "changes": [],
        "verification": ""
    }

def normalize_text(text_input) -> str:
    """Normalize text input to string regardless of type."""
    if isinstance(text_input, dict):
        return " ".join(str(v) for v in text_input.values())
    elif isinstance(text_input, list):
        return " ".join(str(item) for item in text_input)
    else:
        return str(text_input)

def evaluate_swe_problem(response: Dict[str, Any], problem: Dict[str, Any], 
                        analysis: str, solution: str) -> float:
    """Evaluate response against SWE-bench problem."""
    score = 0
    
    problem_statement = problem.get("problem_statement", "").lower()
    instance_id = problem.get("instance_id", "")
    repo = problem.get("repo", "")
    
    # Check problem understanding (30 points)
    key_terms = extract_technical_terms(problem_statement)
    if key_terms:
        understanding_score = sum(1 for term in key_terms 
                                if term in analysis.lower() or term in solution.lower())
        score += min(understanding_score / len(key_terms) * 30, 30)
    
    # Check repository context (10 points)
    if repo and repo.lower() in analysis.lower():
        score += 10
    
    # Check for technical approach indicators (30 points)
    tech_indicators = ["fix", "modify", "update", "implement", "change", "resolve"]
    tech_score = sum(1 for indicator in tech_indicators 
                    if indicator in solution.lower())
    score += min(tech_score / len(tech_indicators) * 30, 30)
    
    # Check for structured approach (20 points)
    structure_indicators = ["step", "first", "then", "approach", "analyze"]
    if any(indicator in solution.lower() for indicator in structure_indicators):
        score += 20
    
    # Check for specific issue references (10 points)
    if instance_id:
        issue_numbers = re.findall(r'\d+', instance_id)
        if any(num in analysis or num in solution for num in issue_numbers):
            score += 10
    
    return min(score, 100)

def extract_technical_terms(text: str) -> List[str]:
    """Extract technical terms efficiently."""
    technical_keywords = [
        "error", "exception", "bug", "test", "function", "method", "class", 
        "import", "module", "api", "database", "server", "client", "config"
    ]
    
    words = text.lower().split()
    return [word for word in technical_keywords if word in words]

def assess_code_quality(analysis: str, solution: str, changes: List) -> float:
    """Assess code quality efficiently."""
    score = 60  # Base score
    
    # Check for quality indicators
    quality_indicators = ["clean", "maintainable", "refactor", "structure", "pattern"]
    score += sum(4 for indicator in quality_indicators 
                if indicator in analysis.lower() or indicator in solution.lower())
    
    # Check for systematic approach
    if "approach" in solution.lower() or "methodology" in solution.lower():
        score += 10
    
    return min(score, 100)

def assess_test_coverage(verification: str, changes: List) -> float:
    """Assess test coverage approach."""
    score = 50  # Base score
    
    verification_lower = verification.lower()
    
    # Check for test-related terms
    test_terms = ["test", "verify", "check", "validate", "assert"]
    score += sum(10 for term in test_terms if term in verification_lower)
    
    # Check for comprehensive testing approach
    if "comprehensive" in verification_lower or "thorough" in verification_lower:
        score += 15
    
    return min(score, 100)

def assess_regression_prevention(verification: str) -> float:
    """Assess regression prevention approach."""
    score = 60  # Base score
    
    verification_lower = verification.lower()
    
    # Check for regression awareness
    regression_terms = ["existing", "backward", "compatible", "regression", "break"]
    score += sum(8 for term in regression_terms if term in verification_lower)
    
    return min(score, 100)

def assess_documentation(analysis: str, solution: str) -> float:
    """Assess documentation quality."""
    score = 50  # Base score
    
    # Check for detailed analysis
    if len(analysis) > 100:
        score += 20
    
    # Check for clear solution description
    if len(solution) > 100:
        score += 20
    
    # Check for technical terminology
    if any(term in analysis.lower() for term in ["implementation", "architecture", "design"]):
        score += 10
    
    return min(score, 100)

def generate_feedback(scores: Dict[str, float]) -> List[str]:
    """Generate concise, actionable feedback."""
    feedback = []
    
    if scores["overall_score"] >= 80:
        feedback.append("✅ Excellent software engineering approach!")
    elif scores["overall_score"] >= 60:
        feedback.append("📈 Good approach with room for improvement.")
    else:
        feedback.append("📚 Software engineering approach needs improvement.")
    
    # Component-specific feedback
    if scores["issue_resolution"] < 60:
        feedback.append("🎯 Better address the specific problem requirements.")
    
    if scores["test_coverage"] < 60:
        feedback.append("🧪 Include more comprehensive testing strategy.")
    
    if scores["regression_prevention"] < 60:
        feedback.append("🛡️ Consider impact on existing functionality.")
    
    return feedback