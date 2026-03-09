"""HTML取得モジュール"""

import requests


class HtmlFetcher:
    DEFAULT_TIMEOUT = 30
    _HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HtmlDiffTool/1.0)"}

    @staticmethod
    def fetch(url: str, auth, timeout: int = 30) -> str:
        """指定URLのHTMLテキストを取得して返す。エラー時は例外を送出。"""
        resp = requests.get(
            url,
            auth=auth,
            headers=HtmlFetcher._HEADERS,
            timeout=timeout,
            verify=True,
        )
        resp.raise_for_status()
        # HTTP ヘッダに charset がない場合 requests は ISO-8859-1 をデフォルトに使う。
        # その場合は charset_normalizer/chardet による検出結果で上書きして日本語化けを防ぐ。
        if resp.encoding and resp.encoding.upper() in ("ISO-8859-1", "LATIN-1"):
            resp.encoding = resp.apparent_encoding
        return resp.text
