## src/base/base_page.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import time

from playwright.async_api import Page, Locator


@dataclass
class PageCheckResult:
    ok: bool
    url: str
    status: int
    load_ms: int
    detail: str = ""


class BasePage:
    def __init__(self, page: Page, url: str) -> None:
        self.page = page
        self.url = url

    async def _goto_and_measure(self, timeout_ms: int) -> tuple[int, int]:
        """URL 이동 + 로드 시간/HTTP 상태코드 측정"""
        t0 = time.perf_counter()
        resp = await self.page.goto(
            self.url, timeout=timeout_ms, wait_until="domcontentloaded"
        )
        load_ms = int((time.perf_counter() - t0) * 1000)
        status = resp.status if resp else -1
        return load_ms, status

    async def _try_visible(self, locator: Locator) -> bool:
        """보이면 True, 예외면 False (안정성 우선)"""
        try:
            return await locator.is_visible()
        except Exception:
            return False
