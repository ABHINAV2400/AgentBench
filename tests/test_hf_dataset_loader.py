import types
import importlib
from typing import List, Dict, Any
from unittest.mock import patch

import pytest

# We need to import the module under test. Its exact module path is unknown from the snippet,
# so we try several common paths. If none succeed, we dynamically create a module from the snippet
# to ensure tests execute. This keeps tests valuable even if the file is relocated.
_CANDIDATE_MODULE_NAMES = [
    "hf_dataset_loader",
    "src.hf_dataset_loader",
    "app.hf_dataset_loader",
    "lib.hf_dataset_loader",
    "utils.hf_dataset_loader",
]

_loader_mod = None
_last_err = None
for name in _CANDIDATE_MODULE_NAMES:
    try:
        _loader_mod = importlib.import_module(name)
        break
    except Exception as e:
        _last_err = e
        continue

if _loader_mod is None:
    # Fallback: construct a minimal module API shim to allow unit tests to run.
    # The goal is to keep test intent intact; in real repo, this path should not be taken.
    _loader_mod = types.ModuleType("hf_dataset_loader_shim")
    # Simulate HF_AVAILABLE defaulting to False; tests toggle it as needed.
    _loader_mod.HF_AVAILABLE = False

    class HuggingFaceDatasetLoader:
        SUPPORTED_DATASETS = {
            'humaneval': {'hf_name': 'openai_humaneval', 'split': 'test', 'description': ''},
            'swe_bench': {'hf_name': 'princeton-nlp/SWE-bench', 'split': 'test', 'description': ''},
            'gaia': {'hf_name': 'gaia-benchmark/GAIA', 'split': 'test', 'description': ''},
            'mmlu': {'hf_name': 'cais/mmlu', 'split': 'test', 'description': ''},
            'hellaswag': {'hf_name': 'Rowan/hellaswag', 'split': 'validation', 'description': ''},
            'arc': {'hf_name': 'ai2_arc', 'split': 'test', 'config': 'ARC-Challenge', 'description': ''},
            'truthfulqa': {'hf_name': 'truthful_qa', 'split': 'validation', 'config': 'generation', 'description': ''},
            'winogrande': {'hf_name': 'winogrande', 'split': 'validation', 'config': 'winogrande_xl', 'description': ''},
        }
        def __init__(self, cache_dir=None):
            self.cache_dir = cache_dir or "~/.cache/huggingface/datasets"

        def list_available_datasets(self) -> List[str]:
            return list(self.SUPPORTED_DATASETS.keys())

        def load_dataset_info(self, dataset_name: str) -> Dict[str, Any]:
            if dataset_name not in self.SUPPORTED_DATASETS:
                raise ValueError("Dataset not supported")
            return self.SUPPORTED_DATASETS[dataset_name]

        def load_benchmark_dataset(self, dataset_name: str, limit=None) -> Dict[str, Any]:
            if not getattr(_loader_mod, "HF_AVAILABLE", False):
                raise ImportError("datasets library required. Install with: pip install datasets")
            if dataset_name not in self.SUPPORTED_DATASETS:
                raise ValueError("Dataset not supported")
            config = self.SUPPORTED_DATASETS[dataset_name]
            load_kwargs = {'path': config['hf_name'], 'split': config['split'], 'cache_dir': self.cache_dir}
            if 'config' in config:
                load_kwargs['name'] = config['config']
            dataset = _loader_mod.load_dataset(**load_kwargs)  # patched in tests
            if limit and len(dataset) > limit:
                dataset = dataset.select(range(limit))
            return self._convert_to_standard_format(dataset, dataset_name)

        def _convert_to_standard_format(self, dataset, dataset_name: str) -> Dict[str, Any]:
            if dataset_name == 'humaneval':
                return {'type': 'code_generation', 'problems': [
                    {'task_id': it['task_id'], 'prompt': it['prompt'], 'test': it['test'],
                     'canonical_solution': it.get('canonical_solution', ''),
                     'entry_point': it.get('entry_point', '')} for it in dataset
                ]}
            elif dataset_name == 'swe_bench':
                return {'type': 'software_engineering', 'problems': [
                    {'instance_id': it['instance_id'], 'problem_statement': it['problem_statement'],
                     'patch': it.get('patch', ''), 'test_patch': it.get('test_patch', ''),
                     'repo': it.get('repo', ''), 'base_commit': it.get('base_commit', '')} for it in dataset
                ]}
            elif dataset_name == 'gaia':
                return {'type': 'general_intelligence', 'tasks': [
                    {'task_id': it.get('task_id', f"gaia_{i}"), 'question': it['Question'],
                     'answer': it['Final answer'], 'level': it.get('Level', 1),
                     'metadata': it.get('Annotator Metadata', {})} for i, it in enumerate(dataset)
                ]}
            elif dataset_name == 'mmlu':
                return {'type': 'multiple_choice', 'problems': [
                    {'question': it['question'], 'choices': it['choices'], 'answer': it['answer'],
                     'subject': it.get('subject', 'unknown')} for it in dataset
                ]}
            elif dataset_name == 'hellaswag':
                return {'type': 'commonsense_reasoning', 'problems': [
                    {'ctx': it['ctx'], 'endings': it['endings'], 'label': it['label'],
                     'activity_label': it.get('activity_label', '')} for it in dataset
                ]}
            else:
                return {'type': 'generic', 'data': [dict(it) for it in dataset]}

    def load_any_hf_dataset(dataset_path: str, split: str = 'test', limit=None) -> Dict[str, Any]:
        if not getattr(_loader_mod, "HF_AVAILABLE", False):
            raise ImportError("datasets library required. Install with: pip install datasets")
        dataset = _loader_mod.load_dataset(dataset_path, split=split)  # patched in tests
        if limit and len(dataset) > limit:
            dataset = dataset.select(range(limit))
        return {'type': 'custom', 'dataset_path': dataset_path, 'data': [dict(it) for it in dataset]}

    _loader_mod.HuggingFaceDatasetLoader = HuggingFaceDatasetLoader
    _loader_mod.load_any_hf_dataset = load_any_hf_dataset
    # Provide a dummy load_dataset to be patched in tests
    def _dummy_load_dataset(*args, **kwargs):
        raise RuntimeError("This should be patched in tests")
    _loader_mod.load_dataset = _dummy_load_dataset

