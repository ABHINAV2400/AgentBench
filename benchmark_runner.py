import argparse
import importlib
import json
import os
import signal
import subprocess
import threading
import time
from pathlib import Path
from dotenv import load_dotenv
from models import (
    custom_model_client, openai_client, 
    claude_client, gemini_client, gpt4_client
)

# Load environment variables from .env file
load_dotenv()

SCENARIOS_DIR = Path(__file__).parent / 'scenarios'
RESULTS_DIR = Path(__file__).parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

# Available scenarios with their server ports
SCENARIO_CONFIGS = {
    'customer_support': {'port': 8001, 'evaluator': 'customer_support_evaluator'},
    'web_navigation': {'port': 8002, 'evaluator': 'web_navigation_evaluator'},
    'swe_bench': {'port': 8003, 'evaluator': 'swe_bench_evaluator'},
    'human_eval': {'port': 8004, 'evaluator': 'human_eval_evaluator'},
    'gaia_tasks': {'port': 8005, 'evaluator': 'gaia_tasks_evaluator'},
    'tool_bench': {'port': 8006, 'evaluator': 'tool_bench_evaluator'}
}

# Available models
MODEL_CONFIGS = {
    'custom_api': lambda: custom_model_client.Model(),
    'incredible_api': lambda: custom_model_client.Model(),
    'openai_gpt4': lambda: openai_client.OpenAIModel('gpt-4'),
    'gpt4o': lambda: gpt4_client.GPT4Client('gpt-4o'),
    'gpt4_turbo': lambda: gpt4_client.GPT4Client('gpt-4-turbo')
}

# Add optional models if available
try:
    MODEL_CONFIGS.update({
        'claude_3_5_sonnet': lambda: claude_client.ClaudeClient('claude-3-5-sonnet-20241022'),
        'claude_3_opus': lambda: claude_client.ClaudeClient('claude-3-opus-20240229')
    })
except NameError:
    pass

try:
    MODEL_CONFIGS.update({
        'gemini_1_5_pro': lambda: gemini_client.GeminiClient('gemini-1.5-pro-latest'),
        'gemini_1_5_flash': lambda: gemini_client.GeminiClient('gemini-1.5-flash-latest')
    })
except NameError:
    pass

def start_mock_server(scenario_name):
    """Start mock server for a scenario."""
    mock_server_path = SCENARIOS_DIR / scenario_name / 'mock_server.py'
    if not mock_server_path.exists():
        raise FileNotFoundError(f"Mock server not found: {mock_server_path}")
    
    print(f"Starting mock server for {scenario_name}...")
    p = subprocess.Popen(['python', str(mock_server_path)])
    time.sleep(2)  # Wait for server to start
    
    # Verify server is running
    port = SCENARIO_CONFIGS[scenario_name]['port']
    import requests
    try:
        response = requests.get(f'http://127.0.0.1:{port}/health', timeout=5)
        if response.status_code == 200:
            print(f"Mock server started successfully on port {port}")
        else:
            raise Exception(f"Server health check failed: {response.status_code}")
    except requests.RequestException as e:
        print(f"Warning: Could not verify server health: {e}")
    
    return p

def stop_server(process):
    """Stop mock server process."""
    try:
        process.send_signal(signal.SIGINT)
        process.wait(timeout=5)
        print("Mock server stopped")
    except Exception:
        process.kill()
        print("Mock server forcibly killed")

def load_scenario_prompt(scenario_name):
    """Load scenario prompt template."""
    path = SCENARIOS_DIR / scenario_name / 'prompt.txt'
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding='utf-8')

