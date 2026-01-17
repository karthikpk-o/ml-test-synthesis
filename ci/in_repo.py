from pathlib import Path
import shutil
import sys

from ci.runner import run_analysis, CIError


def ensure_tool_available(tool: str):
    """
    Ensure required CLI tools exist in PATH.
    """
    if shutil.which(tool) is None:
        raise CIError(
            f"Required tool not found in PATH: {tool}. "
            f"Ensure dependencies are installed before running CI."
        )


def main():
    """
    CI entrypoint for running analysis inside an existing repository.

    Assumptions:
    - This script is executed INSIDE the target repo
    - pytest works
    - coverage works
    - dependencies are already installed
    """

    repo_root = Path.cwd().resolve()

    print(f"📁 Running CI analysis in repo: {repo_root}")

    # -------------------------------------------------
    # Basic sanity checks
    # -------------------------------------------------
    ensure_tool_available("pytest")
    ensure_tool_available("coverage")

    # Optional but useful signal
    if not (repo_root / "pyproject.toml").exists() and not (
        repo_root / "setup.py"
    ).exists():
        print(
            "⚠️  Warning: No pyproject.toml or setup.py found. "
            "Proceeding anyway."
        )

    # -------------------------------------------------
    # Run the full CI pipeline
    # -------------------------------------------------
    try:
        run_analysis(repo_root)
    except CIError as e:
        print(f"\n❌ CI FAILED: {e}")
        sys.exit(1)

    print("\n🎉 CI PASSED")


if __name__ == "__main__":
    main()
