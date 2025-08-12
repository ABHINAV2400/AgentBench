import json
import os
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from typing import Dict, List, Any
import numpy as np

RESULTS_DIR = Path(__file__).parent / 'results'
REPORTS_DIR = Path(__file__).parent / 'reports'
REPORTS_DIR.mkdir(exist_ok=True)

# Benchmark scenario categories
SCENARIO_CATEGORIES = {
    'customer_support': 'Business Applications',
    'web_navigation': 'Web Interaction',
    'swe_bench': 'Software Engineering',
    'human_eval': 'Code Generation',
    'gaia_tasks': 'General Intelligence',
    'tool_bench': 'Tool Usage & APIs'
}

class ComprehensiveBenchmarkReporter:
    def __init__(self):
        self.results = []
        self.load_all_results()
    
    def load_all_results(self):
        """Load all benchmark results from the results directory."""
        if not RESULTS_DIR.exists():
            print("No results directory found")
            return
        
        for result_file in RESULTS_DIR.glob("*.json"):
            if result_file.name.startswith('batch_summary_'):
                continue  # Skip batch summaries
                
            try:
                with open(result_file, 'r') as f:
                    result = json.load(f)
                    result['filename'] = result_file.name
                    self.results.append(result)
            except Exception as e:
                print(f"Error loading {result_file}: {e}")
    
    def generate_comprehensive_report(self):
        """Generate a comprehensive HTML report with all benchmark results."""
        if not self.results:
            print("No results found to generate report")
            return
        
        # Prepare data
        df = self.prepare_dataframe()
        
        # Generate report sections
        html_content = self.generate_html_report(df)
        
        # Save report
        report_file = REPORTS_DIR / f"comprehensive_benchmark_report_{int(datetime.now().timestamp())}.html"
        with open(report_file, 'w') as f:
            f.write(html_content)
        
        # Generate plots
        self.generate_plots(df)
        
        print(f"📊 Comprehensive report generated: {report_file}")
        return report_file
    
    def prepare_dataframe(self):
        """Prepare pandas DataFrame from results."""
        data = []
        
        for result in self.results:
            evaluation = result.get('evaluation', {})
            scores = evaluation.get('scores', {})
            
            row = {
                'scenario': result.get('scenario', 'unknown'),
                'model': result.get('model', 'unknown'),
                'overall_score': scores.get('overall_score', 0),
                'passed': evaluation.get('passed', False),
                'execution_time': result.get('execution_time_sec', 0),
                'timestamp': result.get('timestamp', 0),
                'category': SCENARIO_CATEGORIES.get(result.get('scenario'), 'Other')
            }
            
            # Add scenario-specific scores
            for score_name, score_value in scores.items():
                if score_name != 'overall_score':
                    row[f'score_{score_name}'] = score_value
            
            data.append(row)
        
        return pd.DataFrame(data)
    
    def generate_html_report(self, df: pd.DataFrame) -> str:
        """Generate HTML report content."""
        # Calculate statistics
        stats = self.calculate_statistics(df)
        
        # Generate model comparison table
        model_comparison = self.generate_model_comparison_table(df)
        
        # Generate scenario analysis
        scenario_analysis = self.generate_scenario_analysis(df)
        
        # Generate performance trends
        performance_trends = self.generate_performance_trends(df)
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Comprehensive Benchmark Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #e9e9e9; border-radius: 5px; }}
                .metric h3 {{ margin: 0; color: #333; }}
                .metric p {{ margin: 5px 0 0 0; font-size: 24px; font-weight: bold; color: #007acc; }}
                table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .pass {{ color: #28a745; font-weight: bold; }}
                .fail {{ color: #dc3545; font-weight: bold; }}
                .chart {{ text-align: center; margin: 20px 0; }}
                .summary {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 Comprehensive Agentic AI Benchmark Report</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Total Results Analyzed: {len(df)}</p>
            </div>
            
            {stats}
            {model_comparison}
            {scenario_analysis}
            {performance_trends}
            
            <div class="section">
                <h2>📈 Visualizations</h2>
                <p>See the generated plot files in the reports directory for detailed visualizations.</p>
            </div>
            
            <div class="section">
                <h2>🔍 Detailed Results</h2>
                {self.generate_detailed_results_table(df)}
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def calculate_statistics(self, df: pd.DataFrame) -> str:
        """Calculate overall statistics."""
        total_tests = len(df)
        passed_tests = len(df[df['passed'] == True])
        avg_score = df['overall_score'].mean()
        avg_time = df['execution_time'].mean()
        
        unique_models = df['model'].nunique()
        unique_scenarios = df['scenario'].nunique()
        
        return f"""
        <div class="section">
            <h2>📊 Overall Statistics</h2>
            <div class="metric">
                <h3>Total Tests</h3>
                <p>{total_tests}</p>
            </div>
            <div class="metric">
                <h3>Tests Passed</h3>
                <p>{passed_tests} ({passed_tests/total_tests*100:.1f}%)</p>
            </div>
            <div class="metric">
                <h3>Average Score</h3>
                <p>{avg_score:.1f}/100</p>
            </div>
            <div class="metric">
                <h3>Average Time</h3>
                <p>{avg_time:.2f}s</p>
            </div>
            <div class="metric">
                <h3>Models Tested</h3>
                <p>{unique_models}</p>
            </div>
            <div class="metric">
                <h3>Scenarios Covered</h3>
                <p>{unique_scenarios}</p>
            </div>
        </div>
        """
    
    def generate_model_comparison_table(self, df: pd.DataFrame) -> str:
        """Generate model comparison table."""
        model_stats = df.groupby('model').agg({
            'overall_score': ['mean', 'std', 'count'],
            'passed': 'sum',
            'execution_time': 'mean'
        }).round(2)
        
        model_stats.columns = ['Avg_Score', 'Score_Std', 'Total_Tests', 'Tests_Passed', 'Avg_Time']
        model_stats['Pass_Rate'] = (model_stats['Tests_Passed'] / model_stats['Total_Tests'] * 100).round(1)
        
        table_html = "<table><thead><tr><th>Model</th><th>Avg Score</th><th>Std Dev</th><th>Pass Rate</th><th>Tests</th><th>Avg Time (s)</th></tr></thead><tbody>"
        
        for model, row in model_stats.iterrows():
            pass_rate_class = "pass" if row['Pass_Rate'] >= 70 else "fail"
            table_html += f"""
            <tr>
                <td><strong>{model}</strong></td>
                <td>{row['Avg_Score']:.1f}</td>
                <td>{row['Score_Std']:.1f}</td>
                <td class="{pass_rate_class}">{row['Pass_Rate']:.1f}%</td>
                <td>{int(row['Total_Tests'])}</td>
                <td>{row['Avg_Time']:.2f}</td>
            </tr>
            """
        
        table_html += "</tbody></table>"
        
        return f"""
        <div class="section">
            <h2>🤖 Model Performance Comparison</h2>
            {table_html}
        </div>
        """
    
    def generate_scenario_analysis(self, df: pd.DataFrame) -> str:
        """Generate scenario-by-scenario analysis."""
        scenario_stats = df.groupby('scenario').agg({
            'overall_score': ['mean', 'std'],
            'passed': ['sum', 'count'],
            'execution_time': 'mean'
        }).round(2)
        
        scenario_stats.columns = ['Avg_Score', 'Score_Std', 'Tests_Passed', 'Total_Tests', 'Avg_Time']
        scenario_stats['Pass_Rate'] = (scenario_stats['Tests_Passed'] / scenario_stats['Total_Tests'] * 100).round(1)
        
        table_html = "<table><thead><tr><th>Scenario</th><th>Category</th><th>Avg Score</th><th>Pass Rate</th><th>Models Tested</th><th>Avg Time (s)</th></tr></thead><tbody>"
        
        for scenario, row in scenario_stats.iterrows():
            category = SCENARIO_CATEGORIES.get(scenario, 'Other')
            models_tested = len(df[df['scenario'] == scenario]['model'].unique())
            pass_rate_class = "pass" if row['Pass_Rate'] >= 70 else "fail"
            
            table_html += f"""
            <tr>
                <td><strong>{scenario.replace('_', ' ').title()}</strong></td>
                <td>{category}</td>
                <td>{row['Avg_Score']:.1f}</td>
                <td class="{pass_rate_class}">{row['Pass_Rate']:.1f}%</td>
                <td>{models_tested}</td>
                <td>{row['Avg_Time']:.2f}</td>
            </tr>
            """
        
        table_html += "</tbody></table>"
        
        return f"""
        <div class="section">
            <h2>📋 Scenario Analysis</h2>
            {table_html}
        </div>
        """
    
    def generate_performance_trends(self, df: pd.DataFrame) -> str:
        """Generate performance trends analysis."""
        if len(df) < 2:
            return "<div class='section'><h2>📈 Performance Trends</h2><p>Insufficient data for trend analysis.</p></div>"
        
        # Find best and worst performing combinations
        best_result = df.loc[df['overall_score'].idxmax()]
        worst_result = df.loc[df['overall_score'].idxmin()]
        
        # Category analysis
        category_stats = df.groupby('category')['overall_score'].agg(['mean', 'count']).round(2)
        
        category_table = "<table><thead><tr><th>Category</th><th>Avg Score</th><th>Tests</th></tr></thead><tbody>"
        for category, row in category_stats.iterrows():
            category_table += f"<tr><td>{category}</td><td>{row['mean']:.1f}</td><td>{int(row['count'])}</td></tr>"
        category_table += "</tbody></table>"
        
        return f"""
        <div class="section">
            <h2>📈 Performance Insights</h2>
            
            <div class="summary">
                <h3>🏆 Best Performance</h3>
                <p><strong>{best_result['model']}</strong> on <strong>{best_result['scenario']}</strong>: {best_result['overall_score']:.1f}/100</p>
            </div>
            
            <div class="summary">
                <h3>📉 Lowest Performance</h3>
                <p><strong>{worst_result['model']}</strong> on <strong>{worst_result['scenario']}</strong>: {worst_result['overall_score']:.1f}/100</p>
            </div>
            
            <h3>Performance by Category</h3>
            {category_table}
        </div>
        """
    
    def generate_detailed_results_table(self, df: pd.DataFrame) -> str:
        """Generate detailed results table."""
        table_html = "<table><thead><tr><th>Scenario</th><th>Model</th><th>Score</th><th>Status</th><th>Time (s)</th><th>Date</th></tr></thead><tbody>"
        
        for _, row in df.iterrows():
            status_class = "pass" if row['passed'] else "fail"
            status_text = "PASS" if row['passed'] else "FAIL"
            date_str = datetime.fromtimestamp(row['timestamp']).strftime('%Y-%m-%d %H:%M') if row['timestamp'] > 0 else 'Unknown'
            
            table_html += f"""
            <tr>
                <td>{row['scenario'].replace('_', ' ').title()}</td>
                <td>{row['model']}</td>
                <td>{row['overall_score']:.1f}</td>
                <td class="{status_class}">{status_text}</td>
                <td>{row['execution_time']:.2f}</td>
                <td>{date_str}</td>
            </tr>
            """
        
        table_html += "</tbody></table>"
        return table_html
    
    def generate_plots(self, df: pd.DataFrame):
        """Generate visualization plots."""
        plt.style.use('seaborn-v0_8')
        fig_size = (12, 8)
        
        # 1. Model Performance Comparison
        plt.figure(figsize=fig_size)
        model_scores = df.groupby('model')['overall_score'].mean().sort_values(ascending=False)
        plt.bar(range(len(model_scores)), model_scores.values)
        plt.xticks(range(len(model_scores)), model_scores.index, rotation=45, ha='right')
        plt.ylabel('Average Score')
        plt.title('Model Performance Comparison')
        plt.axhline(y=70, color='r', linestyle='--', label='Passing Threshold')
        plt.legend()
        plt.tight_layout()
        plt.savefig(REPORTS_DIR / 'model_performance_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Scenario Difficulty Analysis
        plt.figure(figsize=fig_size)
        scenario_scores = df.groupby('scenario')['overall_score'].mean().sort_values(ascending=True)
        plt.barh(range(len(scenario_scores)), scenario_scores.values)
        plt.yticks(range(len(scenario_scores)), [s.replace('_', ' ').title() for s in scenario_scores.index])
        plt.xlabel('Average Score')
        plt.title('Scenario Difficulty Analysis (Lower Score = More Difficult)')
        plt.axvline(x=70, color='r', linestyle='--', label='Passing Threshold')
        plt.legend()
        plt.tight_layout()
        plt.savefig(REPORTS_DIR / 'scenario_difficulty_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Score Distribution Heatmap
        if len(df) > 0:
            plt.figure(figsize=(14, 8))
            pivot_data = df.pivot_table(values='overall_score', index='scenario', columns='model', aggfunc='mean')
            sns.heatmap(pivot_data, annot=True, cmap='RdYlGn', center=70, fmt='.1f')
            plt.title('Performance Heatmap: Scenario vs Model')
            plt.ylabel('Scenario')
            plt.xlabel('Model')
            plt.tight_layout()
            plt.savefig(REPORTS_DIR / 'performance_heatmap.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 4. Execution Time Analysis
        plt.figure(figsize=fig_size)
        df.boxplot(column='execution_time', by='scenario', ax=plt.gca())
        plt.title('Execution Time Distribution by Scenario')
        plt.xlabel('Scenario')
        plt.ylabel('Execution Time (seconds)')
        plt.xticks(rotation=45, ha='right')
        plt.suptitle('')  # Remove default title
        plt.tight_layout()
        plt.savefig(REPORTS_DIR / 'execution_time_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Generated {4} visualization plots in {REPORTS_DIR}")
    
    def generate_summary_stats(self):
        """Generate summary statistics."""
        if not self.results:
            return {}
        
        df = self.prepare_dataframe()
        
        return {
            'total_tests': len(df),
            'unique_models': df['model'].nunique(),
            'unique_scenarios': df['scenario'].nunique(),
            'overall_pass_rate': (df['passed'].sum() / len(df) * 100),
            'average_score': df['overall_score'].mean(),
            'best_model': df.groupby('model')['overall_score'].mean().idxmax(),
            'hardest_scenario': df.groupby('scenario')['overall_score'].mean().idxmin(),
            'easiest_scenario': df.groupby('scenario')['overall_score'].mean().idxmax()
        }

def main():
    """Main function to generate comprehensive report."""
    reporter = ComprehensiveBenchmarkReporter()
    
    if not reporter.results:
        print("❌ No benchmark results found. Run some benchmarks first!")
        return
    
    print(f"📊 Found {len(reporter.results)} benchmark results")
    
    # Generate comprehensive report
    report_file = reporter.generate_comprehensive_report()
    
    # Print summary
    stats = reporter.generate_summary_stats()
    print("\n" + "="*60)
    print("📈 BENCHMARK SUMMARY")
    print("="*60)
    print(f"Total Tests: {stats['total_tests']}")
    print(f"Models Tested: {stats['unique_models']}")
    print(f"Scenarios Covered: {stats['unique_scenarios']}")
    print(f"Overall Pass Rate: {stats['overall_pass_rate']:.1f}%")
    print(f"Average Score: {stats['average_score']:.1f}/100")
    print(f"Best Model: {stats['best_model']}")
    print(f"Hardest Scenario: {stats['hardest_scenario']}")
    print(f"Easiest Scenario: {stats['easiest_scenario']}")
    print("="*60)
    print(f"📄 Full report: {report_file}")
    print(f"📊 Plots saved in: {REPORTS_DIR}")

if __name__ == "__main__":
    main()