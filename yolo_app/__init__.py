import pathlib
import sys

# Python 3.13에서 학습된 checkpoint(best.pt 등)를 Python 3.12 이하 환경에서 unpickle할 때
# pathlib._local 모듈 참조 에러가 발생하는 것을 방지하기 위한 호환성 패치
if not hasattr(pathlib, "_local"):
    sys.modules["pathlib._local"] = pathlib
