#!/usr/bin/env python3
import shutil
from pathlib import Path
import sys
from config.paths import PROJECT_ROOT, GLOBAL_ROOT, DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, WORKSPACE_DIR, REPORTS_DIR
from config.paths import CI_WORKSPACE_COVERAGE, CI_WORKSPACE_METRICS, CI_WORKSPACE_REPORTS, CI_WORKSPACE_PROCESSED, CI_WORKSPACE
from config.paths import TRAINING_DATA_DIR, VALIDATION_DATA_DIR
# ---------------------------------------------------------
# Path resolution (authoritative)
# ---------------------------------------------------------
THIS_FILE = Path(__file__).resolve()
# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def remove_path(path: Path):
    if not path.exists():
        print(f"⚠️  NOT FOUND: {path}")
        return

    if path.is_file():
        print(f"🗑️  Removing file: {path}")
        path.unlink()
    elif path.is_dir():
        print(f"🗑️  Removing directory: {path}")
        shutil.rmtree(path)


def remove_dir_contents_preserve_gitkeep(dir_path: Path):
    if not dir_path.exists():
        print(f"⚠️  Directory not found: {dir_path}")
        return

    for p in dir_path.iterdir():
        if p.name == ".gitkeep":
            print(f"🔒 Preserving: {p}")
            continue
        remove_path(p)

# ---------------------------------------------------------
# Cleanup logic
# ---------------------------------------------------------
def main():
    print("🧭 cleanup.py location :", THIS_FILE)
    print("🧭 project root        :", GLOBAL_ROOT)
    print("🧭 ml-test-synthesis   :", PROJECT_ROOT)
    print()

    # Hard sanity check
    if not PROJECT_ROOT.exists() or not DATA_DIR.exists():
        print("❌ FATAL: ml-test-synthesis layout not detected correctly.")
        sys.exit(1)

    print("⚠️  WARNING: Destructive cleanup operation")
    print("This will DELETE:")
    print(" - contents of ml-test-synthesis/data/processed/ (except .gitkeep)")
    print(" - coverage artifacts under ml-test-synthesis/data/")
    print(" - contents of ml-test-synthesis/models/ (except .gitkeep)")
    print(" - entire <project-root>/workspace/\n")

    resp = input("Type 'yes' to continue: ").strip().lower()
    if resp != "yes":
        print("❌ Aborted. No files were deleted.")
        return

    print("\n🧹 Cleaning project artifacts...\n")

    # remove processed dir
    remove_dir_contents_preserve_gitkeep(PROCESSED_DATA_DIR)

    #remove reports dir
    remove_dir_contents_preserve_gitkeep(REPORTS_DIR)

    #remove train dir
    remove_dir_contents_preserve_gitkeep(TRAINING_DATA_DIR)

    #remove validation dir
    remove_dir_contents_preserve_gitkeep(VALIDATION_DATA_DIR)

    #remove ci workspace files
    remove_dir_contents_preserve_gitkeep(CI_WORKSPACE_COVERAGE)
    remove_dir_contents_preserve_gitkeep(CI_WORKSPACE_METRICS)
    remove_dir_contents_preserve_gitkeep(CI_WORKSPACE_PROCESSED)
    remove_dir_contents_preserve_gitkeep(CI_WORKSPACE_REPORTS)

    # 2️⃣ Clean processed directory contents (preserve folder + .gitkeep)
    

    # 3️⃣ Remove coverage artifacts under data/
    for pattern in ["*_coverage.json", "coverage.json", ".coverage"]:
        for p in DATA_DIR.rglob(pattern):
            remove_path(p)
        for p in CI_WORKSPACE.rglob(pattern):
            remove_path(p)

    # 4️⃣ Clean models directory contents (preserve folder + .gitkeep)
    remove_dir_contents_preserve_gitkeep(MODELS_DIR)

    # 5️⃣ Remove entire workspace
    remove_path(WORKSPACE_DIR)

    print("\n✨ Cleanup complete. Fresh pipeline ready.")

# ---------------------------------------------------------
if __name__ == "__main__":
    main()
