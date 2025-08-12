#!/usr/bin/env python3
"""
Demo script showing how real benchmark datasets work vs expected.json files
"""

def demo_human_eval():
    """Demo HumanEval with real test execution."""
    print("🧮 HumanEval Demo - Real Test Execution")
    print("="*50)
    
    # Load real HumanEval problem
    from scenarios.human_eval.dataset import get_human_eval_problems, execute_test
    
    problems = get_human_eval_problems()
    problem = problems[0]  # First problem
    
    print(f"📋 Problem: {problem['task_id']}")
    print(f"🎯 Task: Extract decimal part of a number")
    print(f"📝 Prompt:\n{problem['prompt']}")
    
    # Test with correct solution
    print("\n✅ Testing CORRECT solution:")
    correct_code = problem['prompt'] + problem['canonical_solution'] 
    result = execute_test(correct_code, problem['test'])
    print(f"Result: {result}")
    
    # Test with incorrect solution  
    print("\n❌ Testing INCORRECT solution:")
    incorrect_solution = "    return number - int(number)  # Wrong approach"
    incorrect_code = problem['prompt'] + incorrect_solution
    result = execute_test(incorrect_code, problem['test'])
    print(f"Result: {result}")

def demo_swe_bench():
    """Demo SWE-bench with real patch evaluation.""" 
    print("\n\n💻 SWE-bench Demo - Real Patch Evaluation")
    print("="*50)
    
    from scenarios.swe_bench.dataset import get_swe_bench_problems, evaluate_patch
    
    problems = get_swe_bench_problems()
    problem = problems[0]  # First problem
    
    print(f"📋 Problem: {problem['instance_id']}")
    print(f"🎯 Issue: {problem['problem_statement']}")
    print(f"📦 Repo: {problem['repo']}")
    
    # Test with correct patch
    print("\n✅ Testing CORRECT patch:")
    correct_patch = problem['patch']
    result = evaluate_patch(problem['instance_id'], correct_patch)
    print(f"Similarity: {result['patch_similarity']:.2f}")
    print(f"Passed: {result['passed']}")
    
    # Test with incorrect patch
    print("\n❌ Testing INCORRECT patch:")
    incorrect_patch = "--- a/some_file.py\n+++ b/some_file.py\n@@ -1,1 +1,1 @@\n-old_code\n+wrong_fix"
    result = evaluate_patch(problem['instance_id'], incorrect_patch)
    print(f"Similarity: {result['patch_similarity']:.2f}")
    print(f"Passed: {result['passed']}")

def compare_approaches():
    """Compare real benchmarks vs expected.json approach."""
    print("\n\n🔍 Real Benchmarks vs Expected.json Comparison")
    print("="*60)
    
    print("📊 REAL BENCHMARKS (What we now have):")
    print("✅ Uses actual test cases from HumanEval dataset")
    print("✅ Executes code against real test functions")
    print("✅ Provides accurate pass/fail results")
    print("✅ Matches research paper methodologies")
    print("✅ No manual expected.json maintenance")
    print("✅ Standardized evaluation metrics")
    
    print("\n📝 EXPECTED.JSON APPROACH (What we replaced):")
    print("❌ Manual creation of 'expected' results")
    print("❌ Subjective evaluation criteria")
    print("❌ No real test execution")
    print("❌ Maintenance overhead for each scenario")
    print("❌ Less accurate evaluation")
    print("❌ Doesn't match research standards")

if __name__ == "__main__":
    print("🚀 Comprehensive Agentic AI Benchmark Suite")
    print("Demo: Real Benchmark Datasets vs Expected.json")
    print("="*80)
    
    try:
        demo_human_eval()
        demo_swe_bench() 
        compare_approaches()
        
        print(f"\n\n🎯 CONCLUSION:")
        print("Real benchmark datasets provide:")
        print("• Accurate, standardized evaluation")
        print("• Actual test execution and validation") 
        print("• Research-grade methodology")
        print("• Automatic scoring without manual expected.json files")
        print("\nThis is why established benchmarks don't need expected.json! 🎉")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the benchmark directory and have the required dependencies.")
    except Exception as e:
        print(f"❌ Error: {e}")