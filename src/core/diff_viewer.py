"""差分ブラウザ表示モジュール"""

import difflib
import os
import tempfile
import webbrowser
from pathlib import Path


_DIFF_STYLE = """\
<style>
body  { font-family:'Consolas','Courier New',monospace; font-size:12px; margin:1em; }
table.diff { border-collapse:collapse; width:100%; }
td,th { border:1px solid #ddd; padding:2px 4px; vertical-align:top; }
.diff_header { background:#f0f0f0; text-align:right; }
.diff_next   { background:#c0c0c0; }
.diff_add    { background:#aaffaa; }
.diff_chg    { background:#ffff77; }
.diff_sub    { background:#ffaaaa; }
</style>"""


class DiffViewer:
    """比較結果をHTMLファイルに書き出してブラウザで表示するクラス。"""

    def __init__(self) -> None:
        self._temp_files: list[str] = []

    def open_in_browser(self, result: dict) -> None:
        """result dict から差分HTMLを生成してデフォルトブラウザで開く。"""
        left_lines  = result.get("left_lines")  or (result["left_html"]  or "").splitlines()
        right_lines = result.get("right_lines") or (result["right_html"] or "").splitlines()

        differ = difflib.HtmlDiff(wrapcolumn=120)
        html = differ.make_file(
            left_lines,
            right_lines,
            fromdesc=result["left_url"],
            todesc=result["right_url"],
            context=True,
            numlines=5,
        )
        html = html.replace("charset=ISO-8859-1", "charset=UTF-8")
        html = html.replace("</head>", _DIFF_STYLE + "\n</head>")

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".html", delete=False,
            encoding="utf-8", prefix="diff_",
        ) as f:
            f.write(html)
            path = f.name

        self._temp_files.append(path)
        webbrowser.open(Path(path).as_uri())

    def cleanup(self) -> None:
        """終了時に生成した一時HTMLファイルを削除する。"""
        for path in self._temp_files:
            try:
                os.remove(path)
            except OSError:
                pass
        self._temp_files.clear()
