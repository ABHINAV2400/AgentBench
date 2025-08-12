import argparse
from benchmark_runner import run_benchmark

def run_multiple_benchmarks(scenarios, models):
    """Run multiple benchmark scenarios with multiple models"""
    for scenario in scenarios:
        for model in models:
            print(f"\n{'='*60}")
            run_benchmark(scenario, model)
            print(f"{'='*60}\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run multiple AI agent benchmarks')
    parser.add_argument('--scenarios', nargs='+', default=['customer_support'], 
                       help='List of benchmark scenarios to run')
    parser.add_argument('--models', nargs='+', default=['incredible_api'],
                       help='List of models to test')
    args = parser.parse_args()

    run_multiple_benchmarks(args.scenarios, args.models)