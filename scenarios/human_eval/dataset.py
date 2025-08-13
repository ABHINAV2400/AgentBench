"""
HumanEval dataset loader - Direct Hugging Face Hub integration
Replaces manual dataset with authentic HumanEval from HF
"""
from typing import Dict, List
from hf_dataset_loader import HuggingFaceDatasetLoader

def get_human_eval_problems(limit: int = None) -> List[Dict]:
    """Get HumanEval problems directly from Hugging Face."""
    loader = HuggingFaceDatasetLoader()
    dataset = loader.load_benchmark_dataset('humaneval', limit=limit)
    return dataset['problems']

def get_problem_by_id(task_id: str) -> Dict:
    """Get a specific problem by task ID from HF dataset."""
    problems = get_human_eval_problems()
    for problem in problems:
        if problem["task_id"] == task_id:
            return problem
    raise ValueError(f"Problem {task_id} not found in HumanEval dataset")

def execute_test(code: str, test_code: str) -> Dict:
    """Execute code against HumanEval test cases with enhanced error handling."""
    import sys
    import io
    import traceback
    import signal
    import contextlib
    
    def timeout_handler(signum, frame):
        raise TimeoutError("Code execution timed out")
    
    try:
        # Create isolated execution environment
        exec_globals = {
            '__builtins__': {
                'abs': abs, 'all': all, 'any': any, 'ascii': ascii, 'bin': bin,
                'bool': bool, 'chr': chr, 'dict': dict, 'divmod': divmod,
                'enumerate': enumerate, 'filter': filter, 'float': float,
                'format': format, 'frozenset': frozenset, 'hex': hex, 'int': int,
                'len': len, 'list': list, 'map': map, 'max': max, 'min': min,
                'oct': oct, 'ord': ord, 'pow': pow, 'range': range, 'repr': repr,
                'reversed': reversed, 'round': round, 'set': set, 'sorted': sorted,
                'str': str, 'sum': sum, 'tuple': tuple, 'type': type, 'zip': zip,
                'Exception': Exception, 'ValueError': ValueError, 'TypeError': TypeError,
                'IndexError': IndexError, 'KeyError': KeyError, 'AttributeError': AttributeError,
                '__import__': __import__, 'hasattr': hasattr, 'getattr': getattr,
                'setattr': setattr, 'delattr': delattr, 'callable': callable,
                'isinstance': isinstance, 'issubclass': issubclass
            }
        }
        
        # Add common imports that are safe
        safe_imports = {
            'math': ['math', 'sqrt', 'ceil', 'floor', 'log', 'exp', 'sin', 'cos'],
            'collections': ['Counter', 'defaultdict', 'deque'],
            'itertools': ['combinations', 'permutations', 'product'],
            'functools': ['reduce'],
            'typing': ['List', 'Dict', 'Set', 'Tuple', 'Optional', 'Union']
        }
        
        for module, items in safe_imports.items():
            try:
                mod = __import__(module)
                for item in items:
                    if hasattr(mod, item):
                        exec_globals[item] = getattr(mod, item)
            except ImportError:
                pass
        
        # Set timeout for code execution (5 seconds)
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(5)
        
        # Capture stdout/stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture
            
            # Execute the solution code first
            exec(code, exec_globals)
            
            # Then execute the test code
            exec(test_code, exec_globals)
            
            # If we get here, all tests passed
            return {
                "passed": True,
                "result": "All tests passed",
                "stdout": stdout_capture.getvalue(),
                "stderr": stderr_capture.getvalue()
            }
            
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            signal.alarm(0)  # Cancel timeout
            
    except TimeoutError:
        return {
            "passed": False,
            "result": "Code execution timed out (>5 seconds)"
        }
    except SyntaxError as e:
        return {
            "passed": False,
            "result": f"Syntax error: {str(e)}"
        }
    except NameError as e:
        return {
            "passed": False,
            "result": f"Name error: {str(e)}"
        }
    except AssertionError as e:
        return {
            "passed": False,
            "result": f"Test failed: {str(e) if str(e) else 'Assertion failed'}"
        }
    except Exception as e:
        return {
            "passed": False,
            "result": f"{type(e).__name__}: {str(e)}",
            "traceback": traceback.format_exc()
        }

def get_dataset_info() -> Dict:
    """Get information about the HumanEval dataset."""
    return {
        "name": "OpenAI HumanEval",
        "source": "huggingface:openai_humaneval", 
        "description": "Hand-written programming problems for code generation evaluation",
        "total_problems": 164,
        "url": "https://huggingface.co/datasets/openai_humaneval",
        "paper": "https://arxiv.org/abs/2107.03374"
    }

# Legacy compatibility function
def get_human_eval_dataset() -> Dict:
    """Legacy function for compatibility."""
    return {
        "type": "code_execution",
        "problems": get_human_eval_problems(),
        "info": get_dataset_info()
    }