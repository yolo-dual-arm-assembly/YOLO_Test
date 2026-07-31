from __future__ import annotations

import queue
import sys
import threading
import traceback
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from PIL import Image, ImageOps, ImageTk
from ultralytics import YOLO
from ultralytics.utils.downloads import attempt_download_asset


PROJECT_DIR = Path(__file__).resolve().parent
INPUT_DIR = PROJECT_DIR / "object"
OUTPUT_DIR = PROJECT_DIR / "result"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp"}
PREVIEW_SIZE = (620, 650)
MODEL_OPTIONS = {
    "Robot Custom (POC · 학습된 로봇 객체 탐지 모델)": "best.pt",
    "YOLOv8n (Low · 가장 가벼움 · 빠른 객체 탐지/저사양 CPU에 적합)": "yolov8n.pt",
    "YOLOv8m (Advanced · 정확도와 속도의 균형 · 일반 객체 탐지에 적합)": "yolov8m.pt",
    "YOLO11m-seg (Advanced · 객체 윤곽 마스크 · 정밀 영역 분할에 특화)": "yolo11m-seg.pt",
}
MODEL_FILENAMES = tuple(dict.fromkeys(MODEL_OPTIONS.values()))
LOCAL_MODEL_FILENAMES = {"best.pt"}
DOWNLOADABLE_MODEL_FILENAMES = tuple(
    filename for filename in MODEL_FILENAMES if filename not in LOCAL_MODEL_FILENAMES
)
DEFAULT_MODEL_LABEL = next(
    label for label, filename in MODEL_OPTIONS.items() if filename == "yolo11m-seg.pt"
)


def missing_model_paths(project_dir: Path | None = None) -> list[Path]:
    """Return model paths that must be downloaded before analysis."""
    root = PROJECT_DIR if project_dir is None else project_dir
    return [
        root / filename
        for filename in DOWNLOADABLE_MODEL_FILENAMES
        if not (root / filename).is_file()
    ]


def download_model(model_path: Path) -> Path:
    """Download one official Ultralytics model to its project path."""
    downloaded_path = Path(attempt_download_asset(model_path))
    if not downloaded_path.is_file():
        raise FileNotFoundError(f"모델 다운로드에 실패했습니다: {model_path.name}")
    return downloaded_path


class _ConsoleStream:
    """Send standard output to the GUI without blocking worker threads."""

    def __init__(self, output_queue: queue.SimpleQueue[str], original: object) -> None:
        self._output_queue = output_queue
        self._original = original

    def write(self, message: str) -> int:
        if message:
            self._output_queue.put(message)
            try:
                self._original.write(message)  # type: ignore[attr-defined]
            except Exception:
                pass
        return len(message)

    def flush(self) -> None:
        try:
            self._original.flush()  # type: ignore[attr-defined]
        except Exception:
            pass


