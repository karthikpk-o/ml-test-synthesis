import pandas as pd
from pathlib import Path

from analysis.coverage import collect_coverage
from analysis.pipeline_demo import run_pipeline


def extract_repo_and_file(file_path: str):
    """
    Extract repository name and file path relative to repo root
    from an absolute File_Path pointing inside workspace/target-repos.
    """
    p = Path(file_path).resolve()
    parts = p.parts

    if "target-repos" not in parts:
        raise ValueError(f"Invalid File_Path format: {file_path}")

    idx = parts.index("target-repos")
    repo_name = parts[idx + 1]
    relative_file = Path(*parts[idx + 2:])

    return repo_name, str(relative_file)


def run_pipeline_from_ml(
    repo_base_path: str,
    ml_output_csv: str,
    output_csv: str,
    top_k: int = 30,
):
    df = pd.read_csv(ml_output_csv)

    # ---------------------------------------
    # Normalize paths + extract repo metadata
    # ---------------------------------------
    extracted = df["File_Path"].apply(extract_repo_and_file)
    df["repo_name"] = extracted.apply(lambda x: x[0])
    df["relative_file"] = extracted.apply(lambda x: x[1])

    # ---------------------------------------
    # Filter HIGH-smell functions only
    # ---------------------------------------
    df_high = df[df["smell_label"] == "HIGH"]

    if df_high.empty:
        print("No HIGH smell functions found.")
        return []

    # ---------------------------------------
    # Deterministic prioritization
    # ---------------------------------------
    sort_cols = ["ml_confidence", "lloc"] if "ml_confidence" in df_high.columns else ["lloc"]
    df_high = df_high.sort_values(by=sort_cols, ascending=False)

    selected = df_high.groupby("repo_name").head(top_k)

    results = []

    # ---------------------------------------
    # Run coverage ONCE per repo
    # ---------------------------------------
    for repo_name, repo_data in selected.groupby("repo_name"):
        repo_path = Path(repo_base_path) / repo_name

        print(f"\n🚀 Running coverage once for: {repo_name}")

        try:
            coverage_data = collect_coverage(str(repo_path))

            for _, row in repo_data.iterrows():
                function = {
                    "file": row["relative_file"],
                    "start_line": int(row["start_line"]),
                    "end_line": int(row["end_line"]),
                    "cc": row["cc"],
                    "lloc": row["lloc"],
                    "difficulty": row["difficulty"],
                    "smell_label": row["smell_label"],
                }

                result = run_pipeline(
                    repo_path=str(repo_path),
                    function=function,
                    coverage_data=coverage_data,
                )

                result.update({
                    "repo_name": repo_name,
                    "file_path": row["relative_file"],
                    "method_name": row.get("Method_Name", ""),
                    "cc": row["cc"],
                    "lloc": row["lloc"],
                    "difficulty": row["difficulty"],
                })

                results.append(result)

        except Exception as e:
            print(f"Failed processing repo {repo_name}: {e}")

    # ---------------------------------------
    # Persist final results
    # ---------------------------------------
    if results:
        df_results = pd.DataFrame(results)

        df_results["recommendations"] = df_results["recommendations"].apply(
            lambda recs: "; ".join(recs)
        )

        final_columns = [
            "repo_name",
            "file_path",
            "method_name",
            "start_line",
            "end_line",
            "cc",
            "lloc",
            "difficulty",
            "smell_label",
            "coverage_percent",
            "coverage_bucket",
            "risk_category",
            "recommendations",
        ]

        df_results = df_results[final_columns]

        output_path = Path(output_csv)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        df_results.to_csv(output_path, index=False)
        print(f"\n✅ Final results written to: {output_path}")

    return results


if __name__ == "__main__":
    raise RuntimeError(
        "from_ml.py is not meant to be run directly. "
        "Invoke it via scripts/run_full_pipeline.py"
    )
