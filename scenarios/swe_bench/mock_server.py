from flask import Flask, request, jsonify
import subprocess
import tempfile
import os
import shutil
import json
from threading import Lock

app = Flask(__name__)
execution_lock = Lock()

# Mock repository structure
mock_repo = {
    "src/calculator.py": '''def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def power(a, b):
    return a ** b
''',
    "src/utils.py": '''def validate_number(value):
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Invalid number: {value}")

def format_result(result):
    if isinstance(result, float) and result.is_integer():
        return int(result)
    return result
''',
    "tests/test_calculator.py": '''import pytest
from src.calculator import add, subtract, multiply, divide, power

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(0, 5) == -5

def test_multiply():
    assert multiply(4, 5) == 20
    assert multiply(-2, 3) == -6

def test_divide():
    assert divide(10, 2) == 5
    assert divide(7, 2) == 3.5

def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(5, 0)

def test_power():
    assert power(2, 3) == 8
    assert power(5, 0) == 1
''',
    "requirements.txt": "pytest>=6.0.0",
    "README.md": '''# Calculator Library

A simple calculator library with basic arithmetic operations.

## Features
- Addition, subtraction, multiplication, division
- Power operations
- Input validation
- Error handling

## Usage
```python
from src.calculator import add, subtract
result = add(2, 3)
```
''',
    ".gitignore": '''__pycache__/
*.pyc
*.pyo
*.pyd
.pytest_cache/
dist/
build/
*.egg-info/
'''
}

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "swe_bench_mock_server"})

@app.route('/api/repository/structure')
def get_repo_structure():
    """Get the repository file structure."""
    return jsonify({"files": list(mock_repo.keys())})

@app.route('/api/repository/file/<path:filepath>')
def get_file_content(filepath):
    """Get content of a specific file."""
    if filepath in mock_repo:
        return jsonify({"content": mock_repo[filepath], "filepath": filepath})
    return jsonify({"error": "File not found"}), 404

@app.route('/api/repository/file/<path:filepath>', methods=['PUT'])
def update_file_content(filepath):
    """Update content of a specific file."""
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({"error": "Content required"}), 400
    
    mock_repo[filepath] = data['content']
    return jsonify({"message": "File updated successfully"})

@app.route('/api/repository/file/<path:filepath>', methods=['POST'])
def create_file(filepath):
    """Create a new file."""
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({"error": "Content required"}), 400
    
    if filepath in mock_repo:
        return jsonify({"error": "File already exists"}), 409
    
    mock_repo[filepath] = data['content']
    return jsonify({"message": "File created successfully"})

@app.route('/api/execute/tests', methods=['POST'])
def run_tests():
    """Execute tests and return results."""
    with execution_lock:
        try:
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write files to temp directory
                for filepath, content in mock_repo.items():
                    full_path = os.path.join(temp_dir, filepath)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    with open(full_path, 'w') as f:
                        f.write(content)
                
                # Run pytest
                result = subprocess.run(
                    ['python', '-m', 'pytest', 'tests/', '-v', '--tb=short'],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                return jsonify({
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode,
                    "success": result.returncode == 0
                })
                
        except subprocess.TimeoutExpired:
            return jsonify({"error": "Test execution timeout"}), 408
        except Exception as e:
            return jsonify({"error": f"Execution error: {str(e)}"}), 500

@app.route('/api/execute/code', methods=['POST'])
def execute_code():
    """Execute arbitrary Python code."""
    data = request.get_json()
    if not data or 'code' not in data:
        return jsonify({"error": "Code required"}), 400
    
    with execution_lock:
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write repository files
                for filepath, content in mock_repo.items():
                    full_path = os.path.join(temp_dir, filepath)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    with open(full_path, 'w') as f:
                        f.write(content)
                
                # Write and execute code
                code_file = os.path.join(temp_dir, 'execute.py')
                with open(code_file, 'w') as f:
                    f.write(data['code'])
                
                result = subprocess.run(
                    ['python', 'execute.py'],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                return jsonify({
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode,
                    "success": result.returncode == 0
                })
                
        except subprocess.TimeoutExpired:
            return jsonify({"error": "Code execution timeout"}), 408
        except Exception as e:
            return jsonify({"error": f"Execution error: {str(e)}"}), 500

@app.route('/api/repository/diff')
def get_diff():
    """Get diff of changes made to repository."""
    # This would normally compare with git, but for mock we'll return a simple diff
    return jsonify({"diff": "Mock diff - files have been modified"})

def start_server():
    app.run(host='127.0.0.1', port=8003, debug=False, use_reloader=False)

if __name__ == "__main__":
    start_server()