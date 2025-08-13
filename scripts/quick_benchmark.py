#!/usr/bin/env python3
"""
Quick Benchmark Script - Simple commands to run common benchmark tasks
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle output."""
    print(f"\n🚀 {description}")
    print(f"Running: {cmd}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"⚠️  Stderr: {result.stderr}")
            
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
        else:
            print(f"❌ {description} failed with return code {result.returncode}")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False

def check_environment():
    """Check if environment is set up correctly."""
    print("🔍 Checking environment...")
    
    # Check if we're in the right directory
    if not Path("run_benchmark.py").exists():
        print("❌ run_benchmark.py not found. Make sure you're in the benchmark directory.")
        return False
    
    # Check for .env file or environment variables
    api_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"]
    found_keys = []
    
    for key in api_keys:
        if os.getenv(key):
            found_keys.append(key)
    
    if not found_keys:
        print("⚠️  No API keys found in environment variables.")
        print("Set at least one API key:")
        for key in api_keys:
            print(f"  export {key}='your-key-here'")
        return False
    
    print(f"✅ Found API keys: {', '.join(found_keys)}")
    return True

def main():
    """Main script with menu options."""
    print("🎯 Quick Benchmark Script")
    print("=" * 40)
    
    if not check_environment():
        print("\n🛑 Environment check failed. Please fix issues above.")
        return 1
    
    while True:
        print("\n📋 Available Commands:")
        print("1. Run HumanEval with GPT-4o")
        print("2. Run Web Navigation with GPT-4o") 
        print("3. Run Quick Test (HumanEval with 5 problems)")
        print("4. Run Batch Test (HumanEval + Web Navigation)")
        print("5. Run Full Automated Test")
        print("6. Generate Report from Existing Results")
        print("7. List Available Scenarios")
        print("8. List Available Models")
        print("9. Clean Results Directory")
        print("0. Exit")
        
        choice = input("\n🎮 Enter your choice (0-9): ").strip()
        
        if choice == "0":
            print("👋 Goodbye!")
            break
            
        elif choice == "1":
            success = run_command(
                "python run_benchmark.py --scenario human_eval --model gpt4o",
                "HumanEval with GPT-4o"
            )
            
        elif choice == "2":
            success = run_command(
                "python run_benchmark.py --scenario web_navigation --model gpt4o",
                "Web Navigation with GPT-4o"
            )
            
        elif choice == "3":
            success = run_command(
                "python run_benchmark.py --scenario human_eval --model gpt4o --limit 5",
                "Quick HumanEval Test (5 problems)"
            )
            
        elif choice == "4":
            success = run_command(
                "python run_benchmark.py --batch --scenarios human_eval web_navigation --models gpt4o",
                "Batch Test (HumanEval + Web Navigation)"
            )
            
        elif choice == "5":
            success = run_command(
                "python run_benchmark.py --auto",
                "Full Automated Benchmark"
            )
            
        elif choice == "6":
            success = run_command(
                "python run_benchmark.py --report",
                "Generate Visualization Report"
            )
            
        elif choice == "7":
            success = run_command(
                "python run_benchmark.py --list-scenarios",
                "List Available Scenarios"
            )
            
        elif choice == "8":
            success = run_command(
                "python run_benchmark.py --list-models",
                "List Available Models"
            )
            
        elif choice == "9":
            print("\n🗑️  Clean Results Directory")
            confirm = input("Are you sure you want to delete all results? (y/N): ").strip().lower()
            if confirm == 'y':
                success = run_command(
                    "rm -rf results/* reports/*",
                    "Clean Results and Reports"
                )
                if success:
                    print("✅ Results directory cleaned")
            else:
                print("❌ Operation cancelled")
                
        else:
            print("❌ Invalid choice. Please enter a number between 0-9.")
            continue
            
        if choice in ["1", "2", "3", "4", "5", "6"]:
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    exit(main())