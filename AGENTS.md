# Repository Guidelines

## Project Structure & Module Organization

The application is a small Python/Tkinter YOLO image-analysis tool.

- `yolo_demo.py`: thin backward-compatible entry point that re-exports from `yolo_app`.
- `yolo_app/`: application package — `config.py` (paths and constants), `models.py` (model specs and download logic), `analysis.py` (pure inference loop), `console.py` (GUI console widgets and stdout redirection), `viewer.py` (Tkinter `YoloViewer` and `main`).
- `train_model.py`: CLI script that fine-tunes a base model on `train_set/` (argparse; defaults reproduce the original run).
- `train_set/`: local training dataset in YOLO detection format (`data.yaml`, images, labels).
- `tests/`: pytest suite for non-UI logic.
- `object/`: input images displayed and analyzed by the application.
- `result/`: generated detection and segmentation images, grouped by model.
- `*.pt`: local YOLO model weights.
- `requirements.txt` / `pyproject.toml`: pinned runtime dependencies; `pyproject.toml` also declares the `dev` extra (pytest) and pytest configuration.

Keep new logic in the matching `yolo_app` module; add a new module only when it has a clear, independent responsibility.

## Build, Test, and Development Commands

Create and activate a virtual environment on Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the desktop application with:

```powershell
python .\yolo_demo.py
```

Before submitting changes, compile-check Python and run the tests with:

```powershell
python -m compileall yolo_app yolo_demo.py train_model.py
python -m pytest -q
```

## Coding Style & Naming Conventions

Follow PEP 8 with four-space indentation and type annotations for public methods and non-obvious values. Use `snake_case` for functions and variables, `PascalCase` for classes, and `UPPER_SNAKE_CASE` for module constants. Keep Tkinter callbacks short; move inference and file operations into focused helper methods. Preserve the existing `pathlib.Path` approach instead of introducing raw path strings.

Use UTF-8 for Python, Markdown, CSV, and HTML files. Verify Korean UI text after editing to prevent encoding corruption.

## Testing Guidelines

Run the pytest suite in `tests/` with `python -m pytest -q` (install pytest via `python -m pip install pytest` or the `dev` extra). New non-UI logic should include `pytest` tests named `tests/test_<feature>.py`. For GUI or inference changes, manually verify model selection, single-image analysis, batch analysis, cached-result behavior, and clean application shutdown. Do not rely on generated files already present in `result/`.

## Commit & Pull Request Guidelines

Use concise imperative commits such as `Add telemetry playback controls` or `Fix cached preview refresh`, consistent with the existing history. Keep unrelated changes in separate commits.

Pull requests should describe behavior changes, manual test steps, and any model or data assumptions. Include screenshots for GUI or dashboard changes and link related issues. Avoid committing `.venv/`, caches, generated results, private images, or newly downloaded model weights; use Git LFS or release assets when weights must be distributed.