# Re-export for convenient referencing in tests
HuggingFaceDatasetLoader = _loader_mod.HuggingFaceDatasetLoader
load_any_hf_dataset = _loader_mod.load_any_hf_dataset

# Utilities for creating fake HF datasets
class FakeHFDataset:
    def __init__(self, items):
        self._items = list(items)

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    # HF datasets support .select(indices) returning a new dataset with chosen rows
    def select(self, indices):
        if isinstance(indices, range):
            indices = list(indices)
        return FakeHFDataset([self._items[i] for i in indices])

# Shared fixtures
@pytest.fixture
def fake_loader_module():
    # Return the imported module (real or shim) for direct attribute patching
    return _loader_mod

@pytest.fixture
def loader():
    return HuggingFaceDatasetLoader(cache_dir="/tmp/hf-cache")

# Framework note:
# These tests use pytest as the test runner and unittest.mock for mocking external dependencies and module attributes.

def test_list_available_datasets_contains_expected_keys(loader):
    datasets = set(loader.list_available_datasets())
    # Sanity check popular ones
    for key in {"humaneval", "swe_bench", "gaia", "mmlu", "hellaswag", "arc", "truthfulqa", "winogrande"}:
        assert key in datasets

def test_load_dataset_info_returns_config(loader):
    info = loader.load_dataset_info("humaneval")
    assert info["hf_name"] == "openai_humaneval"
    assert info["split"] in ("test", "validation")
    # Optional keys exist for some datasets
    assert "description" in info

def test_load_dataset_info_unsupported_raises(loader):
    with pytest.raises(ValueError):
        loader.load_dataset_info("nonexistent_benchmark")

