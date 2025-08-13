import json
import re
from typing import Dict, Any, List

def evaluate_customer_support(response: str, expected: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optimized customer support evaluation focusing on practical response quality.
    """
    scores = {
        "response_quality": 0,
        "professionalism": 0, 
        "problem_resolution": 0,
        "api_awareness": 0,
        "overall_score": 0
    }
    
    details = {
        "feedback": [],
        "content_analysis": {},
        "errors": []
    }
    
    try:
        # Normalize response for analysis
        response_lower = response.lower()
        
        # Evaluate response quality
        scores["response_quality"] = evaluate_response_quality_optimized(response, response_lower)
        
        # Evaluate professionalism
        scores["professionalism"] = evaluate_professionalism(response_lower)
        
        # Evaluate problem resolution approach
        scores["problem_resolution"] = evaluate_problem_resolution(response_lower)
        
        # Evaluate API awareness and usage intent
        scores["api_awareness"] = evaluate_api_awareness(response_lower)
        
        # Calculate weighted overall score
        scores["overall_score"] = (
            scores["response_quality"] * 0.3 +
            scores["professionalism"] * 0.25 +
            scores["problem_resolution"] * 0.3 +
            scores["api_awareness"] * 0.15
        )
        
        # Store analysis details
        details["content_analysis"] = analyze_content_elements(response, response_lower)
        
        # Generate feedback
        details["feedback"] = generate_customer_support_feedback(scores, details["content_analysis"])
        
    except Exception as e:
        details["errors"].append(f"Evaluation error: {str(e)}")
        scores["overall_score"] = 0
    
    return {
        "scores": scores,
        "details": details,
        "passed": scores["overall_score"] >= 60  # Reasonable threshold
    }

def evaluate_response_quality_optimized(response: str, response_lower: str) -> float:
    """Evaluate overall response quality."""
    score = 60  # Base score
    
    # Length appropriateness (not too short, not too verbose)
    if 100 <= len(response) <= 1000:
        score += 15
    elif 50 <= len(response) <= 1500:
        score += 10
    elif len(response) < 50:
        score -= 20
    
    # Structure and organization
    structure_indicators = ["dear", "thank you", "best regards", "sincerely", "subject:"]
    structure_score = sum(5 for indicator in structure_indicators if indicator in response_lower)
    score += min(structure_score, 15)
    
    # Clarity and coherence
    clarity_indicators = ["please", "help", "assist", "resolve", "understand"]
    clarity_score = sum(2 for indicator in clarity_indicators if indicator in response_lower)
    score += min(clarity_score, 10)
    
    return min(score, 100)

def evaluate_professionalism(response_lower: str) -> float:
    """Evaluate professional tone and language."""
    score = 70  # Base score
    
    # Professional greetings and closings
    professional_terms = ["dear", "thank you", "appreciate", "regards", "assistance"]
    prof_score = sum(4 for term in professional_terms if term in response_lower)
    score += min(prof_score, 20)
    
    # Positive language
    positive_terms = ["happy", "pleased", "glad", "welcome", "help"]
    pos_score = sum(2 for term in positive_terms if term in response_lower)
    score += min(pos_score, 10)
    
    return min(score, 100)

def evaluate_problem_resolution(response_lower: str) -> float:
    """Evaluate problem-solving approach."""
    score = 50  # Base score
    
    # Solution-oriented language
    solution_terms = ["resolve", "fix", "solution", "help", "assist", "support"]
    solution_score = sum(6 for term in solution_terms if term in response_lower)
    score += min(solution_score, 30)
    
    # Information gathering
    info_gathering = ["provide", "details", "information", "describe", "explain"]
    info_score = sum(4 for term in info_gathering if term in response_lower)
    score += min(info_score, 20)
    
    return min(score, 100)

def evaluate_api_awareness(response_lower: str) -> float:
    """Evaluate API awareness and usage intent."""
    score = 30  # Base score for responses without API usage
    
    # API-related terms
    api_terms = ["api", "ticket", "system", "database", "fetch", "access"]
    api_mentions = sum(1 for term in api_terms if term in response_lower)
    
    if api_mentions > 0:
        score += 30  # Bonus for API awareness
    
    # Technical approach indicators
    tech_terms = ["endpoint", "request", "response", "data", "retrieve"]
    tech_score = sum(8 for term in tech_terms if term in response_lower)
    score += min(tech_score, 40)
    
    return min(score, 100)

def analyze_content_elements(response: str, response_lower: str) -> Dict[str, Any]:
    """Analyze content elements present in response."""
    return {
        "mentions_ticket_id": "ticket" in response_lower and ("id" in response_lower or "#" in response),
        "mentions_warranty": "warranty" in response_lower,
        "has_professional_greeting": any(greeting in response_lower for greeting in ["dear", "hello", "hi"]),
        "has_professional_closing": any(closing in response_lower for closing in ["regards", "sincerely", "thank you"]),
        "asks_for_details": any(phrase in response_lower for phrase in ["provide", "details", "information", "describe"]),
        "mentions_next_steps": any(phrase in response_lower for phrase in ["next step", "follow", "proceed", "continue"]),
        "response_length": len(response),
        "word_count": len(response.split())
    }

def generate_customer_support_feedback(scores: Dict[str, float], content_analysis: Dict[str, Any]) -> List[str]:
    """Generate concise, actionable feedback."""
    feedback = []
    overall_score = scores["overall_score"]
    
    if overall_score >= 80:
        feedback.append("🎯 Excellent customer support response!")
    elif overall_score >= 65:
        feedback.append("✅ Good customer support with room for improvement.")
    else:
        feedback.append("📈 Customer support response needs improvement.")
    
    # Component-specific feedback
    if scores["response_quality"] < 70:
        feedback.append("📝 Improve response structure and clarity.")
    
    if scores["professionalism"] < 70:
        feedback.append("💼 Enhance professional tone and courtesy.")
    
    if scores["problem_resolution"] < 70:
        feedback.append("🔧 Focus more on problem-solving approach.")
    
    if scores["api_awareness"] < 50:
        feedback.append("🔗 Consider using available APIs for better support.")
    
    # Content-specific feedback
    if not content_analysis.get("mentions_warranty", False):
        feedback.append("📋 Include warranty policy information when relevant.")
    
    if not content_analysis.get("asks_for_details", False):
        feedback.append("❓ Ask for more details to better assist the customer.")
    
    return feedback

# Backward compatibility
def evaluate(output: str, expected: dict) -> dict:
    return evaluate_customer_support(output, expected)