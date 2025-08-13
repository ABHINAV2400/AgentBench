"""
Hugging Face dataset integration for automated benchmark loading
Supports loading datasets directly from HF Hub without manual intervention
"""
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    from datasets import load_dataset
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    print("⚠️  datasets library not found. Install with: pip install datasets")

class HuggingFaceDatasetLoader:
    """Loads benchmark datasets from Hugging Face Hub automatically."""
    
    # Popular benchmark datasets available on HF
    SUPPORTED_DATASETS = {
        'humaneval': {
            'hf_name': 'openai_humaneval',
            'split': 'test',
            'description': 'OpenAI HumanEval code generation benchmark'
        },
        'swe_bench': {
            'hf_name': 'princeton-nlp/SWE-bench',
            'split': 'test',
            'description': 'Software engineering benchmark from Princeton'
        },
        'gaia': {
            'hf_name': 'gaia-benchmark/GAIA',
            'split': 'test',
            'description': 'General AI assistant benchmark'
        },
        'mmlu': {
            'hf_name': 'cais/mmlu',
            'split': 'test',
            'description': 'Massive Multitask Language Understanding'
        },
        'hellaswag': {
            'hf_name': 'Rowan/hellaswag',
            'split': 'validation',
            'description': 'Commonsense reasoning benchmark'
        },
        'arc': {
            'hf_name': 'ai2_arc',
            'split': 'test',
            'config': 'ARC-Challenge',
            'description': 'AI2 Reasoning Challenge'
        },
        'truthfulqa': {
            'hf_name': 'truthful_qa',
            'split': 'validation',
            'config': 'generation',
            'description': 'TruthfulQA benchmark for truthfulness'
        },
        'winogrande': {
            'hf_name': 'winogrande',
            'split': 'validation',
            'config': 'winogrande_xl',
            'description': 'Commonsense reasoning benchmark'
        }
    }
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize with optional cache directory."""
        self.cache_dir = cache_dir or str(Path.home() / '.cache' / 'huggingface' / 'datasets')
        
    def list_available_datasets(self) -> List[str]:
        """List all supported datasets."""
        return list(self.SUPPORTED_DATASETS.keys())
    
    def load_dataset_info(self, dataset_name: str) -> Dict[str, Any]:
        """Get information about a dataset."""
        if dataset_name not in self.SUPPORTED_DATASETS:
            raise ValueError(f"Dataset {dataset_name} not supported. Available: {self.list_available_datasets()}")
        
        return self.SUPPORTED_DATASETS[dataset_name]
    
    def load_benchmark_dataset(self, dataset_name: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Load a benchmark dataset from Hugging Face."""
        if not HF_AVAILABLE:
            raise ImportError("datasets library required. Install with: pip install datasets")
        
        if dataset_name not in self.SUPPORTED_DATASETS:
            raise ValueError(f"Dataset {dataset_name} not supported")
        
        config = self.SUPPORTED_DATASETS[dataset_name]
        
        print(f"📥 Loading {dataset_name} from Hugging Face...")
        
        try:
            # Load dataset with optional config
            load_kwargs = {
                'path': config['hf_name'],
                'split': config['split'],
                'cache_dir': self.cache_dir
            }
            
            if 'config' in config:
                load_kwargs['name'] = config['config']
            
            dataset = load_dataset(**load_kwargs)
            
            # Limit dataset size if specified
            if limit and len(dataset) > limit:
                dataset = dataset.select(range(limit))
            
            print(f"✅ Loaded {len(dataset)} samples from {dataset_name}")
            
            # Convert to our standard format
            return self._convert_to_standard_format(dataset, dataset_name)
            
        except Exception as e:
            print(f"❌ Error loading {dataset_name}: {e}")
            raise
    
    def _convert_to_standard_format(self, dataset, dataset_name: str) -> Dict[str, Any]:
        """Convert HF dataset to our standard benchmark format."""
        
        if dataset_name == 'humaneval':
            return {
                'type': 'code_generation',
                'problems': [
                    {
                        'task_id': item['task_id'],
                        'prompt': item['prompt'],
                        'test': item['test'],
                        'canonical_solution': item.get('canonical_solution', ''),
                        'entry_point': item.get('entry_point', '')
                    }
                    for item in dataset
                ]
            }
        
        elif dataset_name == 'swe_bench':
            return {
                'type': 'software_engineering',
                'problems': [
                    {
                        'instance_id': item['instance_id'],
                        'problem_statement': item['problem_statement'],
                        'patch': item.get('patch', ''),
                        'test_patch': item.get('test_patch', ''),
                        'repo': item.get('repo', ''),
                        'base_commit': item.get('base_commit', '')
                    }
                    for item in dataset
                ]
            }
        
        elif dataset_name == 'gaia':
            return {
                'type': 'general_intelligence',
                'tasks': [
                    {
                        'task_id': item.get('task_id', f"gaia_{i}"),
                        'question': item['Question'],
                        'answer': item['Final answer'],
                        'level': item.get('Level', 1),
                        'metadata': item.get('Annotator Metadata', {})
                    }
                    for i, item in enumerate(dataset)
                ]
            }
        
        elif dataset_name == 'mmlu':
            return {
                'type': 'multiple_choice',
                'problems': [
                    {
                        'question': item['question'],
                        'choices': item['choices'],
                        'answer': item['answer'],
                        'subject': item.get('subject', 'unknown')
                    }
                    for item in dataset
                ]
            }
        
        elif dataset_name == 'hellaswag':
            return {
                'type': 'commonsense_reasoning',
                'problems': [
                    {
                        'ctx': item['ctx'],
                        'endings': item['endings'],
                        'label': item['label'],
                        'activity_label': item.get('activity_label', '')
                    }
                    for item in dataset
                ]
            }
        
        else:
            # Generic format for other datasets
            return {
                'type': 'generic',
                'data': [dict(item) for item in dataset]
            }

def load_any_hf_dataset(dataset_path: str, split: str = 'test', limit: Optional[int] = None) -> Dict[str, Any]:
    """Load any dataset from Hugging Face by path."""
    if not HF_AVAILABLE:
        raise ImportError("datasets library required. Install with: pip install datasets")
    
    print(f"📥 Loading custom dataset: {dataset_path}")
    
    try:
        dataset = load_dataset(dataset_path, split=split)
        
        if limit and len(dataset) > limit:
            dataset = dataset.select(range(limit))
        
        print(f"✅ Loaded {len(dataset)} samples")
        
        return {
            'type': 'custom',
            'dataset_path': dataset_path,
            'data': [dict(item) for item in dataset]
        }
    
    except Exception as e:
        print(f"❌ Error loading {dataset_path}: {e}")
        raise

# Example usage and testing
if __name__ == "__main__":
    loader = HuggingFaceDatasetLoader()
    
    print("🚀 Available benchmark datasets:")
    for name in loader.list_available_datasets():
        info = loader.load_dataset_info(name)
        print(f"  • {name}: {info['description']}")
    
    # Test loading a small sample
    if HF_AVAILABLE:
        try:
            print("\n🧪 Testing HumanEval dataset loading...")
            humaneval_data = loader.load_benchmark_dataset('humaneval', limit=3)
            print(f"✅ Successfully loaded {len(humaneval_data['problems'])} problems")
            
            # Show first problem
            if humaneval_data['problems']:
                first_problem = humaneval_data['problems'][0]
                print(f"\n📝 Sample problem: {first_problem['task_id']}")
                print(f"Prompt: {first_problem['prompt'][:100]}...")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
    else:
        print("\n⚠️  Install 'datasets' library to test HF integration")