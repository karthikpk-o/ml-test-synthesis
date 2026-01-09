import json
import pandas as pd
from pathlib import Path


# Base directory: ml-test-synthesis/
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"

INPUT_CSV = PROCESSED_DIR / "final_results.csv"
OUTPUT_CSV = PROCESSED_DIR / "final_results_with_function_coverage.csv"


def load_coverage(repo_name: str) -> dict:
    coverage_file = DATA_DIR / f"{repo_name}_coverage.json"
    if not coverage_file.exists():
        return {}

    with open(coverage_file) as f:
        return json.load(f).get("files", {})


def compute_function_coverage(row, coverage_files) -> float:
    file_path = row["file_path"]
    start = int(row["start_line"])
    end = int(row["end_line"])

    if start > end:
        return 0.0

    total_lines = end - start + 1
    executed = set()

    for covered_file, data in coverage_files.items():
        if covered_file.endswith(file_path):
            executed_lines = set(data.get("executed_lines", []))
            executed = executed_lines.intersection(range(start, end + 1))
            break

    if total_lines == 0:
        return 0.0

    return round((len(executed) / total_lines) * 100, 2)


def main():
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Input CSV not found: {INPUT_CSV}")

    df = pd.read_csv(INPUT_CSV)

    # Only keep columns relevant for function-level coverage
    df = df[
        ["repo_name", "file_path", "method_name", "start_line", "end_line"]
    ]

    # Load coverage once per repo
    coverage_cache = {
        repo: load_coverage(repo)
        for repo in df["repo_name"].unique()
    }

    df["function_coverage_percent"] = df.apply(
        lambda row: compute_function_coverage(
            row, coverage_cache.get(row["repo_name"], {})
        ),
        axis=1,
    )

    PROCESSED_DIR.mkdir(exist_ok=True)

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"[OK] Function-level coverage written to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
