"""URL HTML差分比較ツール - エントリポイント

複数URLのHTMLを一括取得して差分を比較するGUIツール。
PyInstallerで単一EXEにビルド可能。

構成:
    diff_tool.py       このファイル（エントリポイントのみ）
    app.py             HtmlDiffApp（UI統合・比較オーケストレーション）
    core/
        fetcher.py     HtmlFetcher（HTTPリクエスト）
        comparator.py  HtmlComparator（差分計算・lxml正規化）
        url_pairer.py  UrlPairer（URLペアリング）
        diff_viewer.py DiffViewer（ブラウザ差分表示）
    ui/
        url_input_panel.py  UrlInputPanel
        options_panel.py    OptionsPanel
        action_bar.py       ActionBar
        results_tree.py     ResultsTree
"""

import tkinter as tk

from app import HtmlDiffApp


# --------------------------------------------------------------------------- #
# エントリポイント（削除されたクラス群はそれぞれのモジュールへ移動済み）


def main() -> None:
    root = tk.Tk()
    HtmlDiffApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
