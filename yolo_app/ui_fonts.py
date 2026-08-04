"""Tkinter에서 한글을 안정적으로 표시하기 위한 글꼴 설정."""
from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from collections.abc import Iterable


KOREAN_FONT_CANDIDATES = (
    "Noto Sans CJK KR",
    "NanumGothic",
    "NanumBarunGothic",
)
KOREAN_MONO_FONT_CANDIDATES = (
    "Noto Sans Mono CJK KR",
    "NanumGothicCoding",
)
TK_UI_NAMED_FONTS = (
    "TkDefaultFont",
    "TkTextFont",
    "TkMenuFont",
    "TkHeadingFont",
    "TkCaptionFont",
    "TkSmallCaptionFont",
    "TkIconFont",
    "TkTooltipFont",
)


def choose_font_family(
    available_families: Iterable[str],
    candidates: Iterable[str],
    fallback: str,
) -> str:
    """설치된 글꼴 중 우선순위가 가장 높은 family 이름을 반환한다."""
    installed = {family.casefold(): family for family in available_families}
    for candidate in candidates:
        if candidate.casefold() in installed:
            return installed[candidate.casefold()]
    return fallback


def configure_korean_fonts(root: tk.Misc) -> tuple[str, str]:
    """현재 Tk interpreter의 기본 UI/고정폭 글꼴을 한글 글꼴로 설정한다."""
    available = tkfont.families(root)
    ui_family = choose_font_family(
        available,
        KOREAN_FONT_CANDIDATES,
        fallback="DejaVu Sans",
    )
    mono_family = choose_font_family(
        available,
        KOREAN_MONO_FONT_CANDIDATES,
        fallback=ui_family,
    )

    for name in TK_UI_NAMED_FONTS:
        try:
            tkfont.nametofont(name, root=root).configure(family=ui_family)
        except tk.TclError:
            # Tk 버전에 따라 일부 named font가 없을 수 있다.
            continue

    try:
        tkfont.nametofont("TkFixedFont", root=root).configure(family=mono_family)
    except tk.TclError:
        pass

    # tk.Listbox처럼 ttk가 아닌 위젯도 별도 지정 없이 named font를 사용한다.
    root.option_add("*Font", "TkDefaultFont")
    return ui_family, mono_family
