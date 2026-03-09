"""URLペアリングユーティリティ"""

from urllib.parse import urlparse


class UrlPairer:

    @staticmethod
    def url_path(url: str) -> str:
        """ドメイン以下のパス＋クエリ文字列を返す。"""
        p = urlparse(url)
        return p.path + ("?" + p.query if p.query else "")

    @staticmethod
    def build_pairs(
        left_urls: list[str],
        right_urls: list[str],
        mode: str,
        on_unmatched=None,
    ) -> list[tuple[str, str]]:
        """比較モードに応じて (左URL, 右URL) のペアリストを構築する。

        Args:
            mode: "order"（入力順）または "path"（URLパス一致）
            on_unmatched: マッチしないURLのリストを受け取るコールバック
        """
        if mode == "order":
            return list(zip(left_urls, right_urls))

        # パス一致モード
        left_map: dict[str, str] = {}
        for u in left_urls:
            left_map.setdefault(UrlPairer.url_path(u), u)

        pairs: list[tuple[str, str]] = []
        used: set[str] = set()
        unmatched_right: list[str] = []

        for u in right_urls:
            p = UrlPairer.url_path(u)
            if p in left_map and p not in used:
                pairs.append((left_map[p], u))
                used.add(p)
            else:
                unmatched_right.append(u)

        unmatched_left = [v for k, v in left_map.items() if k not in used]
        all_unmatched  = unmatched_left + unmatched_right

        if all_unmatched and on_unmatched:
            on_unmatched(all_unmatched)

        return pairs
