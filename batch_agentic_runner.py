import argparse
import json
import time
from pathlib import Path
from agentic_benchmark_runner import run_benchmark, SCENARIO_CONFIGS, MODEL_CONFIGS

def run_batch_benchmarks(scenarios, models, task_params=None):
    """Run benchmarks for multiple scenarios and models."""
    print(f"🚀 Starting batch benchmark run")
    print(f"📊 Scenarios: {scenarios}")
    print(f"🤖 Models: {models}")
    print(f"⏱️  Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    total_combinations = len(scenarios) * len(models)
    current_combination = 0
    
    start_time = time.time()
    
    for scenario in scenarios:
        for model in models:
            current_combination += 1
            print(f"\n{'='*60}")
            print(f"📍 Progress: {current_combination}/{total_combinations}")
            print(f"🎯 Running: {scenario} with {model}")
            print(f"{'='*60}")
            
            try:
                result = run_benchmark(scenario, model, task_params)
                results.append({
                    'scenario': scenario,
                    'model': model,
                    'success': True,
                    'overall_score': result['evaluation']['scores']['overall_score'],
                    'passed': result['evaluation']['passed'],
                    'execution_time': result['execution_time_sec']
                })
                print(f"✅ Completed: {scenario} with {model}")
                
            except Exception as e:
                print(f"❌ Failed: {scenario} with {model} - {str(e)}")
                results.append({
                    'scenario': scenario,
                    'model': model,
                    'success': False,
                    'error': str(e),
                    'overall_score': 0,
                    'passed': False,
                    'execution_time': 0
                })
    
    total_time = time.time() - start_time
    
    # Generate summary report
    print(f"\n{'='*80}")
    print(f"📈 BATCH BENCHMARK SUMMARY")
    print(f"{'='*80}")
    print(f"⏱️  Total execution time: {total_time:.2f}s ({total_time/60:.1f} minutes)")
    print(f"🎯 Total combinations: {total_combinations}")
    print(f"✅ Successful runs: {sum(1 for r in results if r['success'])}")
    print(f"❌ Failed runs: {sum(1 for r in results if not r['success'])}")
    
    # Results by scenario
    print(f"\n📊 RESULTS BY SCENARIO:")
    for scenario in scenarios:
        scenario_results = [r for r in results if r['scenario'] == scenario]
        successful_results = [r for r in scenario_results if r['success']]
        avg_score = sum(r['overall_score'] for r in successful_results) / len(successful_results) if successful_results else 0
        passed_count = sum(1 for r in scenario_results if r['passed'])
        
        print(f"  📋 {scenario.replace('_', ' ').title()}:")
        print(f"    • Average Score: {avg_score:.1f}/100")
        print(f"    • Passed: {passed_count}/{len(scenario_results)}")
        
        for result in scenario_results:
            status = "✅ PASS" if result['passed'] else "❌ FAIL" if result['success'] else "💥 ERROR"
            score = f"{result['overall_score']:.1f}" if result['success'] else "N/A"
            print(f"    • {result['model']}: {status} ({score}/100)")
    
    # Results by model
    print(f"\n🤖 RESULTS BY MODEL:")
    for model in models:
        model_results = [r for r in results if r['model'] == model]
        successful_results = [r for r in model_results if r['success']]
        avg_score = sum(r['overall_score'] for r in successful_results) / len(successful_results) if successful_results else 0
        passed_count = sum(1 for r in model_results if r['passed'])
        
        print(f"  🤖 {model}:")
        print(f"    • Average Score: {avg_score:.1f}/100")
        print(f"    • Passed: {passed_count}/{len(model_results)}")
        
        for result in model_results:
            status = "✅ PASS" if result['passed'] else "❌ FAIL" if result['success'] else "💥 ERROR"
            score = f"{result['overall_score']:.1f}" if result['success'] else "N/A"
            print(f"    • {result['scenario']}: {status} ({score}/100)")
    
    # Top performers
    successful_results = [r for r in results if r['success']]
    if successful_results:
        top_result = max(successful_results, key=lambda x: x['overall_score'])
        print(f"\n🏆 TOP PERFORMER:")
        print(f"  🥇 {top_result['model']} on {top_result['scenario']}: {top_result['overall_score']:.1f}/100")
        
        # Best model overall
        model_averages = {}
        for model in models:
            model_results = [r for r in successful_results if r['model'] == model]
            if model_results:
                model_averages[model] = sum(r['overall_score'] for r in model_results) / len(model_results)
        
        if model_averages:
            best_model = max(model_averages, key=model_averages.get)
            print(f"  🏅 Best Overall Model: {best_model} (avg: {model_averages[best_model]:.1f}/100)")
    
    # Save batch summary
    summary_file = Path(__file__).parent / 'results' / f"batch_summary_{int(time.time())}.json"
    summary_data = {
        'timestamp': time.time(),
        'scenarios': scenarios,
        'models': models,
        'total_time_sec': total_time,
        'results': results,
        'summary': {
            'total_combinations': total_combinations,
            'successful_runs': sum(1 for r in results if r['success']),
            'failed_runs': sum(1 for r in results if not r['success']),
            'average_score': sum(r['overall_score'] for r in results if r['success']) / len([r for r in results if r['success']]) if any(r['success'] for r in results) else 0
        }
    }
    
    with open(summary_file, 'w') as f:
        json.dump(summary_data, f, indent=2)
    
    print(f"\n💾 Batch summary saved to: {summary_file}")
    return results

def validate_inputs(scenarios, models):
    """Validate scenario and model inputs."""
    invalid_scenarios = [s for s in scenarios if s not in SCENARIO_CONFIGS]
    invalid_models = [m for m in models if m not in MODEL_CONFIGS]
    
    if invalid_scenarios:
        raise ValueError(f"Invalid scenarios: {invalid_scenarios}. Available: {list(SCENARIO_CONFIGS.keys())}")
    
    if invalid_models:
        raise ValueError(f"Invalid models: {invalid_models}. Available: {list(MODEL_CONFIGS.keys())}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run batch agentic AI benchmarks')
    parser.add_argument('--scenarios', nargs='+', 
                       default=['customer_support', 'web_navigation', 'swe_bench', 'human_eval', 'gaia_tasks'],
                       help='List of benchmark scenarios to run')
    parser.add_argument('--models', nargs='+',
                       default=['custom_api', 'gpt4o', 'claude_3_5_sonnet'],
                       help='List of models to test')
    parser.add_argument('--task-description', help='Custom task description for supported scenarios')
    
    args = parser.parse_args()
    
    try:
        validate_inputs(args.scenarios, args.models)
        
        task_params = {}
        if args.task_description:
            task_params['task_description'] = args.task_description
            task_params['issue_description'] = args.task_description
            task_params['problem_list'] = args.task_description
        
        run_batch_benchmarks(args.scenarios, args.models, task_params)
        
    except KeyboardInterrupt:
        print("\n🛑 Batch benchmark interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")