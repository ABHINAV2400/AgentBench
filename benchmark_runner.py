import argparse
import importlib
import json
import os
import signal
import subprocess
import threading
import time
from pathlib import Path
from models import custom_model_client, openai_client

SCENARIOS_DIR = Path(__file__).parent / 'scenarios'
RESULTS_DIR = Path(__file__).parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

def start_mock_server(scenario_name):
    mock_server_path = SCENARIOS_DIR / scenario_name / 'mock_server.py'
    if not mock_server_path.exists():
        raise FileNotFoundError(mock_server_path)
    p = subprocess.Popen(['python', str(mock_server_path)])
    time.sleep(1)
    return p


def stop_server(process):
    try:
        process.send_signal(signal.SIGINT)
        process.wait(timeout=2)
    except Exception:
        process.kill()


def load_scenario_prompt(scenario_name):
    path = SCENARIOS_DIR / scenario_name / 'prompt.txt'
    return path.read_text(encoding='utf-8')


def load_expected_output(scenario_name):
    path = SCENARIOS_DIR / scenario_name / 'expected.json'
    return json.loads(path.read_text(encoding='utf-8'))


def run_benchmark(scenario_name, model_name):
    print(f"Running {scenario_name} benchmark with {model_name} model")
    server_process = start_mock_server(scenario_name)
    try:
        prompt = load_scenario_prompt(scenario_name)
        expected = load_expected_output(scenario_name)

        if model_name == 'incredible_api':
            model = custom_model_client.Model()
        elif model_name == 'openai_gpt4':
            model = openai_client.Model('gpt-4')
        else:
            raise ValueError(f'Unknown model: {model_name}')

        start_time = time.time()
        model_output = model.generate(prompt)
        execution_time = time.time() - start_time

        eval_module = importlib.import_module(f'evals.{scenario_name}_evaluator')
        score = eval_module.evaluate(model_output, expected)

        result = {
            'scenario': scenario_name,
            'model': model_name,
            'output': model_output,
            'score': score,
            'execution_time_sec': execution_time
        }
        result_file = RESULTS_DIR / f"{scenario_name}--{model_name}.json"
        result_file.write_text(json.dumps(result, indent=2))
        print(f'Results saved to: {result_file}')
    finally:
        stop_server(server_process)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run AI agent benchmarks')
    parser.add_argument('--scenario', required=True, help='Benchmark scenario name')
    parser.add_argument('--model', default='incredible_api', help='Model to test')
    args = parser.parse_args()

    run_benchmark(args.scenario, args.model)