"""比較結果ツリービュー"""

import tkinter as tk
from tkinter import ttk
from typing import Callable


class ResultsTree(ttk.LabelFrame):
    """URL比較結果を一覧表示するツリービューウィジェット。"""

    def __init__(
        self,
        parent,
        on_double_click: Callable[[int | None], None],
        **kwargs,
    ) -> None:
        super().__init__(parent, text="比較結果", padding=5, **kwargs)
        self._on_double_click = on_double_click
        self._tree: ttk.Treeview
        self._build()

    def _build(self) -> None:
        cols = ("no", "left_url", "right_url", "status", "diff_count")
        self._tree = ttk.Treeview(self, columns=cols, show="headings", height=8)

        self._tree.heading("no",         text="No.")
        self._tree.heading("left_url",   text="比較元URL")
        self._tree.heading("right_url",  text="比較先URL")
        self._tree.heading("status",     text="取得状態")
        self._tree.heading("diff_count", text="差分行数")

        self._tree.column("no",         width=45,  anchor="center")
        self._tree.column("left_url",   width=360)
        self._tree.column("right_url",  width=360)
        self._tree.column("status",     width=110, anchor="center")
        self._tree.column("diff_count", width=80,  anchor="center")

        self._tree.tag_configure("diff",  background="#fff3cd")
        self._tree.tag_configure("same",  background="#d4edda")
        self._tree.tag_configure("error", background="#f8d7da")

        sb_y = ttk.Scrollbar(self, orient=tk.VERTICAL,   command=self._tree.yview)
        sb_x = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self._tree.xview)
        self._tree.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
        sb_y.pack(side=tk.RIGHT,  fill=tk.Y)
        sb_x.pack(side=tk.BOTTOM, fill=tk.X)
        self._tree.pack(fill=tk.BOTH, expand=True)

        self._tree.bind(
            "<Double-1>",
            lambda _e: self._on_double_click(self.get_selected_index()),
        )

    def add_result(self, i: int, result: dict) -> None:
        """1-based の番号 i と result dict を受け取って行を追加する。"""
        if result.get("error"):
            status, tag, diff_str = "エラー",   "error", "—"
        elif result.get("diff_count", 0) == 0:
            status, tag, diff_str = "差分なし", "same",  "0"
        else:
            status, tag, diff_str = "差分あり", "diff",  str(result["diff_count"])

        self._tree.insert(
            "", tk.END, iid=str(i - 1),
            values=(i, result["left_url"], result["right_url"], status, diff_str),
            tags=(tag,),
        )

    def clear(self) -> None:
        for item in self._tree.get_children():
            self._tree.delete(item)

    def get_selected_index(self) -> int | None:
        """選択中の行の 0-based インデックスを返す。未選択時は None。"""
        sel = self._tree.selection()
        return int(sel[0]) if sel else None
