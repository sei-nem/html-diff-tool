"""アクションバー（実行ボタン・プログレスバー・ステータスラベル）"""

import tkinter as tk
from tkinter import ttk
from typing import Callable


class ActionBar(ttk.Frame):
    """比較実行ボタン・クリアボタン・進捗表示をまとめたバーウィジェット。"""

    def __init__(
        self,
        parent,
        on_compare: Callable[[], None],
        on_clear: Callable[[], None],
        **kwargs,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._on_compare = on_compare
        self._on_clear   = on_clear
        self._compare_btn: ttk.Button
        self._progress: ttk.Progressbar
        self._status_var = tk.StringVar(value="待機中")
        self._build()

    def _build(self) -> None:
        self._compare_btn = ttk.Button(
            self, text="▶  比較実行", command=self._on_compare, width=14
        )
        self._compare_btn.pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(self, text="クリア", command=self._on_clear, width=10).pack(
            side=tk.LEFT, padx=(0, 10)
        )

        self._progress = ttk.Progressbar(self, mode="indeterminate", length=160)
        self._progress.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(self, textvariable=self._status_var, foreground="gray").pack(
            side=tk.LEFT
        )

    def set_running(self, running: bool) -> None:
        """実行中/待機中の状態に応じてボタンとプログレスを切り替える。"""
        if running:
            self._compare_btn.config(state="disabled")
            self._progress.start(10)
        else:
            self._progress.stop()
            self._compare_btn.config(state="normal")

    def set_status(self, text: str) -> None:
        self._status_var.set(text)
