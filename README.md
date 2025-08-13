# AgentBench - Comprehensive AI Benchmark Suite

Production-ready benchmarking framework testing AI models across 5 core capabilities using real academic datasets. Features optimized evaluators, function calling support, and detailed performance analytics.

## Quick Start

```bash
# Setup environment
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Configure API (Railway deployment)
cp .env.railway .env
# Edit .env with Railway URL and API key

# AUTOMATED BENCHMARKING (Recommended)
python auto_dataset_runner.py --continuous  # Zero intervention required
python auto_dataset_runner.py --models custom_api --scenarios all  # Full suite

# BATCH OPERATIONS
python batch_runner.py --scenarios human_eval swe_bench --models custom_api
python batch_runner.py --all-scenarios --model custom_api  # All scenarios

# INTERACTIVE MENU
python scripts/quick_benchmark.py  # User-friendly menu interface

# COMPREHENSIVE REPORTS
python comprehensive_report.py --generate  # Generate visual reports
```

## Benchmark Coverage

| Scenario | Tests | Dataset | API Capability |
|----------|-------|---------|----------------|
| **HumanEval** | Code Generation | HF: 164 problems | Live code execution |
| **SWE-bench** | Software Engineering | HF: 2K+ problems | Code analysis tools |
| **Web Navigation** | UI Automation | WebArena-style tasks | Multi-step workflows |
| **Tool Bench** | Function Calling | API workflows | Data mapping between functions |
| **Customer Support** | Problem Solving | Business scenarios | Real-world task completion |

## Railway API Integration

Configured for Railway deployment with function calling support:
- **Model**: `small-1`
- **Function Calling**: Live code execution, analysis tools, web navigation
- **Data Mapping**: Output from function A flows to function B
- **Streaming**: Complete responses for comprehensive evaluation

## Usage Options

### Automated Benchmarking (Zero Intervention)
```bash
# Full automation with HuggingFace datasets
python auto_dataset_runner.py --continuous --interval 6  # Every 6 hours
python auto_dataset_runner.py --models custom_api --scenarios all
python auto_dataset_runner.py --quick-test  # Fast validation run
```

### Batch Operations
```bash
# Multiple scenarios and models
python batch_runner.py --scenarios human_eval swe_bench tool_bench --models custom_api
python batch_runner.py --all-scenarios --model custom_api
python batch_runner.py --comparison --models custom_api gpt4o  # Compare performance
```

### Interactive Menu
```bash
python scripts/quick_benchmark.py
# Options: Single test, batch run, reports, environment check
```

### Individual Benchmarks
```bash
# Single benchmark (basic usage)
python benchmark_runner.py --scenario human_eval --model custom_api
python benchmark_runner.py --list-scenarios  # See all options
```

### Report Generation
```bash
python comprehensive_report.py --generate  # HTML reports with visualizations
python comprehensive_report.py --comparison  # Compare multiple runs
```

## Benchmark Flow

```
Dataset Load → Prompt Generation → API Call → Function Calling → Response Evaluation → Score Report
```

1. **Real Dataset Loading**: HuggingFace datasets (HumanEval, SWE-bench, GAIA)
2. **Prompt Customization**: Scenario-specific prompts with actual problems
3. **API Integration**: Railway endpoint with function calling tools
4. **Function Execution**: Live code execution, analysis, web navigation
5. **Optimized Evaluation**: Streamlined evaluators with detailed scoring
6. **Performance Analytics**: Comprehensive reports with actionable feedback

## Key Features

- **Function Calling Support** - Execute code, analyze data, navigate web interfaces  
- **Real Dataset Integration** - HuggingFace datasets, no synthetic data  
- **Optimized Evaluators** - 30-60% code reduction, improved accuracy  
- **Data Flow Mapping** - Chain function outputs as inputs to next functions  
- **Railway Ready** - Configured for Railway deployment with proper error handling  
- **Comprehensive Scoring** - Detailed metrics across all AI capabilities  

## Architecture

```
AgentBench/
├── benchmark_runner.py     # Main benchmark orchestrator
├── models/
│   └── custom_model_client.py  # Railway API integration
├── scenarios/              # Benchmark prompts & datasets
│   ├── human_eval/         # Code generation scenarios
│   ├── swe_bench/          # Software engineering tasks  
│   ├── web_navigation/     # UI automation workflows
│   ├── tool_bench/         # Function calling tests
│   └── customer_support/   # Real-world problem solving
├── evals/                  # Optimized evaluation functions
└── results/                # Performance reports & analytics
```

## Performance Tracking

Each benchmark generates detailed performance metrics:
- **Overall Score**: Weighted performance across all components
- **Component Scores**: Individual capability assessment  
- **Function Usage**: Tool selection and execution efficiency
- **Error Analysis**: Failure patterns and improvement suggestions
- **Completion Rates**: Task success percentages

Production-ready framework for comprehensive AI model evaluation.