def load_benchmark_dataset(scenario_name):
    """Load real benchmark datasets instead of expected.json files."""
    try:
        if scenario_name == 'human_eval':
            from scenarios.human_eval.dataset import get_human_eval_problems
            return {"problems": get_human_eval_problems(), "type": "code_execution"}
        
        elif scenario_name == 'swe_bench':
            from scenarios.swe_bench.dataset import get_swe_bench_problems
            return {"problems": get_swe_bench_problems(), "type": "patch_evaluation"}
        
        elif scenario_name == 'web_navigation':
            from scenarios.web_navigation.dataset import get_web_navigation_tasks
            return {"tasks": get_web_navigation_tasks(), "type": "action_sequence"}
        
        elif scenario_name == 'gaia_tasks':
            from scenarios.gaia_tasks.dataset import get_gaia_tasks
            return {"tasks": get_gaia_tasks(), "type": "multi_step_reasoning"}
        
        elif scenario_name == 'tool_bench':
            from scenarios.tool_bench.dataset import get_tool_bench_tasks
            return {"tasks": get_tool_bench_tasks(), "type": "tool_usage"}
        
        # For legacy scenarios, return minimal structure
        return {"evaluation_criteria": {}, "total_points": 100, "type": "legacy"}
        
    except ImportError as e:
        print(f"Warning: Could not load dataset for {scenario_name}: {e}")
        return {"evaluation_criteria": {}, "total_points": 100, "type": "fallback"}

def customize_prompt_for_scenario(prompt_template, scenario_name, task_params=None):
    """Customize prompt template with scenario-specific parameters."""
    if scenario_name == 'web_navigation' and task_params:
        return prompt_template.format(task_description=task_params.get('task_description', 'Navigate and complete basic e-commerce tasks'))
    elif scenario_name == 'swe_bench' and task_params:
        return prompt_template.format(issue_description=task_params.get('issue_description', 'Add missing functionality and fix bugs'))
    elif scenario_name == 'human_eval' and task_params:
        return prompt_template.format(problem_list=task_params.get('problem_list', 'Solve all available coding problems'))
    elif scenario_name == 'gaia_tasks' and task_params:
        return prompt_template.format(task_description=task_params.get('task_description', 'Complete general assistant tasks requiring multi-step reasoning'))
    elif scenario_name == 'tool_bench' and task_params:
        return prompt_template.format(task_description=task_params.get('task_description', 'Complete complex multi-step tasks using available tools and APIs'))
    else:
        return prompt_template

def initialize_model(model_name):
    """Initialize model client."""
    if model_name not in MODEL_CONFIGS:
        raise ValueError(f'Unknown model: {model_name}. Available models: {list(MODEL_CONFIGS.keys())}')
    
    model_factory = MODEL_CONFIGS[model_name]
    
    # Handle different model initialization patterns
    if callable(model_factory):
        if model_name in ['custom_api', 'incredible_api']:
            return model_factory()
        else:
            return model_factory()
    else:
        return model_factory

