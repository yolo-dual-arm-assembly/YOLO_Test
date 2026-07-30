# Repository Guidelines

## Project Structure & Module Organization

The application is a small Python/Tkinter YOLO image-analysis tool.

- `yolo_demo.py`: GUI, model loading, inference, previews, and result handling.
- `object/`: input images displayed and analyzed by the application.
- `result/`: generated detection and segmentation images, grouped by model.
- `dashboard.html` and `run_a.csv`: standalone robot telemetry dashboard and its source log.
- `*.pt`: local YOLO model weights.
- `requirements.txt`: pinned Python dependency entry point.

Keep reusable Python logic near the top-level application until a module has a clear, independent responsibility. If the code grows, place modules under `src/` and tests under `tests/`.

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

Open `dashboard.html` directly in a browser to inspect telemetry visualizations. Before submitting changes, compile-check Python with:

```powershell
python -m py_compile .\yolo_demo.py
```

## Coding Style & Naming Conventions

Follow PEP 8 with four-space indentation and type annotations for public methods and non-obvious values. Use `snake_case` for functions and variables, `PascalCase` for classes, and `UPPER_SNAKE_CASE` for module constants. Keep Tkinter callbacks short; move inference and file operations into focused helper methods. Preserve the existing `pathlib.Path` approach instead of introducing raw path strings.

Use UTF-8 for Python, Markdown, CSV, and HTML files. Verify Korean UI text after editing to prevent encoding corruption.

## Testing Guidelines

No automated test suite is currently configured. New non-UI logic should include `pytest` tests named `tests/test_<feature>.py`. For GUI or inference changes, manually verify model selection, single-image analysis, batch analysis, cached-result behavior, and clean application shutdown. Do not rely on generated files already present in `result/`.

## Commit & Pull Request Guidelines

No usable local Git history is available, so use concise imperative commits such as `Add telemetry playback controls` or `Fix cached preview refresh`. Keep unrelated changes in separate commits.

Pull requests should describe behavior changes, manual test steps, and any model or data assumptions. Include screenshots for GUI or dashboard changes and link related issues. Avoid committing `.venv/`, caches, generated results, private images, or newly downloaded model weights; use Git LFS or release assets when weights must be distributed.
