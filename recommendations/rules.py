def recommend_tests(function: dict) -> list:
    """
    function dict may contain:
      - risk_category
      - coverage_bucket
      - cc (cyclomatic complexity)
      - lloc (logical lines of code)
      - difficulty (Halstead difficulty)
    """

    recs = []

    risk = function.get("risk_category")
    coverage = function.get("coverage_bucket")

    cc = function.get("cc", 0)
    lloc = function.get("lloc", 0)
    difficulty = function.get("difficulty", 0)

    # Absolute priority
    if risk == "Hidden Risk":
        recs.append("Write tests immediately before modifying this code")

    # Coverage-driven guidance
    if coverage == "ZERO":
        recs.append("Add basic smoke tests to ensure execution paths are covered")

    if coverage in ("ZERO", "LOW"):
        recs.append("Increase coverage by adding input boundary tests")

    # Complexity-driven guidance
    if cc >= 10:
        recs.append("Add branch and conditional path tests due to high cyclomatic complexity")

    if lloc >= 30:
        recs.append("Consider decomposing this method; add focused unit tests per responsibility")

    if difficulty >= 20:
        recs.append("Mock external dependencies to isolate complex logic during testing")

    # Refactor guidance
    if risk == "Refactor Candidate":
        recs.append("Safe to refactor after ensuring existing tests capture current behavior")

    # Fallback (avoid empty output)
    if not recs:
        recs.append("No immediate testing action required")

    return recs