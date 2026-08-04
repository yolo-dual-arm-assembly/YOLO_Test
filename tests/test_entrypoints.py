import main as main_entrypoint
import yolo_demo
from yolo_app import __main__ as package_entrypoint
from yolo_app.viewer import main as viewer_main


def test_all_gui_entrypoints_use_viewer_main() -> None:
    assert main_entrypoint.main is viewer_main
    assert package_entrypoint.main is viewer_main
    assert yolo_demo.main is viewer_main
