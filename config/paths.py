from pathlib import Path

# __file__ is <project-root>/ml-test-synthesis/config/paths.py
_this_file = Path(__file__).resolve()

# PROJECT_ROOT = <project-root>/ml-test-synthesis/
PROJECT_ROOT = _this_file.parents[1]

# GLOBAL_ROOT = <project-root>/
GLOBAL_ROOT = PROJECT_ROOT.parent

# WORKSPACE_DIR = <project-root>/workspace/
WORKSPACE_DIR = GLOBAL_ROOT / "workspace"

# TARGET_REPOS_DIR = <project-root>/workspace/target-repos/
TARGET_REPOS_DIR = WORKSPACE_DIR / "target-repos"

# VENVS_DIR = <project-root>/workspace/venvs/
VENVS_DIR = WORKSPACE_DIR / "venvs"

# Data and Models remain inside the project repository
DATA_DIR = PROJECT_ROOT / "data"
TRAINING_DATA_DIR = DATA_DIR / "train"
VALIDATION_DATA_DIR = DATA_DIR / "validation"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
REPORTS_DIR = DATA_DIR / "reports"
MODELS_DIR = PROJECT_ROOT / "models"

#CI PATHS
CI_WORKSPACE = PROJECT_ROOT / "ci_workspace"
CI_WORKSPACE_COVERAGE = CI_WORKSPACE / "coverage"
CI_WORKSPACE_METRICS = CI_WORKSPACE / "metrics"
CI_WORKSPACE_PROCESSED = CI_WORKSPACE / "processed"
CI_WORKSPACE_REPORTS = CI_WORKSPACE / "reports"

# Repos for dataset
TRAINING_REPOS = {
    "requests",
    "flask",
    "click",
    "numpy",
    "django",
}

VALIDATION_REPOS = {
    "attrs",
    "jinja2",
    "itsdangerous",
}
