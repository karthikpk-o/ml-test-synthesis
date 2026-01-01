import subprocess
import sys
from pathlib import Path

# ----------------------------
# Configuration (PINNED REPOS)
# ----------------------------
REPOS = {
    "training": {
        "requests": ("https://github.com/psf/requests.git", "v2.31.0"),
        "flask": ("https://github.com/pallets/flask.git", "2.3.3"),
        "click": ("https://github.com/pallets/click.git", "8.1.7"),
    },
    "validation": {
        "attrs": ("https://github.com/python-attrs/attrs.git", "23.2.0"),
        "jinja2": ("https://github.com/pallets/jinja.git", "3.1.3"),
        "itsdangerous": ("https://github.com/pallets/itsdangerous.git", "2.1.2"),
    },
}

ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT / "workspace"
TARGET_REPOS = WORKSPACE / "target-repos"
VENVS = WORKSPACE / "venvs"


def run(cmd, cwd=None):
    print(f"→ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)


def create_venv(path: Path):
    if not path.exists():
        run([sys.executable, "-m", "venv", str(path)])


def pip_install(venv: Path, packages):
    python = venv / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    run([str(python), "-m", "pip", "install", "--upgrade", "pip"])
    run([str(python), "-m", "pip", "install"] + packages)


def setup_tool_env():
    print("\n[SETUP] Tool environment")
    tool_venv = VENVS / "ml-test-synthesis"
    create_venv(tool_venv)
    pip_install(tool_venv, ["-r", "requirements.txt"])


def setup_repo(name, url, ref):
    print(f"\n[SETUP] Repo: {name}")
    repo_path = TARGET_REPOS / name
    venv_path = VENVS / name

    if not repo_path.exists():
        run(["git", "clone", url, str(repo_path)])

    run(["git", "fetch", "--all", "--tags"], cwd=repo_path)
    run(["git", "checkout", ref], cwd=repo_path)

    create_venv(venv_path)

    python = venv_path / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")

    # Upgrade pip
    run([str(python), "-m", "pip", "install", "--upgrade", "pip"])

    # 1️⃣ Install runtime requirements if present
    req = repo_path / "requirements.txt"
    if req.exists():
        run([str(python), "-m", "pip", "install", "-r", str(req)])

    # 2️⃣ Install the package itself (CRITICAL)
    run([str(python), "-m", "pip", "install", "-e", str(repo_path)])

    # 3️⃣ Install minimal test tooling
    run([str(python), "-m", "pip", "install", "pytest", "coverage", "hypothesis", "freezegun"])




def main():
    print("=== Setting up ML Test Synthesis Workspace ===")

    WORKSPACE.mkdir(exist_ok=True)
    TARGET_REPOS.mkdir(exist_ok=True)
    VENVS.mkdir(exist_ok=True)

    setup_tool_env()

    for category, repos in REPOS.items():
        print(f"\n[{category.upper()} REPOSITORIES]")
        for name, (url, ref) in repos.items():
            setup_repo(name, url, ref)

    print("\n✔ Workspace setup complete")


if __name__ == "__main__":
    main()
