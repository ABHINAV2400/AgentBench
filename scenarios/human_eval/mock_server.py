from flask import Flask, request, jsonify
import subprocess
import tempfile
import os
import json
import sys
from threading import Lock

app = Flask(__name__)
execution_lock = Lock()

# HumanEval-style coding problems
coding_problems = {
    "problem_1": {
        "id": "problem_1",
        "title": "Two Sum",
        "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        "function_signature": "def two_sum(nums, target):",
        "examples": [
            {"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]"},
            {"input": "nums = [3,2,4], target = 6", "output": "[1,2]"}
        ],
        "test_cases": [
            {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1]},
            {"input": {"nums": [3, 2, 4], "target": 6}, "expected": [1, 2]},
            {"input": {"nums": [3, 3], "target": 6}, "expected": [0, 1]},
            {"input": {"nums": [1, 2, 3, 4, 5], "target": 8}, "expected": [2, 4]},
        ]
    },
    "problem_2": {
        "id": "problem_2", 
        "title": "Palindrome Check",
        "description": "Write a function that checks if a given string is a palindrome (reads the same forwards and backwards).",
        "function_signature": "def is_palindrome(s):",
        "examples": [
            {"input": "s = 'racecar'", "output": "True"},
            {"input": "s = 'hello'", "output": "False"},
            {"input": "s = 'A man a plan a canal Panama'", "output": "True"}
        ],
        "test_cases": [
            {"input": {"s": "racecar"}, "expected": True},
            {"input": {"s": "hello"}, "expected": False},
            {"input": {"s": "A man a plan a canal Panama"}, "expected": True},
            {"input": {"s": "race a car"}, "expected": False},
            {"input": {"s": ""}, "expected": True},
            {"input": {"s": "a"}, "expected": True}
        ]
    },
    "problem_3": {
        "id": "problem_3",
        "title": "Fibonacci Sequence",
        "description": "Write a function that returns the nth number in the Fibonacci sequence. The sequence starts with 0, 1, 1, 2, 3, 5, 8, ...",
        "function_signature": "def fibonacci(n):",
        "examples": [
            {"input": "n = 0", "output": "0"},
            {"input": "n = 1", "output": "1"}, 
            {"input": "n = 5", "output": "5"},
            {"input": "n = 10", "output": "55"}
        ],
        "test_cases": [
            {"input": {"n": 0}, "expected": 0},
            {"input": {"n": 1}, "expected": 1},
            {"input": {"n": 2}, "expected": 1},
            {"input": {"n": 5}, "expected": 5},
            {"input": {"n": 10}, "expected": 55},
            {"input": {"n": 15}, "expected": 610}
        ]
    },
    "problem_4": {
        "id": "problem_4",
        "title": "Binary Search",
        "description": "Implement binary search algorithm. Given a sorted array and a target value, return the index of the target or -1 if not found.",
        "function_signature": "def binary_search(arr, target):",
        "examples": [
            {"input": "arr = [1,3,5,7,9], target = 5", "output": "2"},
            {"input": "arr = [1,3,5,7,9], target = 4", "output": "-1"}
        ],
        "test_cases": [
            {"input": {"arr": [1, 3, 5, 7, 9], "target": 5}, "expected": 2},
            {"input": {"arr": [1, 3, 5, 7, 9], "target": 4}, "expected": -1},
            {"input": {"arr": [1, 3, 5, 7, 9], "target": 1}, "expected": 0},
            {"input": {"arr": [1, 3, 5, 7, 9], "target": 9}, "expected": 4},
            {"input": {"arr": [], "target": 1}, "expected": -1},
            {"input": {"arr": [5], "target": 5}, "expected": 0}
        ]
    },
    "problem_5": {
        "id": "problem_5",
        "title": "Valid Parentheses",
        "description": "Given a string containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.",
        "function_signature": "def is_valid_parentheses(s):",
        "examples": [
            {"input": "s = '()'", "output": "True"},
            {"input": "s = '()[]{}'", "output": "True"},
            {"input": "s = '(]'", "output": "False"}
        ],
        "test_cases": [
            {"input": {"s": "()"}, "expected": True},
            {"input": {"s": "()[]{}"}, "expected": True},
            {"input": {"s": "(]"}, "expected": False},
            {"input": {"s": "([)]"}, "expected": False},
            {"input": {"s": "{[]}"}, "expected": True},
            {"input": {"s": ""}, "expected": True}
        ]
    }
}

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "human_eval_mock_server"})

@app.route('/api/problems')
def get_problems():
    """Get list of all available coding problems."""
    problems = []
    for problem_id, problem in coding_problems.items():
        problems.append({
            "id": problem["id"],
            "title": problem["title"],
            "description": problem["description"]
        })
    return jsonify({"problems": problems})

@app.route('/api/problems/<problem_id>')
def get_problem_details(problem_id):
    """Get detailed information about a specific problem."""
    if problem_id not in coding_problems:
        return jsonify({"error": "Problem not found"}), 404
    
    problem = coding_problems[problem_id].copy()
    # Don't include test cases in the response (hidden for evaluation)
    problem.pop("test_cases", None)
    return jsonify(problem)

@app.route('/api/problems/<problem_id>/submit', methods=['POST'])
def submit_solution(problem_id):
    """Submit a solution for evaluation."""
    if problem_id not in coding_problems:
        return jsonify({"error": "Problem not found"}), 404
    
    data = request.get_json()
    if not data or 'solution' not in data:
        return jsonify({"error": "Solution code required"}), 400
    
    solution_code = data['solution']
    problem = coding_problems[problem_id]
    
    with execution_lock:
        try:
            # Test the solution
            results = test_solution(solution_code, problem)
            return jsonify(results)
        except Exception as e:
            return jsonify({
                "error": f"Execution error: {str(e)}",
                "passed": False,
                "test_results": []
            }), 500

def test_solution(solution_code: str, problem: dict) -> dict:
    """Test a solution against test cases."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test file
        test_file = os.path.join(temp_dir, 'test_solution.py')
        
        # Generate test code
        test_code = f"""
import sys
import json

{solution_code}

def run_tests():
    test_cases = {json.dumps(problem['test_cases'])}
    results = []
    passed_count = 0
    
    for i, test_case in enumerate(test_cases):
        try:
            # Extract function name from solution
            func_name = '{problem['function_signature'].split('(')[0].replace('def ', '')}'
            func = locals()[func_name]
            
            # Run test case
            result = func(**test_case['input'])
            expected = test_case['expected']
            
            passed = result == expected
            if passed:
                passed_count += 1
                
            results.append({{
                'test_case': i + 1,
                'input': test_case['input'],
                'expected': expected,
                'actual': result,
                'passed': passed
            }})
            
        except Exception as e:
            results.append({{
                'test_case': i + 1,
                'input': test_case['input'],
                'expected': test_case['expected'],
                'actual': None,
                'passed': False,
                'error': str(e)
            }})
    
    return {{
        'passed': passed_count == len(test_cases),
        'passed_count': passed_count,
        'total_count': len(test_cases),
        'test_results': results
    }}

if __name__ == '__main__':
    try:
        result = run_tests()
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({{'error': str(e), 'passed': False}}))
"""
        
        with open(test_file, 'w') as f:
            f.write(test_code)
        
        # Execute tests
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=temp_dir
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {
                "error": f"Execution failed: {result.stderr}",
                "passed": False,
                "test_results": []
            }

def start_server():
    app.run(host='127.0.0.1', port=8004, debug=False, use_reloader=False)

if __name__ == "__main__":
    start_server()