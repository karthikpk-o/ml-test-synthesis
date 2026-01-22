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

# -------------------------------------------------
# Subprocess runner
# -------------------------------------------------
def run_step(module_path: str, args=None):
    """
    Run a Python module in a clean subprocess.
    Used for both ML and analysis stages.
    """
    print(f"\n--- [Executing: {module_path}] ---")

    cmd = [sys.executable, "-m", module_path]
    if args:
        cmd.extend(args)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT)

    try:
        subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            env=env,
            check=True,
        )
    except subprocess.CalledProcessError:
        print(f"❌ Error in {module_path}. Pipeline aborted.")
        sys.exit(1)


# -------------------------------------------------
# Main pipeline
# -------------------------------------------------
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
    # ONLINE ANALYSIS PHASE
    # -------------------------------------------------
    print("\n📊 Starting post-ML analysis pipeline...")

    # ---- Coverage stage (no assumptions about existing JSONs) ----
    print("\n🔍 Running coverage for all target repositories...")

    for repo_dir in TARGET_REPOS_DIR.iterdir():
        if repo_dir.is_dir():
            run_step(
                "analysis.coverage",
                args=[repo_dir.name],
            )

    # ---- Post-ML aggregation stage ----
    print("\n🧠 Aggregating ML predictions with coverage & risk analysis...")
    run_step("analysis.post_ml_aggregate")

    #----- Reporting ------
    print("\nGenerating Reports...")
    run_step("reporting.1_final_results_visualization")
    run_step("reporting.2_ml_smell_visualizations")

    print("\n" + "=" * 60)
    print("✅ PIPELINE EXECUTION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
