"""URL入力パネル（左右2ペインのテキストウィジェット）"""

import tkinter as tk
from tkinter import ttk
from urllib.parse import urlparse


class UrlInputPanel(ttk.LabelFrame):
    """左右それぞれにURL一覧を改行区切りで入力するパネル。"""

    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, text="URL入力（1行に1つのURL）", padding=5, **kwargs)
        self._left_text: tk.Text
        self._right_text: tk.Text
        self._build()

    def _build(self) -> None:
        for side, attr, label in (
            ("left",  "_left_text",  "比較元URL"),
            ("right", "_right_text", "比較先URL"),
        ):
            lf = ttk.LabelFrame(self, text=label, padding=5)
            lf.pack(
                side=tk.LEFT, fill=tk.BOTH, expand=True,
                padx=(0, 3) if side == "left" else (3, 0),
            )
            text = tk.Text(lf, wrap=tk.NONE, font=("Consolas", 9), undo=True, height=10)
            sb_y = ttk.Scrollbar(lf, orient=tk.VERTICAL,   command=text.yview)
            sb_x = ttk.Scrollbar(lf, orient=tk.HORIZONTAL, command=text.xview)
            text.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
            sb_y.pack(side=tk.RIGHT,  fill=tk.Y)
            sb_x.pack(side=tk.BOTTOM, fill=tk.X)
            text.pack(fill=tk.BOTH, expand=True)
            setattr(self, attr, text)

    @staticmethod
    def _is_url(line: str) -> bool:
        parsed = urlparse(line)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)

    def get_left_urls(self) -> list[str]:
        return [u.strip() for u in self._left_text.get("1.0", tk.END).splitlines() if self._is_url(u.strip())]

    def get_right_urls(self) -> list[str]:
        return [u.strip() for u in self._right_text.get("1.0", tk.END).splitlines() if self._is_url(u.strip())]
