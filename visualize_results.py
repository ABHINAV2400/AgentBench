#!/usr/bin/env python3
"""
AI Agent Benchmark Results Visualization System

Creates comprehensive charts and comparisons of benchmark results
"""

import json
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
from pathlib import Path

def load_all_results(results_dir="results"):
    """Load all benchmark result files"""
    results = []
    result_files = glob.glob(f"{results_dir}/*.json")
    
    for file_path in result_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                # Extract scenario and model from filename
                filename = os.path.basename(file_path)
                parts = filename.replace('.json', '').split('--')
                data['scenario'] = parts[0]
                data['model'] = parts[1] if len(parts) > 1 else 'unknown'
                data['file_path'] = file_path
                results.append(data)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    return results

def extract_score_data(results):
    """Extract detailed scoring data for visualization"""
    data_rows = []
    
    for result in results:
        model = result.get('model', 'unknown')
        scenario = result.get('scenario', 'unknown')
        
        # Overall metrics
        overall_score = result.get('score', {}).get('overall_score', 0)
        passed = result.get('score', {}).get('passed', False)
        execution_time = result.get('execution_time_sec', 0)
        
        # Detailed scores
        detailed = result.get('score', {}).get('detailed_scores', {})
        
        workflow_score = detailed.get('workflow_completion', {}).get('workflow_score', 0)
        database_score = detailed.get('database_accuracy', {}).get('database_accuracy_score', 0)
        api_score = detailed.get('api_usage', {}).get('api_usage_score', 0)
        quality_score = detailed.get('response_quality', {}).get('response_quality_score', 0)
        
        # Execution summary
        summary = result.get('score', {}).get('execution_summary', {})
        api_calls = summary.get('total_api_calls', 0)
        db_changes = summary.get('total_database_changes', 0)
        workflow_states = summary.get('total_workflow_states', 0)
        
        data_rows.append({
            'model': model,
            'scenario': scenario,
            'overall_score': overall_score,
            'passed': passed,
            'execution_time': execution_time,
            'workflow_score': workflow_score,
            'database_score': database_score,
            'api_score': api_score,
            'quality_score': quality_score,
            'total_api_calls': api_calls,
            'total_db_changes': db_changes,
            'total_workflow_states': workflow_states
        })
    
    return pd.DataFrame(data_rows)

