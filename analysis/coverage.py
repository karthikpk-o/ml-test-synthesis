import subprocess
import json
from pathlib import Path
import sys


class CoverageError(Exception):
    pass


def detect_package_name(repo_path: Path) -> str:
    """
    Detect the primary Python package in a repository.

    Supports:
    - Flat layout: repo/<pkg>/__init__.py
    - Src layout:  repo/src/<pkg>/__init__.py

    Fails explicitly if the package cannot be uniquely determined.
    """

    candidates = []

    # Flat layout
    for p in repo_path.iterdir():
        if (
            p.is_dir()
            and (p / "__init__.py").exists()
            and p.name not in {"tests", "test"}
        ):
            candidates.append(p.name)

    # src/ layout
    src_dir = repo_path / "src"
    if src_dir.exists():
        for p in src_dir.iterdir():
            if p.is_dir() and (p / "__init__.py").exists():
                candidates.append(p.name)

    candidates = sorted(set(candidates))

    if len(candidates) != 1:
        raise CoverageError(
            f"Could not uniquely detect Python package in {repo_path}. "
            f"Found candidates: {candidates}"
        )

    return candidates[0]


def pytest_args() -> list[str]:
    """
    Global pytest exclusions for environment-sensitive tests.

    These exclusions:
    - remove static type-checking tests (mypy / pyright)
    - remove deprecation-warning assertion tests
    - do NOT affect runtime execution paths
    """
    return ["-k", "not mypy and not TestAssoc"]


def collect_coverage(repo_path: str) -> dict:
    repo_path = Path(repo_path).resolve()

    if not repo_path.exists():
        raise CoverageError(f"Repo path does not exist: {repo_path}")

    repo_name = repo_path.name
    package_name = detect_package_name(repo_path)

    # Build coverage command
    cmd = [
        "coverage",
        "run",
        "--rcfile=/dev/null",          # ignore repo-specific configs
        f"--source={package_name}",    # restrict to Python package only
        "-m",
        "pytest",
    ]
    cmd += pytest_args()

    try:
        subprocess.run(
            cmd,
            cwd=repo_path,
            check=True,
        )
    except subprocess.CalledProcessError:
        raise CoverageError(
            f"Coverage execution failed for repository: {repo_name}"
        )

    # Generate JSON report
    try:
        subprocess.run(
            ["coverage", "json", "-o", "coverage.json"],
            cwd=repo_path,
            check=True,
        )
    except subprocess.CalledProcessError:
        raise CoverageError(
            f"Coverage JSON generation failed for repository: {repo_name}"
        )

    coverage_file = repo_path / "coverage.json"
    if not coverage_file.exists():
        raise CoverageError("coverage.json not generated")

    with open(coverage_file, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python coverage.py <path-to-repo>")
        sys.exit(1)

    repo_path = Path(sys.argv[1]).resolve()
    repo_name = repo_path.name

    data_dir = Path(__file__).resolve().parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    try:
        coverage_data = collect_coverage(repo_path)

        output_file = data_dir / f"{repo_name}_coverage.json"
        with open(output_file, "w") as f:
            json.dump(coverage_data, f, indent=2)

        print(f"[OK] Coverage saved to: {output_file}")

    except CoverageError as e:
        print(f"[ERROR] {e}")
        sys.exit(2)
