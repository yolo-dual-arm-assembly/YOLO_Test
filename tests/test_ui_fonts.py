from yolo_app.ui_fonts import choose_font_family


def test_choose_font_family_uses_candidate_priority() -> None:
    available = ("NanumGothic", "Noto Sans CJK KR", "DejaVu Sans")

    chosen = choose_font_family(
        available,
        ("Noto Sans CJK KR", "NanumGothic"),
        fallback="DejaVu Sans",
    )

    assert chosen == "Noto Sans CJK KR"


def test_choose_font_family_is_case_insensitive() -> None:
    chosen = choose_font_family(
        ("NanumGothicCoding",),
        ("nanumgothiccoding",),
        fallback="monospace",
    )

    assert chosen == "NanumGothicCoding"


def test_choose_font_family_uses_fallback() -> None:
    chosen = choose_font_family(
        ("DejaVu Sans",),
        ("Noto Sans CJK KR",),
        fallback="DejaVu Sans",
    )

    assert chosen == "DejaVu Sans"
