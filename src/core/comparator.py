"""HTML比較・差分計算モジュール

常にlxmlでHTMLを構造的に正規化してから差分を取る。
空白・改行はテキストノードのトリムと折り畳みで除去し、
タグ構造・属性・テキスト内容の変化のみを検出する。
"""

import difflib
import re


class HtmlComparator:

    @staticmethod
    def _clean_whitespace(node) -> None:
        """ツリーを再帰的に走査してテキストノードの空白を正規化する。

        - 要素間の空白専用テキストノード（tail/text が空白のみ）は空文字に置換
        - それ以外のテキストはstrip＋連続空白を1スペースに折り畳む
        """
        if node.text:
            stripped = re.sub(r"\s+", " ", node.text).strip()
            node.text = stripped if stripped else None
        for child in node:
            HtmlComparator._clean_whitespace(child)
            if child.tail:
                stripped = re.sub(r"\s+", " ", child.tail).strip()
                child.tail = stripped if stripped else None

    @classmethod
    def normalize_html(cls, html_text: str) -> list[str]:
        """lxmlでHTMLをパース・空白正規化・pretty_printし、行リストを返す。"""
        import lxml.html as lxhtml
        from lxml import etree

        doc = lxhtml.fromstring(html_text)
        cls._clean_whitespace(doc)
        normalized = etree.tostring(
            doc, pretty_print=True, encoding="unicode", method="html"
        )
        return normalized.splitlines()

    @staticmethod
    def compute_diff_count(left_lines: list[str], right_lines: list[str]) -> int:
        """unified diff で追加/削除行数の合計を返す。"""
        diffs = list(difflib.unified_diff(left_lines, right_lines, lineterm=""))
        return sum(
            1
            for line in diffs
            if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
        )

    @classmethod
    def prepare_lines(
        cls,
        left_html: str,
        right_html: str,
    ) -> tuple[list[str], list[str], str | None]:
        """lxmlで正規化した比較用の行リストを生成する。

        Returns:
            (left_lines, right_lines, error_message_or_None)
            lxml パース失敗時は生テキスト差分にフォールバックしてエラーメッセージを返す。
        """
        try:
            left_lines  = cls.normalize_html(left_html)
            right_lines = cls.normalize_html(right_html)
            return left_lines, right_lines, None
        except Exception as exc:  # noqa: BLE001
            return (
                left_html.splitlines(),
                right_html.splitlines(),
                f"lxml正規化失敗（テキスト差分で代替）: {exc}",
            )
