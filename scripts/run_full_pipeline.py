import subprocess
import sys
import os
from pathlib import Path

# -------------------------------------------------
# Resolve project root and ensure imports work
# -------------------------------------------------
SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parents[1]  # <project-root>/ml-test-synthesis

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# -------------------------------------------------
# Imports from existing config.paths (NO INVENTED CONSTANTS)
# -------------------------------------------------
from config.paths import (
    TARGET_REPOS_DIR,
    PROCESSED_DATA_DIR,
)

from analysis.from_ml import run_pipeline_from_ml


def run_step(module_path: str):
    """
    Run a Python module in a clean subprocess.
    Used ONLY for ML stages.
    """
    print(f"\n--- [Executing: {module_path}] ---")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT)

    try:
        subprocess.run(
            [sys.executable, "-m", module_path],
            cwd=str(PROJECT_ROOT),
            env=env,
            check=True,
        )
    except subprocess.CalledProcessError:
        print(f"❌ Error in {module_path}. Pipeline aborted.")
        sys.exit(1)


def main():
    print("🚀 STARTING MACHINE LEARNING–GUIDED CODE SMELL DETECTION PIPELINE")

    # -------------------------------------------------
    # OFFLINE ML PHASE (isolated subprocesses)
    # -------------------------------------------------
    run_step("ml.build_training_dataset")
    run_step("ml.build_validation_dataset")
    run_step("ml.train_model")
    run_step("ml.inference")

    # -------------------------------------------------
    # ONLINE ANALYSIS PHASE (in-process)
    # -------------------------------------------------
    print("\n📊 Starting post-ML analysis pipeline...")

    ml_output_csv = PROCESSED_DATA_DIR / "ml_smell_predictions.csv"
    final_output_csv = PROCESSED_DATA_DIR / "final_results.csv"

    run_pipeline_from_ml(
        repo_base_path=str(TARGET_REPOS_DIR),
        ml_output_csv=str(ml_output_csv),
        output_csv=str(final_output_csv),
    )

    print("\n" + "=" * 60)
    print("✅ PIPELINE COMPLETE")
    print(f"📄 Final results: {final_output_csv}")
    print("=" * 60)


if __name__ == "__main__":
    main()
