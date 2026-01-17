import subprocess
import sys
import os
from pathlib import Path


class CIError(Exception):
    """Raised when CI pipeline fails."""
    pass

# ---------------------------------------------------------
# Utilities
# ---------------------------------------------------------
def run_step(module: str, project_root: Path, repo_root: Path):
    """
    Run a python module as a subprocess with correct PYTHONPATH.
    Used for ML / analysis stages that must be isolated.
    """
    print(f"\n--- [CI STEP] {module} ---")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)
    env["TARGET_REPO"] = str(repo_root)
    env["CI_MODE"] = "1"
    env["CI_WORKSPACE"] = str(project_root / "ci_workspace")

    try:
        subprocess.run(
            [sys.executable, "-m", module],
            cwd=project_root,
            env=env,
            check=True,
        )
    except subprocess.CalledProcessError:
        raise CIError(f"Step failed: {module}")


# ---------------------------------------------------------
# Main CI pipeline
# ---------------------------------------------------------
def run_analysis(repo_root: Path):
    """
    Run the full ML-guided test-risk analysis pipeline
    INSIDE a repository (CI mode).
    """

    repo_root = repo_root.resolve()
    project_root = Path(__file__).resolve().parents[1]

    print("\n🚦 STARTING CI ANALYSIS")
    print(f"📁 Target repo: {repo_root}")
    print(f"🧠 Tool root  : {project_root}")

    # -------------------------------------------------
    # Phase 1: Feature extraction from target repo
    # -------------------------------------------------
    run_step("ml.build_validation_dataset", project_root, repo_root)

    # -------------------------------------------------
    # Phase 2: ML inference
    # -------------------------------------------------
    run_step("ml.inference", project_root, repo_root)

    # -------------------------------------------------
    # Phase 3: Coverage collection on repo
    # -------------------------------------------------
    run_step("analysis.coverage", project_root, repo_root)

    # -------------------------------------------------
    # Phase 4: Post-ML aggregation (risk computation)
    # -------------------------------------------------
    run_step("analysis.post_ml_aggregate", project_root, repo_root)

    print("\n✅ CI ANALYSIS COMPLETE")


# ---------------------------------------------------------
# Defensive main (should not be used directly)
# ---------------------------------------------------------
if __name__ == "__main__":
    raise RuntimeError(
        "ci.runner is not meant to be executed directly.\n"
        "Use one of:\n"
        "  python -m ci.in_repo\n"
        "  python -m ci.clone_repo <git-url>"
    )
