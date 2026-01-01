import subprocess
import json
import sys
from pathlib import Path


class CoverageError(Exception):
    pass


def collect_coverage(repo_path: str) -> dict:
    """
    Run pytest + coverage for a repository using its dedicated venv.

    Behavior:
    - Coverage is executed ONCE per repo
    - If pytest fails, coverage degrades to ZERO (returns {})
    - Pipeline never aborts due to test failures
    """

    repo_path = Path(repo_path).resolve()

    if not repo_path.exists():
        raise CoverageError(f"Repo path does not exist: {repo_path}")

    repo_name = repo_path.name

    # ----------------------------
    # Resolve repo-specific venv
    # ----------------------------
    bin_dir = "Scripts" if sys.platform == "win32" else "bin"
    exe_name = "python.exe" if sys.platform == "win32" else "python"

    venv_python = (
        repo_path.parents[2]    # <project-root>
        / "workspace"
        / "venvs"
        / repo_name
        / bin_dir
        / exe_name
    )

    if not venv_python.exists():
        raise CoverageError(
            f"Python venv not found for repo '{repo_name}' at {venv_python}"
        )

    # ----------------------------
    # Run coverage + pytest
    # ----------------------------
    try:
        subprocess.run(
            [
                str(venv_python),
                "-m",
                "coverage",
                "run",
                "-m",
                "pytest",
                "--maxfail=1",
                "--disable-warnings",
            ],
            cwd=repo_path,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        stdout = e.stdout.decode(errors="ignore") if e.stdout else ""
        stderr = e.stderr.decode(errors="ignore") if e.stderr else ""

        print(
            f"⚠️ Pytest failed for {repo_name}. "
            f"Coverage degraded to ZERO.\n"
            f"--- STDOUT ---\n{stdout}\n"
            f"--- STDERR ---\n{stderr}\n"
        )
        return {}

    # ----------------------------
    # Generate coverage JSON
    # ----------------------------
    try:
        subprocess.run(
            [
                str(venv_python),
                "-m",
                "coverage",
                "json",
                "-o",
                "coverage.json",
            ],
            cwd=repo_path,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        print(
            f"⚠️ Coverage JSON generation failed for {repo_name}. "
            "Coverage degraded to ZERO."
        )
        return {}

    coverage_file = repo_path / "coverage.json"

    if not coverage_file.exists():
        print(
            f"⚠️ coverage.json not generated for {repo_name}. "
            "Coverage degraded to ZERO."
        )
        return {}

    # ----------------------------
    # Load coverage data
    # ----------------------------
    try:
        with open(coverage_file, "r") as f:
            return json.load(f)
    except Exception as e:
        print(
            f"⚠️ Failed to parse coverage.json for {repo_name}: {e}. "
            "Coverage degraded to ZERO."
        )
        return {}