def create_score_comparison_chart(df):
    """Create interactive score comparison chart"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Overall Performance', 'Detailed Score Breakdown', 
                       'Execution Metrics', 'Pass/Fail Status'),
        specs=[[{"secondary_y": False}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "pie"}]]
    )
    
    # Overall Performance (radar chart style)
    models = df['model'].unique()
    colors = px.colors.qualitative.Set1[:len(models)]
    
    for i, model in enumerate(models):
        model_data = df[df['model'] == model]
        fig.add_trace(
            go.Scatter(
                x=['Workflow', 'Database', 'API Usage', 'Quality'],
                y=[
                    model_data['workflow_score'].mean(),
                    model_data['database_score'].mean(), 
                    model_data['api_score'].mean(),
                    model_data['quality_score'].mean()
                ],
                mode='lines+markers',
                name=f'{model} - Detailed Scores',
                line_color=colors[i],
                fill='toself' if i == 0 else None
            ),
            row=1, col=1
        )
    
    # Overall Score Bar Chart
    fig.add_trace(
        go.Bar(
            x=df['model'],
            y=df['overall_score'],
            name='Overall Score',
            marker_color=colors[:len(df)],
            text=[f"{score:.2%}" for score in df['overall_score']],
            textposition='auto'
        ),
        row=1, col=2
    )
    
    # Execution Metrics
    fig.add_trace(
        go.Bar(
            x=df['model'], 
            y=df['execution_time'],
            name='Execution Time (sec)',
            marker_color='lightblue',
            text=[f"{time:.3f}s" for time in df['execution_time']],
            textposition='auto'
        ),
        row=2, col=1
    )
    
    # Pass/Fail Pie Chart
    pass_fail_counts = df['passed'].value_counts()
    fig.add_trace(
        go.Pie(
            labels=['Passed', 'Failed'],
            values=[pass_fail_counts.get(True, 0), pass_fail_counts.get(False, 0)],
            marker_colors=['green', 'red']
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title_text="AI Model Benchmark Comparison Dashboard",
        showlegend=True,
        height=800
    )
    
    return fig

def create_detailed_breakdown_chart(results):
    """Create detailed breakdown of model performance"""
    fig = go.Figure()
    
    models = []
    workflow_scores = []
    database_scores = []
    api_scores = []
    quality_scores = []
    
    for result in results:
        model = result.get('model', 'unknown')
        detailed = result.get('score', {}).get('detailed_scores', {})
        
        models.append(model)
        workflow_scores.append(detailed.get('workflow_completion', {}).get('workflow_score', 0))
        database_scores.append(detailed.get('database_accuracy', {}).get('database_accuracy_score', 0))
        api_scores.append(detailed.get('api_usage', {}).get('api_usage_score', 0))
        quality_scores.append(detailed.get('response_quality', {}).get('response_quality_score', 0))
    
    # Create stacked bar chart
    fig.add_trace(go.Bar(name='Workflow Completion', x=models, y=workflow_scores))
    fig.add_trace(go.Bar(name='Database Accuracy', x=models, y=database_scores))
    fig.add_trace(go.Bar(name='API Usage', x=models, y=api_scores))
    fig.add_trace(go.Bar(name='Response Quality', x=models, y=quality_scores))
    
    fig.update_layout(
        title='Detailed Performance Breakdown by Category',
        xaxis_title='AI Models',
        yaxis_title='Score (0.0 - 1.0)',
        barmode='group',
        height=500
    )
    
    return fig

def create_execution_analysis_chart(df):
    """Create execution analysis visualization"""
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('API Calls Made', 'Database Changes', 'Workflow States'),
        specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]]
    )
    
    # API Calls
    fig.add_trace(
        go.Bar(x=df['model'], y=df['total_api_calls'], name='API Calls',
               marker_color='lightcoral'),
        row=1, col=1
    )
    
    # Database Changes
    fig.add_trace(
        go.Bar(x=df['model'], y=df['total_db_changes'], name='DB Changes',
               marker_color='lightgreen'),
        row=1, col=2  
    )
    
    # Workflow States
    fig.add_trace(
        go.Bar(x=df['model'], y=df['total_workflow_states'], name='Workflow States',
               marker_color='lightblue'),
        row=1, col=3
    )
    
    fig.update_layout(
        title='Model Execution Analysis - Actions Taken',
        showlegend=False,
        height=400
    )
    
    return fig

def generate_summary_report(results):
    """Generate text summary of benchmark results"""
    df = extract_score_data(results)
    
    report = []
    report.append("# AI Agent Benchmark Summary Report\n")
    report.append(f"**Total Tests Run**: {len(results)}")
    report.append(f"**Models Tested**: {', '.join(df['model'].unique())}")
    report.append(f"**Scenarios Tested**: {', '.join(df['scenario'].unique())}\n")
    
    # Overall Performance
    report.append("## Overall Performance Rankings")
    ranked = df.nlargest(10, 'overall_score')
    for idx, row in ranked.iterrows():
        status = "✅ PASSED" if row['passed'] else "❌ FAILED"
        report.append(f"**{row['model']}**: {row['overall_score']:.1%} {status}")
    
    report.append("\n## Detailed Analysis")
    
    # Best performers by category
    report.append(f"**🏆 Best Workflow Execution**: {df.loc[df['workflow_score'].idxmax(), 'model']} ({df['workflow_score'].max():.1%})")
    report.append(f"**💾 Best Database Accuracy**: {df.loc[df['database_score'].idxmax(), 'model']} ({df['database_score'].max():.1%})")
    report.append(f"**🔗 Best API Usage**: {df.loc[df['api_score'].idxmax(), 'model']} ({df['api_score'].max():.1%})")
    report.append(f"**✍️ Best Response Quality**: {df.loc[df['quality_score'].idxmax(), 'model']} ({df['quality_score'].max():.1%})")
    
    # Performance insights
    report.append("\n## Key Insights")
    avg_score = df['overall_score'].mean()
    report.append(f"- Average benchmark score across all models: {avg_score:.1%}")
    
    fastest_model = df.loc[df['execution_time'].idxmin(), 'model']
    fastest_time = df['execution_time'].min()
    report.append(f"- Fastest execution: {fastest_model} ({fastest_time:.3f} seconds)")
    
    pass_rate = (df['passed'].sum() / len(df)) * 100
    report.append(f"- Overall pass rate: {pass_rate:.0f}%")
    
    return "\n".join(report)

def save_visualizations(results_dir="results", output_dir="visualizations"):
    """Create and save all visualizations"""
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    # Load results
    results = load_all_results(results_dir)
    if not results:
        print("No result files found!")
        return
    
    df = extract_score_data(results)
    
    print(f"Loaded {len(results)} benchmark results")
    print("Creating visualizations...")
    
    # 1. Main comparison dashboard
    comparison_fig = create_score_comparison_chart(df)
    comparison_fig.write_html(f"{output_dir}/benchmark_comparison.html")
    comparison_fig.write_image(f"{output_dir}/benchmark_comparison.png", width=1200, height=800)
    
    # 2. Detailed breakdown
    breakdown_fig = create_detailed_breakdown_chart(results)
    breakdown_fig.write_html(f"{output_dir}/detailed_breakdown.html")
    breakdown_fig.write_image(f"{output_dir}/detailed_breakdown.png", width=1000, height=500)
    
    # 3. Execution analysis
    execution_fig = create_execution_analysis_chart(df)
    execution_fig.write_html(f"{output_dir}/execution_analysis.html")
    execution_fig.write_image(f"{output_dir}/execution_analysis.png", width=1200, height=400)
    
    # 4. Summary report
    summary = generate_summary_report(results)
    with open(f"{output_dir}/summary_report.md", "w") as f:
        f.write(summary)
    
    print(f"✅ Visualizations saved to {output_dir}/")
    print(f"📊 Open {output_dir}/benchmark_comparison.html to view interactive dashboard")
    print(f"📋 View {output_dir}/summary_report.md for detailed analysis")

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Visualize AI Agent Benchmark Results')
    parser.add_argument('--results-dir', default='results', help='Directory containing result files')
    parser.add_argument('--output-dir', default='visualizations', help='Output directory for visualizations')
    
    args = parser.parse_args()
    
    save_visualizations(args.results_dir, args.output_dir)

if __name__ == "__main__":
    main()