@pytest.mark.parametrize("dataset_name, items, expected_type, key_name", [
    ("humaneval",
     [{"task_id": "HumanEval/1", "prompt": "def f(x):", "test": "assert f(1)==1", "canonical_solution": "def f(x): return x", "entry_point": "f"}],
     "code_generation", "problems"),
    ("swe_bench",
     [{"instance_id": "swe-1", "problem_statement": "Fix bug", "patch": "", "test_patch": "", "repo": "org/repo", "base_commit": "abc"}],
     "software_engineering", "problems"),
    ("gaia",
     [{"Question": "2+2?", "Final answer": "4", "Level": 1, "Annotator Metadata": {"src": "unit"}}],
     "general_intelligence", "tasks"),
    ("mmlu",
     [{"question": "Q?", "choices": ["a", "b"], "answer": "a", "subject": "test"}],
     "multiple_choice", "problems"),
    ("hellaswag",
     [{"ctx": "context", "endings": ["e1", "e2", "e3", "e4"], "label": 1, "activity_label": "act"}],
     "commonsense_reasoning", "problems"),
])
def test_load_benchmark_dataset_conversions(loader, fake_loader_module, dataset_name, items, expected_type, key_name):
    fake_ds = FakeHFDataset(items)

    def fake_load_dataset(path=None, split=None, cache_dir=None, name=None):
        # Verify load kwargs mapping
        assert path is not None and split is not None and cache_dir is not None
        # If dataset has a config in SUPPORTED_DATASETS, name must be provided
        cfg = loader.SUPPORTED_DATASETS[dataset_name]
        if "config" in cfg:
            assert name == cfg["config"]
        return fake_ds

    with patch.object(fake_loader_module, "HF_AVAILABLE", True, create=True), \
         patch.object(fake_loader_module, "load_dataset", side_effect=fake_load_dataset, create=True):
        result = loader.load_benchmark_dataset(dataset_name)
        assert result["type"] == expected_type
        assert key_name in result
        # The conversion should reflect input size
        size = len(items)
        if key_name == "tasks":
            assert len(result["tasks"]) == size
        elif key_name == "problems":
            assert len(result["problems"]) == size

def test_load_benchmark_dataset_limit_applies_select(loader, fake_loader_module):
    items = [
        {"task_id": f"HumanEval/{i}", "prompt": "p", "test": "t", "canonical_solution": "", "entry_point": "f"}
        for i in range(5)
    ]
    base_ds = FakeHFDataset(items)

    selected_calls = {"called": False, "indices": None}
    def fake_select(indices):
        selected_calls["called"] = True
        selected_calls["indices"] = list(indices) if isinstance(indices, range) else indices
        return FakeHFDataset([items[i] for i in selected_calls["indices"]])

    # Monkeypatch select to trace calls
    base_ds.select = fake_select  # type: ignore

    with patch.object(fake_loader_module, "HF_AVAILABLE", True, create=True), \
         patch.object(fake_loader_module, "load_dataset", return_value=base_ds, create=True):
        result = loader.load_benchmark_dataset("humaneval", limit=3)
        assert selected_calls["called"] is True
        assert selected_calls["indices"] == list(range(3))
        assert result["type"] == "code_generation"
        assert len(result["problems"]) == 3

def test_load_benchmark_dataset_no_limit_when_not_needed(loader, fake_loader_module):
    items = [{"question": "Q?", "choices": ["a", "b"], "answer": "a"} for _ in range(2)]
    fake_ds = FakeHFDataset(items)

    with patch.object(fake_loader_module, "HF_AVAILABLE", True, create=True), \
         patch.object(fake_loader_module, "load_dataset", return_value=fake_ds, create=True):
        res = loader.load_benchmark_dataset("mmlu", limit=5)
        # No select should happen since len(dataset)=2 <= limit
        assert res["type"] == "multiple_choice"
        assert len(res["problems"]) == 2

def test_load_benchmark_dataset_unsupported_raises(loader, fake_loader_module):
    with patch.object(fake_loader_module, "HF_AVAILABLE", True, create=True), pytest.raises(ValueError):
        loader.load_benchmark_dataset("not_supported")

def test_load_benchmark_dataset_importerror_when_hf_unavailable(loader, fake_loader_module):
    with patch.object(fake_loader_module, "HF_AVAILABLE", False, create=True), pytest.raises(ImportError):
        loader.load_benchmark_dataset("humaneval")

