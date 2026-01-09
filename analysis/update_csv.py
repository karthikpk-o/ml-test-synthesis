import pandas as pd
from pathlib import Path

from analysis.risk import classify_risk
from recommendations.rules import recommend_tests


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

ORIGINAL_CSV = PROCESSED_DIR / "final_results.csv"
COVERAGE_CSV = PROCESSED_DIR / "final_results_with_function_coverage.csv"
OUTPUT_CSV = PROCESSED_DIR / "final_results_corrected.csv"


def coverage_bucket_from_percent(p: float) -> str:
    if p == 0:
        return "ZERO"
    if p <= 30:
        return "LOW"
    if p <= 70:
        return "MEDIUM"
    return "HIGH"


def main():
    # 1️⃣ Load original results (authoritative column order)
    df_orig = pd.read_csv(ORIGINAL_CSV)
    original_columns = list(df_orig.columns)

    # 2️⃣ Load function-level coverage
    df_cov = pd.read_csv(COVERAGE_CSV)

    # 3️⃣ Merge function-level coverage back
    df = df_orig.merge(
        df_cov[
            [
                "repo_name",
                "file_path",
                "method_name",
                "start_line",
                "end_line",
                "function_coverage_percent",
            ]
        ],
        on=["repo_name", "file_path", "method_name", "start_line", "end_line"],
        how="left",
    )

    # Missing coverage → 0
    df["function_coverage_percent"] = df["function_coverage_percent"].fillna(0.0)

    # 4️⃣ Recompute coverage bucket
    df["coverage_bucket"] = df["function_coverage_percent"].apply(
        coverage_bucket_from_percent
    )

    # 5️⃣ Recompute risk category
    df["risk_category"] = df.apply(
        lambda row: classify_risk(
            row["smell_label"],
            row["coverage_bucket"],
        ),
        axis=1,
    )

    # 6️⃣ Recompute recommendations
    def build_recommendations(row):
        function_dict = {
            "risk_category": row["risk_category"],
            "coverage_bucket": row["coverage_bucket"],
            "cc": row.get("cc", 0),
            "lloc": row.get("lloc", 0),
            "difficulty": row.get("difficulty", 0),
        }
        return "; ".join(recommend_tests(function_dict))

    df["recommendations"] = df.apply(build_recommendations, axis=1)

    # 7️⃣ Replace old coverage_percent with function-level coverage
    coverage_col_index = original_columns.index("coverage_percent")

    df = df.drop(columns=["coverage_percent"])
    df = df.rename(columns={"function_coverage_percent": "coverage_percent"})

    # 8️⃣ Restore column order exactly
    new_columns = []
    for col in original_columns:
        if col == "coverage_percent":
            new_columns.append("coverage_percent")
        else:
            new_columns.append(col)

    # Ensure derived columns are included (if they existed originally)
    for col in df.columns:
        if col not in new_columns:
            new_columns.append(col)

    df = df[new_columns]

    # 9️⃣ Write final corrected CSV
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"[OK] Corrected results written to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