def run_benchmark(scenario_name, model_name, task_params=None):
    """Run benchmark for a specific scenario and model."""
    if scenario_name not in SCENARIO_CONFIGS:
        raise ValueError(f'Unknown scenario: {scenario_name}. Available: {list(SCENARIO_CONFIGS.keys())}')
    
    print(f"\n🚀 Running {scenario_name} benchmark with {model_name} model")
    print(f"📊 Scenario: {scenario_name.replace('_', ' ').title()}")
    print(f"🤖 Model: {model_name}")
    
    server_process = None
    try:
        # Start mock server
        server_process = start_mock_server(scenario_name)
        
        # Load scenario components
        prompt_template = load_scenario_prompt(scenario_name)
        expected = load_benchmark_dataset(scenario_name)
        
        # Customize prompt for scenario
        prompt = customize_prompt_for_scenario(prompt_template, scenario_name, task_params)
        
        # Initialize model
        model = initialize_model(model_name)
        
        # Generate response
        print("🧠 Generating model response...")
        start_time = time.time()
        
        if hasattr(model, 'generate_response'):
            model_output = model.generate_response(prompt)
            if isinstance(model_output, dict):
                response_text = model_output.get('response', str(model_output))
            else:
                response_text = str(model_output)
        elif hasattr(model, 'generate'):
            model_output = model.generate(prompt)
            response_text = str(model_output)
        else:
            raise AttributeError(f"Model {model_name} does not have 'generate' or 'generate_response' method")
        
        execution_time = time.time() - start_time
        
        # Evaluate response
        print("📋 Evaluating response...")
        evaluator_name = SCENARIO_CONFIGS[scenario_name]['evaluator']
        eval_module = importlib.import_module(f'evals.{evaluator_name}')
        
        # Call appropriate evaluation function
        eval_function_name = f"evaluate_{scenario_name}"
        if hasattr(eval_module, eval_function_name):
            evaluation_result = getattr(eval_module, eval_function_name)(response_text, expected)
        elif hasattr(eval_module, 'evaluate'):
            evaluation_result = eval_module.evaluate(response_text, expected)
        else:
            raise AttributeError(f"No evaluation function found in {evaluator_name}")
        
        # Compile results
        result = {
            'scenario': scenario_name,
            'model': model_name,
            'prompt': prompt[:500] + "..." if len(prompt) > 500 else prompt,  # Truncate long prompts
            'output': response_text,
            'evaluation': evaluation_result,
            'execution_time_sec': execution_time,
            'timestamp': time.time(),
            'task_parameters': task_params or {}
        }
        
        # Save results
        result_file = RESULTS_DIR / f"{scenario_name}--{model_name}.json"
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        # Print summary
        scores = evaluation_result.get('scores', {})
        overall_score = scores.get('overall_score', 0)
        passed = evaluation_result.get('passed', False)
        
        print(f"\n✅ Benchmark completed!")
        print(f"📈 Overall Score: {overall_score:.1f}/100")
        print(f"🎯 Result: {'PASSED' if passed else 'FAILED'}")
        print(f"⏱️  Execution Time: {execution_time:.2f}s")
        print(f"💾 Results saved to: {result_file}")
        
        # Print detailed scores
        if scores:
            print(f"\n📊 Detailed Scores:")
            for component, score in scores.items():
                if component != 'overall_score':
                    print(f"  • {component.replace('_', ' ').title()}: {score:.1f}/100")
        
        # Print feedback
        feedback = evaluation_result.get('details', {}).get('feedback', [])
        if feedback:
            print(f"\n💭 Feedback:")
            for item in feedback[:3]:  # Show first 3 feedback items
                print(f"  • {item}")
        
        return result
        
    except Exception as e:
        print(f"❌ Benchmark failed: {str(e)}")
        raise e
    finally:
        if server_process:
            stop_server(server_process)

def list_available_scenarios():
    """List all available benchmark scenarios."""
    print("Available benchmark scenarios:")
    for scenario, config in SCENARIO_CONFIGS.items():
        print(f"  • {scenario}: {scenario.replace('_', ' ').title()}")

def list_available_models():
    """List all available models."""
    print("Available models:")
    for model_name in MODEL_CONFIGS.keys():
        print(f"  • {model_name}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run comprehensive agentic AI benchmarks')
    parser.add_argument('--scenario', help='Benchmark scenario name')
    parser.add_argument('--model', default='custom_api', help='Model to test')
    parser.add_argument('--list-scenarios', action='store_true', help='List available scenarios')
    parser.add_argument('--list-models', action='store_true', help='List available models')
    parser.add_argument('--task-description', help='Custom task description for supported scenarios')
    
    args = parser.parse_args()
    
    if args.list_scenarios:
        list_available_scenarios()
    elif args.list_models:
        list_available_models()
    elif args.scenario:
        task_params = {}
        if args.task_description:
            task_params['task_description'] = args.task_description
            task_params['issue_description'] = args.task_description
            task_params['problem_list'] = args.task_description
        
        try:
            run_benchmark(args.scenario, args.model, task_params)
        except KeyboardInterrupt:
            print("\n🛑 Benchmark interrupted by user")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        parser.print_help()