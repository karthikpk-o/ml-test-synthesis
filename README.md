
# Machine Learning–Guided Code Smell Detection for Targeted Test Synthesis in Python

This project presents a practical system for identifying testing risk in Python codebases by combining machine learning–based code smell detection with dynamic test coverage analysis. Rather than automatically generating tests, the system prioritizes testing effort by identifying high-risk, under-tested code regions and synthesizing actionable test recommendations.


## 1. Project Overview

Modern Python projects often contain complex code that is insufficiently tested. While code smells indicate maintainability issues, and coverage tools indicate test execution, neither alone provides guidance on *where testing effort should be focused*.

This project addresses that gap by:

1. Detecting code smells using a machine learning model trained on static code metrics  
2. Measuring runtime test coverage at the function level  
3. Combining both signals to classify **testing risk**  
4. Generating **test synthesis guidance** to help developers prioritize testing and refactoring  


## 2. System Architecture

The system operates in two distinct phases:

### Offline Phase (Machine Learning)
- Extract static code metrics using Radon  
- Label functions using heuristic-based smell definitions  
- Train an SVM model to predict smelly functions  
- Persist the trained model for inference  

### Online Phase (Analysis Pipeline)
- Analyze a target repository  
- Predict code smells using the trained model  
- Collect test coverage using `coverage.py`  
- Map coverage to individual functions  
- Classify each function into a risk category  
- Generate targeted test recommendations  


## 3. Workspace Layout (Generated)

The project uses an external **workspace directory**, generated automatically by the setup script.  
The workspace is **not** inside the project repository.


```
<project-root>/
├── workspace/
│   ├── target-repos/         # Cloned external repositories (read-only)
│   └── venvs/                # One virtual environment per repo + tool
└── ml-test-synthesis/        # This project repository
```

The workspace is treated as an execution environment and is never committed to version control.


## 4. Project Repository Structure
```
ml-test-synthesis/
├── analysis/                 # Coverage, mapping, risk classification, ML integration
├── config/                   # Centralized path definitions (cross-platform)
├── data/                     # Persisted datasets and outputs
│   ├── training/             # Training datasets (heuristically labeled)
│   ├── validation/           # Validation datasets (unlabeled)
│   └── processed/            # ML predictions + final analysis results
├── ml/                       # Offline ML scripts (dataset build, training, inference)
├── models/                   # Trained ML model and scaler
├── recommendations/          # Rule-based test recommendation engine
├── reporting/                # Placeholder files for future visualization (not executed)
├── scripts/                  # Workspace setup + full pipeline orchestration
├── requirements.txt
└── README.md
```


## 5. Automated Setup (Recommended)

From a directory of your choice, clone the repository and run the following commands:

### Prerequisites
- Python 3.9+  
- Git  

### Setup Command

```bash
git clone <your forked repo link>
cd ml-test-synthesis
python scripts/setup_workspace.py
```

This script:

-   Creates the `workspace/` directory at the repository root level
    
-   Clones all target repositories into `workspace/target-repos/`
    
-   Checks out pinned tags/commits
    
-   Creates isolated virtual environments under `workspace/venvs/`
    
-   Installs all required dependencies
    

## 6. Repository Pinning & Reproducibility

All repositories are pinned to specific tagged releases or commit hashes to ensure deterministic results. Repository versions are defined directly in the setup script.

This ensures:

-   Identical analysis across machines
    
-   Stable ML results
    
-   Reproducible evaluation
    

## 6.1 Training and Validation Repositories

### Training Repositories

Used exclusively to build the ML dataset and train the code smell detection model.

Examples:

-   `requests`
    
-   `flask`
    
-   `click`
    

### Validation Repositories

Never used during training. Used to evaluate generalization and the end-to-end pipeline.

Examples:

-   `attrs`
    
-   `jinja2`
    
-   `itsdangerous`
    

## 7. Virtual Environments

|Purpose  | Virtual Environment |
|--|--|
|Tool / orchestration| `workspace/venvs/ml-test-synthesis` |
|Coverage for requests|`workspace/venvs/requests`|
|Coverage for flask|`workspace/venvs/flask`|
|Coverage for click|`workspace/venvs/click`|

Target repository dependencies must never be installed into the tool environment.


## 8. Execution Guide (End-to-End)

### Step 1: Activate the tool environment
Run the following command from the root directory `<project-root>/`

```bash
source workspace/venvs/ml-test-synthesis/bin/activate   # Linux/macOS
workspace\venvs\ml-test-synthesis\Scripts\activate      # Windows
```

### Step 2: Run the full pipeline

```bash
cd ml-test-synthesis
python scripts/run_full_pipeline.py
```

This executes, in order:

1.  Training dataset construction
    
2.  Validation dataset construction
    
3.  ML model training
    
4.  ML inference on validation repositories
    
5.  Coverage-aware risk analysis and test recommendation synthesis
    

### Output

The final analysis results are written to:

```
data/processed/final_results.csv
```

Each row corresponds to one function and includes static metrics, ML smell label, runtime coverage, risk category, and recommended testing actions.

## 9. Risk Categories
| Category | Description |
|--|--|
| Hidden Risk | Smelly code with low or zero coverage |
|Refactor Candidate|Smelly but adequately tested code|
|Low Value|Simple, untested code|
|Safe Zone|Clean and well-tested code|

## 10. Test Synthesis Strategy

The system generates **test guidance**, not test code. Recommendations are derived from:

-   Coverage gaps
    
-   Cyclomatic complexity
    
-   Method size
    
-   Dependency complexity

## 11. Datasets and Machine Learning

Static code metrics are extracted directly from pinned repositories and processed in memory during dataset construction.

Persisted datasets:

-   `data/training/` — heuristically labeled datasets for ML training
    
-   `data/validation/` — unlabeled datasets for ML inference
    
-   `data/processed/` — ML predictions and final pipeline results
    

Raw metric dumps are not persisted, as they can be deterministically regenerated from pinned repositories.

Trained models and scalers are stored in the `models/` directory.

## 12. Reporting and Visualization (Future Work)

The `reporting/` directory contains placeholder files reserved for future visualization or dashboard integration (e.g., Grafana). Reporting is not part of the current execution pipeline. All evaluation and analysis outputs are generated as structured CSV files under `data/processed/`.

## 13. Reproducibility Statement

All experiments are fully reproducible. Repositories are pinned to immutable versions, environments are isolated, filesystem paths are centralized via configuration, and the entire workflow is executable via a single orchestration script.

## 14. Limitations

-   Smell labels are heuristic-based rather than manually curated
    
-   Coverage is approximated at the function level using line execution
    
-   The system provides guidance, not automated test generation
    

## 15. Conclusion

This project demonstrates that combining machine learning–guided code smell detection with coverage-aware analysis enables practical, risk-driven testing decisions in Python systems. The approach is scalable, reproducible, and aligned with real-world development constraints.