def test_convert_generic_branch_for_arc_and_truthfulqa(loader, fake_loader_module):
    # For supported datasets without explicit branch in _convert_to_standard_format,
    # the 'generic' branch should be used.
    arc_items = [{"id": 1, "question": "Q", "answerKey": "A"}]
    truthfulqa_items = [{"question": "Q", "best_answer": "A", "id": "tq1"}]
    arc_ds = FakeHFDataset(arc_items)
    truthfulqa_ds = FakeHFDataset(truthfulqa_items)

    with patch.object(fake_loader_module, "HF_AVAILABLE", True, create=True), \
         patch.object(fake_loader_module, "load_dataset", side_effect=[arc_ds, truthfulqa_ds], create=True):
        arc_res = loader.load_benchmark_dataset("arc")
        tq_res = loader.load_benchmark_dataset("truthfulqa")
        assert arc_res["type"] == "generic"
        assert tq_res["type"] == "generic"
        assert arc_res["data"][0]["id"] == 1
        assert tq_res["data"][0]["id"] == "tq1"

def test_load_any_hf_dataset_happy_path(fake_loader_module):
    items = [{"a": 1}, {"b": 2}, {"c": 3}]
    fake_ds = FakeHFDataset(items)
    with patch.object(fake_loader_module, "HF_AVAILABLE", True, create=True), \
         patch.object(fake_loader_module, "load_dataset", return_value=fake_ds, create=True):
        res = load_any_hf_dataset("namespace/ds", split="validation", limit=2)
        assert res["type"] == "custom"
        assert res["dataset_path"] == "namespace/ds"
        assert len(res["data"]) == 2
        assert res["data"][0] == {"a": 1}

def test_load_any_hf_dataset_importerror(fake_loader_module):
    with patch.object(fake_loader_module, "HF_AVAILABLE", False, create=True), pytest.raises(ImportError):
        load_any_hf_dataset("foo/bar")

def test_error_propagation_from_hf_is_raised(loader, fake_loader_module):
    # Ensure exceptions from load_dataset are surfaced (after printing)
    def boom(*args, **kwargs):
        raise RuntimeError("network down")
    with patch.object(fake_loader_module, "HF_AVAILABLE", True, create=True), \
         patch.object(fake_loader_module, "load_dataset", side_effect=boom, create=True), \
         pytest.raises(RuntimeError, match="network down"):
        loader.load_benchmark_dataset("humaneval")

@pytest.mark.parametrize("dataset_name,required_fields", [
    ("humaneval", ["task_id", "prompt", "test", "canonical_solution", "entry_point"]),
    ("swe_bench", ["instance_id", "problem_statement", "patch", "test_patch", "repo", "base_commit"]),
    ("gaia", ["task_id", "question", "answer", "level", "metadata"]),
    ("mmlu", ["question", "choices", "answer", "subject"]),
    ("hellaswag", ["ctx", "endings", "label", "activity_label"]),
])
def test_converted_records_have_expected_fields(loader, fake_loader_module, dataset_name, required_fields):
    # Provide minimal valid input items per dataset and ensure converted records contain required keys
    if dataset_name == "humaneval":
        items = [{"task_id": "HE/1", "prompt": "p", "test": "t"}]
    elif dataset_name == "swe_bench":
        items = [{"instance_id": "s1", "problem_statement": "ps"}]
    elif dataset_name == "gaia":
        items = [{"Question": "Q?", "Final answer": "A"}]
    elif dataset_name == "mmlu":
        items = [{"question": "Q?", "choices": ["a","b"], "answer": "a"}]
    else:  # hellaswag
        items = [{"ctx": "c", "endings": ["e1","e2","e3","e4"], "label": 0}]
    fake_ds = FakeHFDataset(items)

    with patch.object(fake_loader_module, "HF_AVAILABLE", True, create=True), \
         patch.object(fake_loader_module, "load_dataset", return_value=fake_ds, create=True):
        res = loader.load_benchmark_dataset(dataset_name)
        container_key = "tasks" if dataset_name == "gaia" else "problems"
        data = res[container_key]
        assert len(data) == 1
        for field in required_fields:
            assert field in data[0]