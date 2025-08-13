#!/usr/bin/env python3
"""
Clean benchmark runner - Main entry point for all benchmarks
Uses only HuggingFace datasets and clean evaluation methods
"""
import argparse
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import core modules
from benchmark_runner import run_benchmark, SCENARIO_CONFIGS, MODEL_CONFIGS
from batch_runner import run_batch_benchmarks
from auto_dataset_runner import run_automated_benchmarks
from comprehensive_report import ComprehensiveBenchmarkReporter

def main():
    """Main entry point for benchmark execution."""
    parser = argparse.ArgumentParser(
        description='🚀 Comprehensive AI Benchmark Suite with HuggingFace Integration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single benchmark with HuggingFace dataset
  python run_benchmark.py --scenario human_eval --model gpt4o
  
  # Multiple scenarios and models
  python run_benchmark.py --batch --scenarios human_eval swe_bench --models gpt4o claude_3_5_sonnet
  
  # Fully automated with all available models
  python run_benchmark.py --auto
  
  # Generate visualization report
  python run_benchmark.py --report

Available Scenarios:
  human_eval     - HumanEval code generation (HuggingFace)
  swe_bench      - Software engineering tasks (HuggingFace) 
  gaia_tasks     - General AI assistant tasks (HuggingFace)
  web_navigation - Web automation scenarios (WebArena-style)
  tool_bench     - Tool usage and API workflows (ToolBench-style)
  customer_support - Business application scenarios

Available Models:
  gpt4o, gpt4_turbo, claude_3_5_sonnet, claude_3_opus, 
  gemini_1_5_pro, gemini_1_5_flash, custom_api
        """
    )
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--batch', action='store_true', 
                           help='Run batch benchmarks across multiple scenarios/models')
    mode_group.add_argument('--auto', action='store_true',
                           help='Run fully automated benchmarks with all available models')
    mode_group.add_argument('--report', action='store_true',
                           help='Generate comprehensive visualization report')
    
    # Single benchmark options
    parser.add_argument('--scenario', choices=list(SCENARIO_CONFIGS.keys()),
                       help='Single benchmark scenario to run')
    parser.add_argument('--model', choices=list(MODEL_CONFIGS.keys()), 
                       default='gpt4o', help='Model to test (default: gpt4o)')
    
    # Batch benchmark options
    parser.add_argument('--scenarios', nargs='+', choices=list(SCENARIO_CONFIGS.keys()),
                       default=['human_eval', 'web_navigation'],
                       help='List of scenarios for batch mode')
    parser.add_argument('--models', nargs='+', choices=list(MODEL_CONFIGS.keys()),
                       default=['gpt4o'],
                       help='List of models for batch mode')
    
    # Task customization
    parser.add_argument('--task-description', 
                       help='Custom task description for supported scenarios')
    parser.add_argument('--limit', type=int,
                       help='Limit number of problems per dataset (for testing)')
    
    # Utility options
    parser.add_argument('--list-scenarios', action='store_true',
                       help='List available benchmark scenarios')
    parser.add_argument('--list-models', action='store_true', 
                       help='List available models')
    
    args = parser.parse_args()
    
    try:
        if args.list_scenarios:
            print("📊 Available Benchmark Scenarios:")
            for scenario, config in SCENARIO_CONFIGS.items():
                print(f"  • {scenario:15} - {scenario.replace('_', ' ').title()}")
                
        elif args.list_models:
            print("🤖 Available Models:")
            for model in MODEL_CONFIGS.keys():
                print(f"  • {model}")
                
        elif args.report:
            print("📈 Generating comprehensive benchmark report...")
            reporter = ComprehensiveBenchmarkReporter()
            report_file = reporter.generate_comprehensive_report()
            print(f"✅ Report generated: {report_file}")
            
        elif args.auto:
            print("🤖 Starting fully automated benchmark suite...")
            run_automated_benchmarks()
            
        elif args.batch:
            print(f"📊 Running batch benchmarks...")
            task_params = {}
            if args.task_description:
                task_params['task_description'] = args.task_description
                task_params['issue_description'] = args.task_description  
                task_params['problem_list'] = args.task_description
            
            run_batch_benchmarks(args.scenarios, args.models, task_params)
            
        elif args.scenario:
            print(f"🎯 Running single benchmark: {args.scenario} with {args.model}")
            task_params = {}
            if args.task_description:
                task_params['task_description'] = args.task_description
                task_params['issue_description'] = args.task_description
                task_params['problem_list'] = args.task_description
            if args.limit:
                task_params['limit'] = args.limit
            
            result = run_benchmark(args.scenario, args.model, task_params)
            print("✅ Benchmark completed successfully!")
            
        else:
            print("🚀 Welcome to the AI Benchmark Suite!")
            print("Use --help to see all available options.")
            print("\nQuick start:")
            print("  python run_benchmark.py --scenario human_eval --model gpt4o")
            print("  python run_benchmark.py --auto")
            print("  python run_benchmark.py --report")
            
    except KeyboardInterrupt:
        print("\n🛑 Benchmark interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())