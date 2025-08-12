#!/usr/bin/env python3
"""
AI Model Comparison Runner

Runs benchmarks across multiple models and generates comparison reports
"""

import argparse
from batch_runner import run_multiple_benchmarks
from visualize_results import save_visualizations
import time

def compare_all_models(scenarios=None, models=None):
    """Run comprehensive comparison across all models"""
    
    # Default models and scenarios
    if scenarios is None:
        scenarios = ['customer_support']
    
    if models is None:
        models = ['incredible_api', 'openai_gpt4']
    
    print("🚀 Starting Comprehensive Model Comparison")
    print(f"📊 Testing {len(models)} models on {len(scenarios)} scenarios")
    print(f"🤖 Models: {', '.join(models)}")
    print(f"🎭 Scenarios: {', '.join(scenarios)}")
    print("="*60)
    
    # Record start time
    start_time = time.time()
    
    # Run all benchmarks
    run_multiple_benchmarks(scenarios, models)
    
    # Calculate total time
    total_time = time.time() - start_time
    
    print("\n" + "="*60)
    print("🎯 All benchmarks completed!")
    print(f"⏱️ Total execution time: {total_time:.2f} seconds")
    print("📈 Generating visualizations...")
    
    # Generate visualizations
    save_visualizations()
    
    print("\n✅ Model comparison complete!")
    print("📊 Check the 'visualizations/' directory for results")
    print("🌐 Open 'visualizations/benchmark_comparison.html' for interactive dashboard")

def main():
    parser = argparse.ArgumentParser(description='Compare AI models across benchmarks')
    parser.add_argument('--scenarios', nargs='+', default=['customer_support'],
                       help='Scenarios to test')
    parser.add_argument('--models', nargs='+', default=['incredible_api', 'openai_gpt4'],
                       help='Models to compare')
    
    args = parser.parse_args()
    
    compare_all_models(args.scenarios, args.models)

if __name__ == "__main__":
    main()