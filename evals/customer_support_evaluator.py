import requests
import json

def get_ai_tracking_data():
    """Retrieve AI action tracking data from the mock server"""
    try:
        response = requests.get('http://127.0.0.1:8001/tracking/actions')
        return response.json()
    except Exception as e:
        return None

def evaluate_workflow_states(actual_states, expected_states):
    """Compare actual workflow states against expected states"""
    score = 0.0
    max_score = len(expected_states)
    state_results = []
    
    for expected_state in expected_states:
        state_name = expected_state['state']
        required = expected_state.get('required', True)
        
        # Find matching actual state
        matching_state = None
        for actual_state in actual_states:
            if state_name in actual_state.get('state', '') or state_name in actual_state.get('description', ''):
                matching_state = actual_state
                break
        
        if matching_state:
            score += 1.0
            state_results.append({
                'state': state_name,
                'expected': expected_state['description'],
                'actual': matching_state['description'],
                'achieved': True,
                'timestamp': matching_state.get('timestamp')
            })
        else:
            state_results.append({
                'state': state_name,
                'expected': expected_state['description'],
                'actual': None,
                'achieved': False,
                'required': required
            })
    
    return {
        'workflow_score': score / max(1, max_score),
        'states_completed': score,
        'total_states_expected': max_score,
        'state_details': state_results
    }

def evaluate_api_calls(actual_calls, expected_calls):
    """Compare actual API calls against expected API pattern"""
    score = 0.0
    max_score = len(expected_calls)
    call_results = []
    
    for expected_call in expected_calls:
        expected_endpoint = expected_call['endpoint']
        expected_method = expected_call['method']
        expected_order = expected_call.get('order', 1)
        
        # Find matching actual call
        matching_call = None
        for actual_call in actual_calls:
            if (expected_endpoint in actual_call.get('endpoint', '') and 
                expected_method == actual_call.get('method')):
                matching_call = actual_call
                break
        
        if matching_call:
            score += 1.0
            call_results.append({
                'endpoint': expected_endpoint,
                'method': expected_method,
                'expected_order': expected_order,
                'found': True,
                'actual_timestamp': matching_call.get('timestamp'),
                'payload': matching_call.get('payload')
            })
        else:
            call_results.append({
                'endpoint': expected_endpoint,
                'method': expected_method,
                'expected_order': expected_order,
                'found': False
            })
    
    return {
        'api_usage_score': score / max(1, max_score),
        'calls_completed': score,
        'total_calls_expected': max_score,
        'call_details': call_results
    }

def evaluate_database_changes(actual_changes, expected_changes):
    """Compare actual database modifications against expected changes"""
    score = 0.0
    max_score = len(expected_changes)
    change_results = []
    
    for expected_key, expected_change in expected_changes.items():
        expected_field = expected_change['field']
        
        # Find matching actual change
        matching_change = None
        for actual_change in actual_changes:
            if (str(actual_change.get('record_id')) in expected_key and
                actual_change.get('field') == expected_field):
                matching_change = actual_change
                break
        
        if matching_change:
            score += 1.0
            change_results.append({
                'target': expected_key,
                'field': expected_field,
                'found': True,
                'old_value': matching_change.get('old_value'),
                'new_value': matching_change.get('new_value'),
                'timestamp': matching_change.get('timestamp')
            })
        else:
            change_results.append({
                'target': expected_key,
                'field': expected_field,
                'found': False,
                'expected_change': expected_change['expected_change']
            })
    
    return {
        'database_accuracy_score': score / max(1, max_score),
        'changes_completed': score,
        'total_changes_expected': max_score,
        'change_details': change_results
    }

def evaluate_response_quality(model_output, expected_content_elements):
    """Evaluate the quality of the AI's textual response"""
    if not expected_content_elements:
        return {'response_quality_score': 1.0, 'content_analysis': 'No specific content requirements'}
    
    matches = 0
    matched_elements = []
    
    for element in expected_content_elements:
        if element.lower() in model_output.lower():
            matches += 1
            matched_elements.append(element)
    
    quality_score = matches / len(expected_content_elements)
    
    return {
        'response_quality_score': quality_score,
        'content_elements_matched': matched_elements,
        'total_content_elements': len(expected_content_elements),
        'response_length': len(model_output)
    }

