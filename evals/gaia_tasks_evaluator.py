import json
import re
from typing import Dict, Any, List

def evaluate_gaia_tasks(response: str, expected: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate GAIA-style general assistant tasks.
    """
    scores = {
        "task_comprehension": 0,
        "tool_usage": 0,
        "reasoning_quality": 0,
        "accuracy": 0,
        "completeness": 0,
        "methodology": 0,
        "overall_score": 0
    }
    
    details = {
        "task_scores": [],
        "feedback": [],
        "steps_executed": [],
        "tools_used": [],
        "reasoning_analysis": {},
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
                    "task_analysis": response,
                    "approach": "",
                    "steps_taken": [],
                    "results": {},
                    "final_answer": response,
                    "confidence": 0.5,
                    "methodology": ""
                }
        else:
            parsed_response = response
        
        # Extract components
        task_analysis = parsed_response.get("task_analysis", "")
        approach = parsed_response.get("approach", "")
        steps_taken = parsed_response.get("steps_taken", [])
        results = parsed_response.get("results", {})
        final_answer = parsed_response.get("final_answer", "")
        confidence = parsed_response.get("confidence", 0.5)
        methodology = parsed_response.get("methodology", "")
        
        # Evaluate against expected tasks (assume single task evaluation for now)
        # In practice, you'd match the response to the specific task being evaluated
        task_evaluated = expected["tasks"][0]  # Simplified for demo
        
        # Evaluate components
        scores["task_comprehension"] = evaluate_task_comprehension(
            task_analysis, task_evaluated
        )
        
        scores["tool_usage"] = evaluate_tool_usage(
            steps_taken, results, task_evaluated
        )
        
        scores["reasoning_quality"] = evaluate_reasoning_quality(
            approach, methodology, steps_taken
        )
        
        scores["accuracy"] = evaluate_accuracy(
            final_answer, results, task_evaluated
        )
        
        scores["completeness"] = evaluate_completeness(
            steps_taken, task_evaluated
        )
        
        scores["methodology"] = evaluate_methodology(
            methodology, approach
        )
        
        # Calculate overall score
        weights = {
            "task_comprehension": 0.15,
            "tool_usage": 0.20,
            "reasoning_quality": 0.20,
            "accuracy": 0.25,
            "completeness": 0.15,
            "methodology": 0.05
        }
        
        scores["overall_score"] = sum(
            scores[component] * weight 
            for component, weight in weights.items()
        )
        
        # Store analysis details
        details["steps_executed"] = steps_taken
        details["tools_used"] = extract_tools_used(steps_taken)
        details["reasoning_analysis"] = {
            "approach_length": len(approach.split()) if approach else 0,
            "methodology_provided": bool(methodology),
            "confidence_stated": confidence
        }
        
        # Generate feedback
        details["feedback"] = generate_gaia_feedback(scores, parsed_response, task_evaluated)
        
    except Exception as e:
        details["errors"].append(f"Evaluation error: {str(e)}")
        scores["overall_score"] = 0
    
    return {
        "scores": scores,
        "details": details,
        "passed": scores["overall_score"] >= expected.get("passing_threshold", 75)
    }

def evaluate_task_comprehension(task_analysis: str, expected_task: Dict[str, Any]) -> float:
    """Evaluate understanding of the task."""
    score = 50  # Base score
    
    if not task_analysis:
        return 20
    
    task_description = expected_task["description"].lower()
    analysis_lower = task_analysis.lower()
    
    # Check for key elements mentioned in description
    key_terms = extract_key_task_terms(task_description)
    mentioned_terms = sum(1 for term in key_terms if term in analysis_lower)
    
    if key_terms:
        score += (mentioned_terms / len(key_terms)) * 30
    
    # Check for complexity awareness
    if "step" in analysis_lower or "complex" in analysis_lower:
        score += 10
    
    # Check for requirements understanding
    if "require" in analysis_lower or "need" in analysis_lower:
        score += 10
    
    return min(100, score)

def evaluate_tool_usage(steps_taken: List, results: Dict, expected_task: Dict[str, Any]) -> float:
    """Evaluate appropriate tool usage."""
    score = 40  # Base score
    
    expected_tools = set(expected_task.get("expected_tools", []))
    steps_text = " ".join(str(step) for step in steps_taken)
    results_text = " ".join(str(value) for value in results.values())
    
    # Check if expected tools are mentioned or used
    tools_used = set()
    for tool in expected_tools:
        if tool in steps_text.lower() or tool in results_text.lower():
            tools_used.add(tool)
    
    if expected_tools:
        tool_usage_ratio = len(tools_used) / len(expected_tools)
        score += tool_usage_ratio * 40
    
    # Bonus for multiple tools
    if len(tools_used) > 1:
        score += 10
    
    # Check for tool sequencing
    if len(steps_taken) >= len(expected_task.get("required_steps", [])):
        score += 10
    
    return min(100, score)

def evaluate_reasoning_quality(approach: str, methodology: str, steps_taken: List) -> float:
    """Evaluate quality of reasoning process."""
    score = 50  # Base score
    
    # Check approach quality
    if approach:
        if len(approach.split()) > 20:  # Substantial approach
            score += 15
        if "step" in approach.lower() or numbered_pattern(approach):
            score += 10
        if "because" in approach.lower() or "therefore" in approach.lower():
            score += 5
    
    # Check methodology explanation
    if methodology:
        if len(methodology.split()) > 10:
            score += 10
        if "method" in methodology.lower() or "approach" in methodology.lower():
            score += 5
    
    # Check logical flow in steps
    if len(steps_taken) >= 3:
        score += 5
    
    return min(100, score)

def evaluate_accuracy(final_answer: str, results: Dict, expected_task: Dict[str, Any]) -> float:
    """Evaluate accuracy against expected criteria."""
    score = 30  # Base score for attempting an answer
    
    if not final_answer:
        return 10
    
    success_criteria = expected_task.get("success_criteria", [])
    answer_lower = final_answer.lower()
    results_text = " ".join(str(value) for value in results.values()).lower()
    
    # Check against success criteria
    criteria_met = 0
    for criterion in success_criteria:
        criterion_lower = criterion.lower()
        if any(key_term in answer_lower or key_term in results_text 
               for key_term in extract_key_terms(criterion_lower)):
            criteria_met += 1
    
    if success_criteria:
        accuracy_ratio = criteria_met / len(success_criteria)
        score += accuracy_ratio * 50
    
    # Check for specific expected values/results
    task_id = expected_task.get("id", "")
    if task_id == "task_1":  # Tesla/Apple comparison
        if "2003" in answer_lower and "1976" in answer_lower:
            score += 10
        if "27" in answer_lower or "difference" in answer_lower:
            score += 5
    elif task_id == "task_3":  # Data processing  
        if "18.75" in answer_lower or "positive" in answer_lower:
            score += 10
        if "15" in answer_lower and "greater" in answer_lower:
            score += 5
    
    return min(100, score)

def evaluate_completeness(steps_taken: List, expected_task: Dict[str, Any]) -> float:
    """Evaluate completeness of task execution."""
    score = 40  # Base score
    
    required_steps = expected_task.get("required_steps", [])
    steps_text = " ".join(str(step) for step in steps_taken).lower()
    
    # Check if required steps are addressed
    steps_covered = 0
    for required_step in required_steps:
        step_keywords = extract_key_terms(required_step.lower())
        if any(keyword in steps_text for keyword in step_keywords):
            steps_covered += 1
    
    if required_steps:
        completeness_ratio = steps_covered / len(required_steps)
        score += completeness_ratio * 40
    
    # Bonus for comprehensive execution
    if len(steps_taken) >= len(required_steps):
        score += 10
    
    # Check for final conclusion/answer
    if steps_taken and any("result" in str(step).lower() or "answer" in str(step).lower() 
                          for step in steps_taken):
        score += 10
    
    return min(100, score)

def evaluate_methodology(methodology: str, approach: str) -> float:
    """Evaluate explanation of methodology."""
    score = 60  # Base score
    
    combined_text = (methodology + " " + approach).lower()
    
    # Check for methodology keywords
    method_keywords = ["method", "approach", "process", "procedure", "technique"]
    for keyword in method_keywords:
        if keyword in combined_text:
            score += 5
    
    # Check for explanation quality
    if len(combined_text.split()) > 30:
        score += 15
    
    # Check for reasoning explanations
    reasoning_keywords = ["because", "therefore", "since", "as", "due to"]
    for keyword in reasoning_keywords:
        if keyword in combined_text:
            score += 3
    
    return min(100, score)

def extract_key_task_terms(description: str) -> List[str]:
    """Extract key terms from task description."""
    # Remove common words and focus on meaningful terms
    words = description.split()
    key_terms = []
    
    skip_words = {"the", "and", "or", "to", "a", "an", "in", "on", "at", "by", "for"}
    
    for word in words:
        word = word.strip('.,!?():').lower()
        if len(word) > 3 and word not in skip_words:
            key_terms.append(word)
    
    return key_terms

def extract_key_terms(text: str) -> List[str]:
    """Extract key terms from text."""
    words = text.split()
    terms = []
    
    for word in words:
        word = word.strip('.,!?():').lower()
        if len(word) > 2 and word.isalpha():
            terms.append(word)
    
    return terms

def numbered_pattern(text: str) -> bool:
    """Check if text contains numbered steps."""
    return bool(re.search(r'\b\d+\.\s|\b\d+\)\s', text))

def extract_tools_used(steps: List) -> List[str]:
    """Extract tools mentioned in steps."""
    tools = []
    tool_names = [
        "search_knowledge", "get_weather", "calculate", "translate_text",
        "analyze_document", "handle_multi_step_task", "chain_reasoning", "process_data"
    ]
    
    steps_text = " ".join(str(step) for step in steps).lower()
    
    for tool in tool_names:
        if tool in steps_text:
            tools.append(tool)
    
    return tools

def generate_gaia_feedback(scores: Dict[str, float], response: Dict[str, Any], 
                          task: Dict[str, Any]) -> List[str]:
    """Generate feedback for GAIA evaluation."""
    feedback = []
    
    overall_score = scores["overall_score"]
    if overall_score >= 90:
        feedback.append("Excellent general assistant performance!")
    elif overall_score >= 75:
        feedback.append("Good assistant capabilities with room for improvement.")
    else:
        feedback.append("Assistant performance needs significant improvement.")
    
    # Component-specific feedback
    if scores["task_comprehension"] < 70:
        feedback.append("Improve task understanding and analysis.")
    
    if scores["tool_usage"] < 70:
        feedback.append("Better utilize available tools for task completion.")
    
    if scores["reasoning_quality"] < 70:
        feedback.append("Enhance reasoning quality and logical flow.")
    
    if scores["accuracy"] < 70:
        feedback.append("Focus on accuracy and meeting task requirements.")
    
    if scores["completeness"] < 70:
        feedback.append("Ensure all task requirements are fully addressed.")
    
    if scores["methodology"] < 70:
        feedback.append("Provide clearer explanation of problem-solving methodology.")
    
    # Task-specific feedback
    task_complexity = task.get("complexity", "medium")
    if task_complexity == "hard" and overall_score < 80:
        feedback.append("Complex tasks require more thorough analysis and execution.")
    
    # Confidence feedback
    confidence = response.get("confidence", 0.5)
    if confidence < 0.6:
        feedback.append("Build confidence through more thorough verification.")
    elif confidence > 0.9 and overall_score < 85:
        feedback.append("Confidence level seems misaligned with actual performance.")
    
    return feedback