from analysis.coverage import collect_coverage
from analysis.mapper import compute_function_coverage
from analysis.risk import classify_risk
from recommendations.rules import recommend_tests


def run_pipeline(repo_path: str, function: dict, smell_label: str):
    """
    function dict must contain:
      - file
      - start_line
      - end_line
      - cc
      - lloc
      - difficulty
    """

    # Step 1: Coverage
    coverage_data = collect_coverage(repo_path)

    # Step 2: Function coverage
    coverage_percent, coverage_bucket = compute_function_coverage(
        function, coverage_data
    )

    # Step 3: Risk classification
    risk_category = classify_risk(smell_label, coverage_bucket)

    # Step 4: Test recommendations
    function_enriched = {
        **function,
        "coverage_percent": coverage_percent,
        "coverage_bucket": coverage_bucket,
        "risk_category": risk_category,
    }

    recommendations = recommend_tests(function_enriched)

    return {
        "file": function["file"],
        "start_line": function["start_line"],
        "end_line": function["end_line"],
        "smell_label": smell_label,
        "coverage_percent": coverage_percent,
        "coverage_bucket": coverage_bucket,
        "risk_category": risk_category,
        "recommendations": recommendations,
    }


if __name__ == "__main__":
    # Example test on requests
    repo = "../target-repos/requests"

    sample_function = {
        "file": "requests/sessions.py",
        "start_line": 1,
        "end_line": 50,
        "cc": 15,
        "lloc": 45,
        "difficulty": 22,
    }

    result = run_pipeline(repo, sample_function, smell_label="HIGH")

    from pprint import pprint
    pprint(result)
