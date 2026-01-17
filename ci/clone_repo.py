import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from ci.runner import run_analysis, CIError


def run(cmd, cwd=None):
    print(f"→ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)


def ensure_git():
    if shutil.which("git") is None:
        raise CIError("git is required but not found in PATH")


def create_venv(venv_dir: Path):
    run([sys.executable, "-m", "venv", str(venv_dir)])


def venv_python(venv_dir: Path) -> Path:
    return venv_dir / (
        "Scripts/python.exe" if sys.platform == "win32" else "bin/python"
    )


def install_dependencies(python: Path, repo_dir: Path):
    run([str(python), "-m", "pip", "install", "--upgrade", "pip"])

    if (repo_dir / "requirements.txt").exists():
        run([str(python), "-m", "pip", "install", "-r", "requirements.txt"], cwd=repo_dir)

    if (repo_dir / "pyproject.toml").exists() or (repo_dir / "setup.py").exists():
        run([str(python), "-m", "pip", "install", "-e", "."], cwd=repo_dir)

    run([str(python), "-m", "pip", "install", "pytest", "coverage"])


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m ci.clone_repo <git-repo-url>")
        sys.exit(1)

    repo_url = sys.argv[1]
    ensure_git()

    with tempfile.TemporaryDirectory(prefix="ml_ci_") as tmp:
        tmp_path = Path(tmp)
        repo_dir = tmp_path / "repo"
        venv_dir = tmp_path / "venv"

        print(f"\n📥 Cloning repo: {repo_url}")
        run(["git", "clone", repo_url, str(repo_dir)])

        print("\n🐍 Creating virtual environment")
        create_venv(venv_dir)
        python = venv_python(venv_dir)

        print("\n📦 Installing repository dependencies")
        install_dependencies(python, repo_dir)

        print("\n🚦 Running ML-based CI analysis")
        try:
            # NOTE: tool runner is invoked from tool repo, 
            # but coverage step will use this venv python
            run_analysis(repo_dir, external_python=python)
        except CIError as e:
            print(f"\n❌ CI FAILED: {e}")
            sys.exit(1)

        print("\n🎉 CI PASSED")


if __name__ == "__main__":
    main()
