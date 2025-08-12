#!/usr/bin/env python3
"""
Fully automated benchmark runner using Hugging Face datasets
No user intervention required - loads datasets, runs benchmarks, generates reports
"""
import os
import time
import json
from pathlib import Path
from dotenv import load_dotenv
from benchmark_runner import run_benchmark, MODEL_CONFIGS
from comprehensive_report import ComprehensiveBenchmarkReporter

# Load environment variables
load_dotenv()

# Automated benchmark configurations
AUTO_SCENARIOS = {
    'human_eval': {
        'description': 'Code generation benchmark using HumanEval dataset',
        'dataset_source': 'huggingface:openai_humaneval',
        'auto_evaluation': True
    },
    'swe_bench': {
        'description': 'Software engineering benchmark using SWE-bench dataset', 
        'dataset_source': 'huggingface:princeton-nlp/SWE-bench',
        'auto_evaluation': True
    },
    'web_navigation': {
        'description': 'Web navigation tasks using WebArena-style challenges',
        'dataset_source': 'builtin:web_navigation_tasks',
        'auto_evaluation': True
    },
    'gaia_tasks': {
        'description': 'General intelligence tasks using GAIA benchmark',
        'dataset_source': 'huggingface:gaia-benchmark/GAIA',
        'auto_evaluation': True
    }
}

# Models to test automatically (only those with API keys available)
def get_available_models():
    """Get models that have API keys configured."""
    available = []
    
    if os.getenv('OPENAI_API_KEY'):
        available.extend(['gpt4o', 'gpt4_turbo'])
    
    if os.getenv('ANTHROPIC_API_KEY'):
        available.extend(['claude_3_5_sonnet', 'claude_3_opus'])
    
    if os.getenv('GOOGLE_API_KEY'):
        available.extend(['gemini_1_5_pro', 'gemini_1_5_flash'])
    
    if os.getenv('CUSTOM_API_KEY') or os.getenv('CUSTOM_API_URL'):
        available.append('custom_api')
    
    return available

def run_automated_benchmarks():
    """Run automated benchmarks with zero user intervention."""
    print("🚀 Starting Fully Automated Benchmark Suite")
    print("=" * 60)
    
    # Check available models
    available_models = get_available_models()
    if not available_models:
        print("❌ No API keys found. Please configure at least one:")
        print("   • OPENAI_API_KEY for GPT models")
        print("   • ANTHROPIC_API_KEY for Claude models") 
        print("   • GOOGLE_API_KEY for Gemini models")
        print("   • CUSTOM_API_KEY for custom models")
        return
    
    print(f"🤖 Found {len(available_models)} available models:")
    for model in available_models:
        print(f"   • {model}")
    
    print(f"📊 Running {len(AUTO_SCENARIOS)} automated scenarios:")
    for scenario, config in AUTO_SCENARIOS.items():
        print(f"   • {scenario}: {config['description']}")
    
    print("\n⏱️  Starting automated execution...")
    start_time = time.time()
    
    results = []
    total_tests = len(AUTO_SCENARIOS) * len(available_models)
    current_test = 0
    
    # Run all combinations
    for scenario in AUTO_SCENARIOS:
        for model in available_models:
            current_test += 1
            print(f"\n[{current_test}/{total_tests}] Running {scenario} with {model}")
            
            try:
                result = run_benchmark(scenario, model)
                results.append(result)
                
                score = result['evaluation']['scores']['overall_score']
                passed = result['evaluation']['passed']
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"   Result: {status} ({score:.1f}/100)")
                
            except Exception as e:
                print(f"   ❌ ERROR: {str(e)}")
                results.append({
                    'scenario': scenario,
                    'model': model,
                    'evaluation': {'scores': {'overall_score': 0}, 'passed': False},
                    'error': str(e)
                })
    
    total_time = time.time() - start_time
    
    # Generate automated report
    print(f"\n📈 Generating comprehensive report...")
    reporter = ComprehensiveBenchmarkReporter()
    report_file = reporter.generate_comprehensive_report()
    
    # Print summary
    successful_tests = len([r for r in results if r['evaluation']['passed']])
    avg_score = sum(r['evaluation']['scores']['overall_score'] for r in results) / len(results)
    
    print("\n" + "=" * 60)
    print("🎯 AUTOMATED BENCHMARK COMPLETE")
    print("=" * 60)
    print(f"⏱️  Total Time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
    print(f"📊 Tests Run: {len(results)}")
    print(f"✅ Passed: {successful_tests} ({successful_tests/len(results)*100:.1f}%)")
    print(f"📈 Average Score: {avg_score:.1f}/100")
    print(f"📄 Full Report: {report_file}")
    print("=" * 60)
    
    return results

def run_continuous_benchmarks(interval_hours=24):
    """Run benchmarks continuously every N hours."""
    print(f"🔄 Starting continuous benchmarking (every {interval_hours} hours)")
    
    while True:
        try:
            print(f"\n⏰ {time.strftime('%Y-%m-%d %H:%M:%S')} - Running scheduled benchmark")
            run_automated_benchmarks()
            
            print(f"😴 Sleeping for {interval_hours} hours until next run...")
            time.sleep(interval_hours * 3600)
            
        except KeyboardInterrupt:
            print("\n🛑 Continuous benchmarking stopped by user")
            break
        except Exception as e:
            print(f"❌ Error in continuous benchmarking: {e}")
            print("⏱️  Retrying in 1 hour...")
            time.sleep(3600)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Fully automated benchmark runner')
    parser.add_argument('--continuous', action='store_true', 
                       help='Run continuously every 24 hours')
    parser.add_argument('--interval', type=int, default=24,
                       help='Hours between continuous runs (default: 24)')
    
    args = parser.parse_args()
    
    if args.continuous:
        run_continuous_benchmarks(args.interval)
    else:
        run_automated_benchmarks()