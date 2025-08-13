# 🚀 AI Benchmark Suite

Comprehensive benchmarking framework for agentic AI models using HuggingFace datasets. Features improved evaluators with enhanced solution parsing, detailed feedback, and professional reporting.

## ⚡ Quick Start

```bash
# Setup
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Set API keys
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key" 
export GOOGLE_API_KEY="your-key"

# Run benchmarks
python run_benchmark.py --scenario human_eval --model gpt4o
python run_benchmark.py --auto  # Automated testing
python run_benchmark.py --report  # Generate visualizations

# Interactive menu (recommended)
python scripts/quick_benchmark.py
```

## 📊 Available Benchmarks

- **🧮 HumanEval** - Code generation (HuggingFace dataset, 164 problems)
- **💻 SWE-bench** - Software engineering (HuggingFace dataset, 2K+ problems) 
- **🧠 GAIA** - General intelligence (HuggingFace dataset, 466 tasks)
- **🌐 Web Navigation** - Browser automation (WebArena-style)
- **🔧 Tool Usage** - API workflows (ToolBench-style)
- **💼 Customer Support** - Business scenarios

## 🤖 Supported Models

**OpenAI:** `gpt4o`, `gpt4_turbo`  
**Anthropic:** `claude_3_5_sonnet`, `claude_3_opus`  
**Google:** `gemini_1_5_pro`, `gemini_1_5_flash`  
**Custom:** `custom_api`

## 🎯 Usage

### Interactive Menu (Recommended)
```bash
python scripts/quick_benchmark.py
# Provides easy menu for all common tasks
```

### Command Line
```bash
# Single test
python run_benchmark.py --scenario human_eval --model gpt4o

# Quick test (3 problems)
python run_benchmark.py --scenario human_eval --model gpt4o --limit 3

# Multiple scenarios/models  
python run_benchmark.py --batch --scenarios human_eval swe_bench --models gpt4o claude_3_5_sonnet

# Fully automated
python run_benchmark.py --auto

# Generate reports
python run_benchmark.py --report

# List options
python run_benchmark.py --list-scenarios
python run_benchmark.py --list-models
```

## 📈 Key Features

✅ **Enhanced Evaluators** - Improved solution parsing, better feedback, detailed metrics  
✅ **HuggingFace Integration** - Real datasets, no manual test data  
✅ **Smart Parsing** - Multiple strategies for extracting solutions from responses  
✅ **Detailed Feedback** - Actionable insights with completion rates and diagnostics  
✅ **Interactive Script** - User-friendly menu for common tasks  
✅ **Professional Reporting** - Interactive visualizations and analytics  
✅ **Full Automation** - Zero intervention after API key setup  

## 🎛️ Interactive Menu

The `scripts/quick_benchmark.py` provides:
- Environment validation
- Pre-configured test scenarios  
- Batch operations
- Result management
- Real-time feedback

## 🏗️ Structure

```
benchmark/
├── run_benchmark.py        # Main entry point
├── scripts/
│   └── quick_benchmark.py  # Interactive menu script
├── models/                 # AI model integrations  
├── scenarios/              # Benchmark datasets & prompts
├── evals/                  # Enhanced evaluation functions
├── results/                # Generated results
└── reports/                # Visualizations
```

## 🔧 Recent Improvements

**Enhanced Evaluators:**
- **HumanEval**: Better solution parsing, multiple extraction strategies, improved scoring
- **Web Navigation**: Advanced response parsing, reasoning quality assessment, detailed feedback
- **Diagnostics**: Solution attempt tracking, error categorization, actionable suggestions

**Quick Benchmark Script:**
- Interactive menu with 9 common operations
- Environment checking and validation  
- Real-time command execution with feedback
- Batch operations and result management

Built for reliable AI evaluation with research-grade accuracy. 🎯