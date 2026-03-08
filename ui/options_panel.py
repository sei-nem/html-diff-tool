"""オプションパネル（比較モード・Basic認証）"""

import tkinter as tk
from tkinter import ttk


class OptionsPanel(ttk.Frame):
    """比較モード・Basic認証をまとめたオプション行ウィジェット。"""

    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self.compare_mode  = tk.StringVar(value="order")
        self._username_var = tk.StringVar()
        self._password_var = tk.StringVar()
        self._build()

    def _build(self) -> None:
        # 比較モード
        mode_frame = ttk.LabelFrame(self, text="比較モード", padding=5)
        mode_frame.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Radiobutton(
            mode_frame, text="入力順で比較",
            variable=self.compare_mode, value="order",
        ).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(
            mode_frame, text="URLパス一致で比較",
            variable=self.compare_mode, value="path",
        ).pack(side=tk.LEFT, padx=5)

        # Basic 認証
        auth_frame = ttk.LabelFrame(self, text="Basic認証", padding=5)
        auth_frame.pack(side=tk.LEFT, padx=5, fill=tk.Y)
        ttk.Label(auth_frame, text="ユーザー名:").pack(side=tk.LEFT)
        ttk.Entry(auth_frame, textvariable=self._username_var, width=14).pack(
            side=tk.LEFT, padx=(2, 8)
        )
        ttk.Label(auth_frame, text="パスワード:").pack(side=tk.LEFT)
        ttk.Entry(
            auth_frame, textvariable=self._password_var, width=14, show="*"
        ).pack(side=tk.LEFT, padx=(2, 0))

    @property
    def auth(self) -> tuple[str, str] | None:
        """ユーザー名が入力されていれば (user, pass) を、なければ None を返す。"""
        username = self._username_var.get().strip()
        return (username, self._password_var.get().strip()) if username else None