def evaluate_customer_support_comprehensive(model_output: str, expected_criteria: dict) -> dict:
    """
    Comprehensive evaluation using workflow states, database changes, and API calls
    
    Args:
        model_output: The AI model's response to the customer support scenario
        expected_criteria: Dictionary containing detailed evaluation criteria
    
    Returns:
        Dictionary with comprehensive evaluation scores and metrics
    """
    # Get actual AI behavior data from tracking
    tracking_data = get_ai_tracking_data()
    
    if not tracking_data:
        # Fallback to basic evaluation if tracking unavailable
        return evaluate_basic_response(model_output, expected_criteria)
    
    # Extract expected criteria
    expected_workflow = expected_criteria.get('expected_workflow_states', [])
    expected_database = expected_criteria.get('expected_database_changes', {})
    expected_api = expected_criteria.get('expected_api_calls', [])
    expected_content = []
    
    # Extract content elements from workflow states
    for state in expected_workflow:
        content_elements = state.get('expected_content_elements', [])
        expected_content.extend(content_elements)
    
    # Perform comprehensive evaluation
    workflow_results = evaluate_workflow_states(
        tracking_data.get('workflow_states', []), 
        expected_workflow
    )
    
    api_results = evaluate_api_calls(
        tracking_data.get('api_calls', []),
        expected_api
    )
    
    database_results = evaluate_database_changes(
        tracking_data.get('database_changes', []),
        expected_database
    )
    
    quality_results = evaluate_response_quality(model_output, expected_content)
    
    # Calculate weighted overall score
    weights = expected_criteria.get('scoring_weights', {
        'workflow_completion': 0.4,
        'database_accuracy': 0.3,
        'api_usage': 0.2,
        'response_quality': 0.1
    })
    
    overall_score = (
        workflow_results['workflow_score'] * weights.get('workflow_completion', 0.4) +
        database_results['database_accuracy_score'] * weights.get('database_accuracy', 0.3) +
        api_results['api_usage_score'] * weights.get('api_usage', 0.2) +
        quality_results['response_quality_score'] * weights.get('response_quality', 0.1)
    )
    
    # Determine if passing
    minimum_score = expected_criteria.get('minimum_passing_score', 0.7)
    passed = overall_score >= minimum_score
    
    return {
        'overall_score': round(overall_score, 3),
        'passed': passed,
        'minimum_passing_score': minimum_score,
        'detailed_scores': {
            'workflow_completion': workflow_results,
            'database_accuracy': database_results, 
            'api_usage': api_results,
            'response_quality': quality_results
        },
        'execution_summary': {
            'total_api_calls': len(tracking_data.get('api_calls', [])),
            'total_database_changes': len(tracking_data.get('database_changes', [])),
            'total_workflow_states': len(tracking_data.get('workflow_states', [])),
            'test_duration': tracking_data.get('end_time', '') if tracking_data.get('start_time') else 'unknown'
        },
        'model_output': model_output,
        'tracking_data_available': True
    }

def evaluate_basic_response(model_output: str, expected_criteria: dict) -> dict:
    """Fallback evaluation when tracking data is unavailable"""
    # Extract basic content requirements
    content_elements = []
    for state in expected_criteria.get('expected_workflow_states', []):
        content_elements.extend(state.get('expected_content_elements', []))
    
    if not content_elements:
        # Legacy support
        content_elements = expected_criteria.get('expected_reply_contains', [])
    
    quality_results = evaluate_response_quality(model_output, content_elements)
    
    return {
        'overall_score': quality_results['response_quality_score'],
        'passed': quality_results['response_quality_score'] >= expected_criteria.get('minimum_passing_score', 0.7),
        'detailed_scores': {
            'response_quality': quality_results
        },
        'model_output': model_output,
        'tracking_data_available': False,
        'note': 'Limited evaluation - tracking data unavailable'
    }

# Keep backward compatibility
def evaluate(output: str, expected: dict) -> dict:
    return evaluate_customer_support_comprehensive(output, expected)