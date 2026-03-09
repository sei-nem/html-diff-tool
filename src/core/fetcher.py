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
        return resp.text
