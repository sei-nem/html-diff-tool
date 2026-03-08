"""アプリケーション統合クラス"""

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import tkinter as tk
from tkinter import ttk, messagebox

from core.comparator import HtmlComparator
from core.diff_viewer import DiffViewer
from core.fetcher import HtmlFetcher
from core.url_pairer import UrlPairer
from ui.action_bar import ActionBar
from ui.options_panel import OptionsPanel
from ui.results_tree import ResultsTree
from ui.url_input_panel import UrlInputPanel


class HtmlDiffApp:
    """UIコンポーネントと処理ロジックを統合するメインアプリケーションクラス。"""

    MAX_WORKERS = 5

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("URL HTML差分比較ツール")
        self.root.geometry("1060x760")
        self.root.minsize(820, 620)

        self.results: list[dict] = []
        self._viewer = DiffViewer()

        self._setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ----------------------------------------------------------------------- #
    # UI 構築
    # ----------------------------------------------------------------------- #
    def _setup_ui(self) -> None:
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        self._url_panel = UrlInputPanel(main)
        self._url_panel.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        self._options = OptionsPanel(main)
        self._options.pack(fill=tk.X, pady=5)

        self._action_bar = ActionBar(
            main, on_compare=self._start_compare, on_clear=self._clear_results
        )
        self._action_bar.pack(fill=tk.X, pady=5)

        self._results_tree = ResultsTree(main, on_double_click=self._on_result_selected)
        self._results_tree.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            main,
            text="※ 行をダブルクリックすると差分をブラウザで表示します",
            foreground="gray",
            font=("", 8),
        ).pack(anchor="w", pady=(2, 0))

    # ----------------------------------------------------------------------- #
    # 比較実行
    # ----------------------------------------------------------------------- #
    def _start_compare(self) -> None:
        left_urls  = self._url_panel.get_left_urls()
        right_urls = self._url_panel.get_right_urls()

        if not left_urls or not right_urls:
            messagebox.showwarning("入力エラー", "左右両方にURLを入力してください。")
            return

        auth = self._options.auth

        def on_unmatched(urls: list[str]) -> None:
            self.root.after(
                0,
                lambda: messagebox.showwarning(
                    "マッチしないURL",
                    "以下のURLはペアが見つかりませんでした:\n\n" + "\n".join(urls),
                ),
            )

        pairs = UrlPairer.build_pairs(
            left_urls, right_urls,
            self._options.compare_mode.get(),
            on_unmatched=on_unmatched,
        )
        if not pairs:
            messagebox.showwarning("ペアなし", "比較できるURLペアが見つかりませんでした。")
            return

        self._clear_results()
        self._action_bar.set_running(True)
        self._action_bar.set_status(f"0 / {len(pairs)} 処理中...")

        threading.Thread(
            target=self._do_compare, args=(pairs, auth), daemon=True
        ).start()

    def _do_compare(
        self, pairs: list[tuple[str, str]], auth
    ) -> None:
        total   = len(pairs)
        results: list[dict] = [{}] * total
        done    = 0

        def fetch_pair(idx: int, left_url: str, right_url: str) -> tuple[int, dict]:
            left_html = right_html = None
            error: str | None = None

            for label, url in (("左側", left_url), ("右側", right_url)):
                try:
                    html = HtmlFetcher.fetch(url, auth, HtmlFetcher.DEFAULT_TIMEOUT)
                    if label == "左側":
                        left_html = html
                    else:
                        right_html = html
                except requests.exceptions.SSLError as exc:
                    error = f"{label} SSL証明書エラー: {exc}"; break
                except requests.exceptions.ConnectionError as exc:
                    error = f"{label} 接続エラー: {exc}"; break
                except requests.exceptions.Timeout:
                    error = f"{label} タイムアウト: {url}"; break
                except requests.exceptions.HTTPError as exc:
                    error = f"{label} HTTPエラー {exc.response.status_code}: {url}"; break
                except Exception as exc:  # noqa: BLE001
                    error = f"{label} エラー: {exc}"; break

            left_lines = right_lines = None
            diff_count = 0

            if error is None and left_html is not None and right_html is not None:
                left_lines, right_lines, norm_error = HtmlComparator.prepare_lines(
                    left_html, right_html
                )
                if norm_error:
                    error = norm_error
                diff_count = HtmlComparator.compute_diff_count(left_lines, right_lines)

            return idx, {
                "left_url":    left_url,
                "right_url":   right_url,
                "left_html":   left_html,
                "right_html":  right_html,
                "left_lines":  left_lines,
                "right_lines": right_lines,
                "diff_count":  diff_count,
                "error":       error,
            }

        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            futures = {
                executor.submit(fetch_pair, i, l, r): i
                for i, (l, r) in enumerate(pairs)
            }
            for future in as_completed(futures):
                try:
                    idx, result = future.result()
                    results[idx] = result
                except Exception as exc:  # noqa: BLE001
                    idx = futures[future]
                    l, r = pairs[idx]
                    results[idx] = {
                        "left_url":    l,    "right_url":   r,
                        "left_html":   None, "right_html":  None,
                        "left_lines":  None, "right_lines": None,
                        "diff_count":  0,    "error":       str(exc),
                    }
                done += 1
                self.root.after(
                    0,
                    lambda c=done, t=total: self._action_bar.set_status(
                        f"{c} / {t} 処理中..."
                    ),
                )

        self.root.after(0, lambda: self._update_results(results))

    def _update_results(self, results: list[dict]) -> None:
        self.results = results
        for i, result in enumerate(results, 1):
            self._results_tree.add_result(i, result)

        total      = len(results)
        diff_total = sum(1 for r in results if r.get("diff_count", 0) > 0)
        err_total  = sum(1 for r in results if r.get("error"))

        self._action_bar.set_running(False)
        self._action_bar.set_status(
            f"完了: {total}件 ／ 差分あり: {diff_total}件 ／ エラー: {err_total}件"
        )

    # ----------------------------------------------------------------------- #
    # 差分ビュー表示
    # ----------------------------------------------------------------------- #
    def _on_result_selected(self, idx: int | None) -> None:
        if idx is None or idx >= len(self.results):
            return
        result = self.results[idx]
        if result.get("error"):
            messagebox.showerror("取得エラー", result["error"])
            return
        self._viewer.open_in_browser(result)

    # ----------------------------------------------------------------------- #
    # その他
    # ----------------------------------------------------------------------- #
    def _clear_results(self) -> None:
        self._results_tree.clear()
        self.results = []
        self._action_bar.set_status("待機中")

    def _on_close(self) -> None:
        self._viewer.cleanup()
        self.root.destroy()
