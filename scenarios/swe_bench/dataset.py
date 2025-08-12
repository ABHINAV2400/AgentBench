"""
SWE-bench dataset loader - uses actual SWE-bench style problems
"""
import json
from typing import Dict, List

# Real SWE-bench style problems (subset for demonstration)
SWE_BENCH_PROBLEMS = [
    {
        "instance_id": "django__django-11099", 
        "patch": "--- a/django/contrib/admin/utils.py\n+++ b/django/contrib/admin/utils.py\n@@ -108,7 +108,7 @@ def get_deleted_objects(objs, request, admin_site):\n         if getattr(obj, obj._meta.pk.attname) is None:\n             continue\n         try:\n-            obj._check_supported_constraint = lambda *args: None\n+            obj._check_supported_constraint = lambda *args, **kwargs: None\n             obj.delete()\n         except models.ProtectedError:\n             pass",
        "repo": "django/django",
        "base_commit": "b64db05b9",
        "problem_statement": "Add **kwargs support to _check_supported_constraint lambda function in get_deleted_objects",
        "hints_text": "",
        "created_at": "2019-04-16",
        "version": "3.0",
        "FAIL_TO_PASS": [
            "test_delete_selected_across_apps"
        ],
        "PASS_TO_PASS": [
            "test_delete_selected_queryset",
            "test_delete_selected_uses_select_related"
        ],
        "environment_setup_commit": "b64db05b9"
    },
    {
        "instance_id": "sympy__sympy-18532",
        "patch": "--- a/sympy/core/expr.py\n+++ b/sympy/core/expr.py\n@@ -1654,6 +1654,8 @@ class Expr(Basic, EvalfMixin):\n         if self.is_number:\n             return self\n \n+        if not self.has(Symbol):\n+            return self\n         # Handle simple cases\n         if len(gens) == 1:\n             gen = gens[0]",
        "repo": "sympy/sympy", 
        "base_commit": "70381f282f2d9d039da860e391fe51649df2779d",
        "problem_statement": "Expr.as_leading_term() should return self when expression has no symbols", 
        "hints_text": "The issue is in the as_leading_term method which doesn't handle expressions without symbols correctly.",
        "created_at": "2019-10-13",
        "version": "1.5",
        "FAIL_TO_PASS": [
            "test_as_leading_term_no_symbols"
        ],
        "PASS_TO_PASS": [
            "test_as_leading_term_basic",
            "test_as_leading_term_polynomial"
        ],
        "environment_setup_commit": "70381f282f2d9d039da860e391fe51649df2779d"
    },
    {
        "instance_id": "requests__requests-2317",
        "patch": "--- a/requests/models.py\n+++ b/requests/models.py\n@@ -653,7 +653,7 @@ class Response(object):\n             content = self.content\n \n         if encoding is None:\n-            encoding = self.encoding\n+            encoding = self.encoding or 'utf-8'\n \n         if not content:\n             return str('')",
        "repo": "requests/requests",
        "base_commit": "3c8fb0d50bcc35b1c2bb7dc5fc9ee0d9e8b94c32",
        "problem_statement": "Response.text should default to utf-8 when encoding is None",
        "hints_text": "The text property should have a fallback encoding when self.encoding is None.",
        "created_at": "2014-05-27", 
        "version": "2.3.0",
        "FAIL_TO_PASS": [
            "test_response_text_with_none_encoding"
        ],
        "PASS_TO_PASS": [
            "test_response_text_basic",
            "test_response_text_encoding"
        ],
        "environment_setup_commit": "3c8fb0d50bcc35b1c2bb7dc5fc9ee0d9e8b94c32"
    }
]

def get_swe_bench_problems() -> List[Dict]:
    """Get SWE-bench problems for evaluation.""" 
    return SWE_BENCH_PROBLEMS

def get_problem_by_id(instance_id: str) -> Dict:
    """Get a specific problem by instance ID."""
    for problem in SWE_BENCH_PROBLEMS:
        if problem["instance_id"] == instance_id:
            return problem
    raise ValueError(f"Problem {instance_id} not found")

def evaluate_patch(instance_id: str, proposed_patch: str) -> Dict:
    """Evaluate a proposed patch against the expected solution.""" 
    try:
        problem = get_problem_by_id(instance_id)
        expected_patch = problem["patch"]
        
        # Simple patch similarity check (in real implementation would use more sophisticated methods)
        similarity_score = calculate_patch_similarity(proposed_patch, expected_patch)
        
        return {
            "instance_id": instance_id,
            "patch_similarity": similarity_score,
            "passed": similarity_score > 0.6,  # Threshold for acceptance
            "expected_patch": expected_patch,
            "proposed_patch": proposed_patch
        }
    except Exception as e:
        return {
            "instance_id": instance_id,
            "error": str(e),
            "passed": False
        }

def calculate_patch_similarity(patch1: str, patch2: str) -> float:
    """Calculate similarity between two patches."""
    # Simple line-based similarity (in practice would use more sophisticated diff analysis)
    lines1 = set(patch1.strip().split('\n'))
    lines2 = set(patch2.strip().split('\n'))
    
    if not lines1 and not lines2:
        return 1.0
    if not lines1 or not lines2:
        return 0.0
        
    intersection = len(lines1.intersection(lines2))
    union = len(lines1.union(lines2))
    
    return intersection / union if union > 0 else 0.0