class YoloViewer(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("YOLO 이미지 분석 비교")
        self.geometry("1500x850")
        self.minsize(1050, 650)

        INPUT_DIR.mkdir(exist_ok=True)
        OUTPUT_DIR.mkdir(exist_ok=True)

        self.image_paths: list[Path] = []
        self.original_photo: ImageTk.PhotoImage | None = None
        self.result_photo: ImageTk.PhotoImage | None = None
        self.model: YOLO | None = None
        self.loaded_model_path: Path | None = None
        self.processing = False
        self.skip_existing = True
        self.model_choice = tk.StringVar(value=DEFAULT_MODEL_LABEL)
        self._console_queue: queue.SimpleQueue[str] = queue.SimpleQueue()
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr

        self._build_ui()
        sys.stdout = _ConsoleStream(self._console_queue, self._original_stdout)
        sys.stderr = _ConsoleStream(self._console_queue, self._original_stderr)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(100, self._drain_console)
        self.refresh_images()
        self.after(100, self._prepare_models)

    def _build_ui(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        sidebar = ttk.Frame(self, padding=10)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.rowconfigure(3, weight=1)

        ttk.Label(sidebar, text="모델 선택", font=("", 12, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        self.model_combo = ttk.Combobox(
            sidebar,
            textvariable=self.model_choice,
            values=list(MODEL_OPTIONS),
            state="readonly",
            width=64,
        )
        self.model_combo.grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=(4, 12)
        )
        self.model_combo.bind("<<ComboboxSelected>>", self._on_model_changed)

        ttk.Label(sidebar, text="이미지 목록", font=("", 14, "bold")).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(0, 8)
        )

        self.image_list = tk.Listbox(
            sidebar,
            width=34,
            activestyle="dotbox",
            exportselection=False,
        )
        self.image_list.grid(row=3, column=0, sticky="nsew")
        self.image_list.bind("<<ListboxSelect>>", self._on_select)

        scrollbar = ttk.Scrollbar(
            sidebar, orient="vertical", command=self.image_list.yview
        )
        scrollbar.grid(row=3, column=1, sticky="ns")
        self.image_list.configure(yscrollcommand=scrollbar.set)

        button_frame = ttk.Frame(sidebar)
        button_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        button_frame.columnconfigure((0, 1), weight=1)
        
        self.selected_button = ttk.Button(
            button_frame, text="선택 이미지 분석", command=self.analyze_selected
        )
        self.selected_button.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        self.all_button = ttk.Button(
            button_frame, text="전체 다시 분석", command=self.analyze_all
        )
        self.all_button.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        content = ttk.Frame(self, padding=(0, 10, 10, 10))
        content.grid(row=0, column=1, sticky="nsew")
        content.columnconfigure((0, 2), weight=1, uniform="preview")
        content.columnconfigure(1, weight=0)
        content.rowconfigure(1, weight=1)

        ttk.Label(content, text="변환 전", font=("", 14, "bold")).grid(
            row=0, column=0, pady=(0, 8)
        )
        ttk.Label(content, text="변환 후", font=("", 14, "bold")).grid(
            row=0, column=2, pady=(0, 8)
        )

        self.original_label = ttk.Label(
            content, text="이미지를 선택하세요", anchor="center", relief="solid"
        )
        self.original_label.grid(row=1, column=0, sticky="nsew", padx=(0, 5))

        reanalyze_panel = ttk.Frame(content)
        reanalyze_panel.grid(row=1, column=1, padx=10)

        self.compare_reanalyze_button = ttk.Button(
            reanalyze_panel,
            text="이 이미지만\n다시 분석 →",
            command=self.analyze_selected,
            width=16,
        )
        self.compare_reanalyze_button.pack()

        self.selected_progress = ttk.Progressbar(
            reanalyze_panel,
            mode="determinate",
            maximum=100,
            length=135,
        )
        self.selected_progress.pack(fill="x", pady=(12, 4))

        self.selected_progress_text = tk.StringVar(value="대기 중")
        ttk.Label(
            reanalyze_panel,
            textvariable=self.selected_progress_text,
            anchor="center",
        ).pack(fill="x")

        self.result_label = ttk.Label(
            content, text="분석 결과가 없습니다", anchor="center", relief="solid"
        )
        self.result_label.grid(row=1, column=2, sticky="nsew", padx=(5, 0))

        self.status = tk.StringVar(value="준비")
        ttk.Label(content, textvariable=self.status, anchor="w").grid(
            row=2, column=0, columnspan=3, sticky="ew", pady=(8, 0)
        )
        self.progress = ttk.Progressbar(content, mode="determinate")
        self.progress.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(4, 0))

        console_frame = ttk.LabelFrame(self, text="콘솔 출력", padding=(8, 6))
        console_frame.grid(
            row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 10)
        )
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)

        self.console = tk.Text(
            console_frame,
            height=9,
            wrap="word",
            state="disabled",
            background="#1e1e1e",
            foreground="#d4d4d4",
            insertbackground="#ffffff",
            font=("Consolas", 10),
        )
        self.console.grid(row=0, column=0, sticky="nsew")
        console_scrollbar = ttk.Scrollbar(
            console_frame, orient="vertical", command=self.console.yview
        )
        console_scrollbar.grid(row=0, column=1, sticky="ns")
        self.console.configure(yscrollcommand=console_scrollbar.set)
        ttk.Button(console_frame, text="지우기", command=self._clear_console).grid(
            row=1, column=0, columnspan=2, sticky="e", pady=(6, 0)
        )

    def _drain_console(self) -> None:
        messages: list[str] = []
        while True:
            try:
                messages.append(self._console_queue.get_nowait())
            except queue.Empty:
                break

        if messages:
            self.console.configure(state="normal")
            self.console.insert(tk.END, "".join(messages))
            if int(self.console.index("end-1c").split(".")[0]) > 1_000:
                self.console.delete("1.0", "200.0")
            self.console.see(tk.END)
            self.console.configure(state="disabled")

        if self.winfo_exists():
            self.after(100, self._drain_console)

    def _clear_console(self) -> None:
        self.console.configure(state="normal")
        self.console.delete("1.0", tk.END)
        self.console.configure(state="disabled")

    def _on_close(self) -> None:
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr
        self.destroy()

    def refresh_images(self) -> None:
        selected_name = self._selected_path().name if self._selected_path() else None
        self.image_paths = sorted(
            path
            for path in INPUT_DIR.iterdir()
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
        )

        self.image_list.delete(0, tk.END)
        selected_index = 0
        for index, image_path in enumerate(self.image_paths):
            result_exists = self._result_path(image_path).exists()
            marker = "✓" if result_exists else "○"
            self.image_list.insert(tk.END, f"{marker}  {image_path.name}")
            if image_path.name == selected_name:
                selected_index = index

        if self.image_paths:
            self.image_list.selection_set(selected_index)
            self.image_list.see(selected_index)
            self.show_selected()
        else:
            self.status.set(f"입력 이미지가 없습니다: {INPUT_DIR}")

    def _prepare_models(self) -> None:
        missing_models = missing_model_paths()
        if not missing_models:
            self._start_initial_analysis()
            return

        self.processing = True
        self._set_buttons_enabled(False)
        self.progress.configure(maximum=len(missing_models), value=0)
        self.status.set(f"누락 모델 {len(missing_models)}개 다운로드 준비 중...")
        print(
            "[model download start] "
            + ", ".join(model_path.name for model_path in missing_models)
        )
        threading.Thread(
            target=self._download_models_worker,
            args=(missing_models,),
            daemon=True,
        ).start()

    def _download_models_worker(self, model_paths: list[Path]) -> None:
        try:
            for index, model_path in enumerate(model_paths, start=1):
                self.after(
                    0,
                    self.status.set,
                    f"[{index}/{len(model_paths)}] 다운로드 중: {model_path.name}",
                )
                download_model(model_path)
                print(
                    f"[{index}/{len(model_paths)}] model ready: {model_path.name}"
                )
                self.after(
                    0,
                    self._model_download_progress,
                    index,
                    len(model_paths),
                    model_path.name,
                )
            self.after(0, self._model_download_finished, len(model_paths))
        except Exception as error:
            traceback.print_exc()
            self.after(0, self._model_download_failed, str(error))

    def _model_download_progress(
        self, current: int, total: int, model_name: str
    ) -> None:
        self.progress.configure(value=current)
        self.status.set(f"[{current}/{total}] 모델 준비 완료: {model_name}")

    def _model_download_finished(self, count: int) -> None:
        self.processing = False
        self._set_buttons_enabled(True)
        self.progress.configure(value=count)
        self.status.set(f"모델 다운로드 완료: {count}개")
        print(f"[model download complete] models={count}")
        self.after(100, self._start_initial_analysis)

    def _model_download_failed(self, error: str) -> None:
        self.processing = False
        self._set_buttons_enabled(True)
        self.progress.configure(value=0)
        self.status.set("모델 다운로드 중 오류가 발생했습니다.")
        messagebox.showerror(
            "모델 다운로드 오류",
            "인터넷 연결을 확인한 뒤 프로그램을 다시 실행해 주세요.\n\n"
            f"{error}",
        )

    def _start_initial_analysis(self) -> None:
        if not self.image_paths:
            return
        if not self.model_path.exists():
            messagebox.showerror("모델 오류", f"모델 파일이 없습니다:\n{self.model_path}")
            return

        existing = [
            path for path in self.image_paths if self._result_path(path).exists()
        ]

        if existing:
            self.skip_existing = messagebox.askyesno(
                "기존 결과 확인",
                f"{self.model_path.name} 모델로 이미 분석한 이미지는 생략할까요?\n\n"
                "Yes: 기존 결과 유지\nNo: 모든 이미지 다시 분석",
            )
            targets = (
                [path for path in self.image_paths if not self._result_path(path).exists()]
                if self.skip_existing
                else self.image_paths
            )
        else:
            targets = self.image_paths

        if targets:
            self._run_analysis(targets)
        else:
            self.status.set("모든 이미지가 이미 분석된 상태입니다.")

    @property
    def model_path(self) -> Path:
        return PROJECT_DIR / MODEL_OPTIONS[self.model_choice.get()]

    def _on_model_changed(self, _event: tk.Event) -> None:
        self.model = None
        self.loaded_model_path = None
        self.selected_progress.configure(value=0)
        self.selected_progress_text.set("대기 중")
        self.progress.configure(value=0)
        self.refresh_images()
        self.status.set(f"모델 전환 완료: {self.model_path.name}")

    def _selected_path(self) -> Path | None:
        selection = self.image_list.curselection()
        if not selection or selection[0] >= len(self.image_paths):
            return None
        return self.image_paths[selection[0]]

    def _result_path(
        self, image_path: Path, model_path: Path | None = None
    ) -> Path:
        selected_model = model_path or self.model_path
        return OUTPUT_DIR / selected_model.stem / f"det_{image_path.name}"

    def _on_select(self, _event: tk.Event) -> None:
        self.show_selected()

    def show_selected(self) -> None:
        image_path = self._selected_path()
        if image_path is None:
            return

        self.original_photo = self._load_preview(image_path)
        self.original_label.configure(image=self.original_photo, text="")

        result_path = self._result_path(image_path)
        if result_path.exists():
            self.result_photo = self._load_preview(result_path)
            self.result_label.configure(image=self.result_photo, text="")
        else:
            self.result_photo = None
            self.result_label.configure(image="", text="아직 분석되지 않았습니다.")

        self.status.set(image_path.name)

    @staticmethod
    def _load_preview(path: Path) -> ImageTk.PhotoImage:
        with Image.open(path) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")
            image.thumbnail(PREVIEW_SIZE, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(image)

    def analyze_selected(self) -> None:
        image_path = self._selected_path()
        if image_path:
            self.selected_progress.configure(value=0)
            self.selected_progress_text.set("0% · 진행 중")
            self._run_analysis([image_path])

    def analyze_all(self) -> None:
        self._run_analysis(self.image_paths)

    def _run_analysis(self, targets: list[Path]) -> None:
        if self.processing or not targets:
            return
        if not self.model_path.exists():
            messagebox.showerror("모델 오류", f"모델 파일이 없습니다:\n{self.model_path}")
            return

        active_model_path = self.model_path
        self._result_path(targets[0], active_model_path).parent.mkdir(
            parents=True, exist_ok=True
        )
        self.processing = True
        self._set_buttons_enabled(False)
        self.progress.configure(maximum=len(targets), value=0)
        self.status.set(f"{len(targets)}개 이미지 분석 준비 중...")
        threading.Thread(
            target=self._analyze_worker,
            args=(list(targets), active_model_path),
            daemon=True,
        ).start()

    def _analyze_worker(
        self, targets: list[Path], active_model_path: Path
    ) -> None:
        try:
            if self.model is None or self.loaded_model_path != active_model_path:
                self.after(0, self.status.set, f"모델 로딩 중: {active_model_path.name}")
                self.model = YOLO(str(active_model_path))
                self.loaded_model_path = active_model_path

            print(f"[analysis start] model={active_model_path.name}, images={len(targets)}")
            results = self.model(
                [str(path) for path in targets],
                verbose=False,
                conf=0.05,
            )
            for index, (image_path, result) in enumerate(
                zip(targets, results, strict=True),
                start=1,
            ):
                result.save(
                    filename=str(self._result_path(image_path, active_model_path))
                )
                print(
                    f"[{index}/{len(targets)}] {image_path.name}: "
                    f"{result.verbose().strip()}"
                )
                self.after(0, self._analysis_progress, index, len(targets), image_path)

            print(f"[analysis complete] images={len(targets)}")
            self.after(0, self._analysis_finished, len(targets))
        except Exception as error:
            traceback.print_exc()
            self.after(0, self._analysis_failed, str(error))

    def _analysis_progress(
        self, current: int, total: int, image_path: Path
    ) -> None:
        percentage = round(current / total * 100)
        self.progress.configure(value=current)
        self.selected_progress.configure(value=percentage)
        self.selected_progress_text.set(f"{percentage}% · 결과 저장 완료")
        self.status.set(f"[{current}/{total}] 완료: {image_path.name}")
        self.refresh_images()

    def _analysis_finished(self, count: int) -> None:
        self.processing = False
        self._set_buttons_enabled(True)
        self.refresh_images()
        self.progress.configure(value=count)
        self.selected_progress.configure(value=100)
        self.selected_progress_text.set("100% · 분석 완료")
        self.status.set(f"분석 완료: {count}개")

    def _analysis_failed(self, error: str) -> None:
        self.processing = False
        self._set_buttons_enabled(True)
        self.selected_progress.configure(value=0)
        self.selected_progress_text.set("오류 발생")
        self.status.set("분석 중 오류가 발생했습니다.")
        messagebox.showerror("분석 오류", error)

    def _set_buttons_enabled(self, enabled: bool) -> None:
        state = tk.NORMAL if enabled else tk.DISABLED
        self.selected_button.configure(state=state)
        self.all_button.configure(state=state)
        self.compare_reanalyze_button.configure(state=state)
        self.model_combo.configure(state="readonly" if enabled else "disabled")


def main() -> None:
    app = YoloViewer()
    app.mainloop()


if __name__ == "__main__":
    main()
