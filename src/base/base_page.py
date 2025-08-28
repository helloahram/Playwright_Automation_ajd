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
    def __init__(
        self, page: Page, url: str, ready_locators: list[Locator] | None = None
    ) -> None:
        self.page = page
        self.url = url
        self.ready_locators = ready_locators or []

    async def _goto_and_measure(self, timeout_ms: int) -> tuple[int, int]:
        """URL 이동 + 로드 시간/ HTTP 상태코드 측정"""
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

    async def is_ready(self) -> bool:
        """
        페이지 준비 여부를 확인
        - ready_locators 리스트에 정의된 locator 들을 순차적으로 확인
        - 하나라도 화면에 보이면 True 반환
        - 아무 것도 보이지 않으면 False 반환
        """
        for loc in self.ready_locators:
            if await self._try_visible(loc):  # 보이는 locator 발견 시 True
                return True
        return False  # 모든 locator가 보이지 않으면 False

    async def check(self, timeout_ms: int, slow_ms: int) -> PageCheckResult:
        """
        페이지 로딩 및 준비 상태를 종합적으로 확인

        절차:
        1. 지정된 URL로 이동하면서 로딩 시간 (ms) 과 HTTP 상태코드를 측정
        2. is_ready()로 페이지 준비 여부 판단
           → 준비되지 않았으면 ok=False 결과 반환
        3. 로딩 시간이 slow_ms 기준을 초과하면 ok=False 결과 반환
        4. 모든 조건이 통과되면 ok=True 결과 반환

        Args:
            timeout_ms: 페이지 이동 시 허용할 최대 대기 시간 (ms)
            slow_ms: 성능 체크 기준 (ms). 지정하지 않으면 검사 안 함

        Returns:
            PageCheckResult: (ok 여부, url, 상태코드, 로드 시간, 상세 메시지)
        """
        load_ms, status = await self._goto_and_measure(timeout_ms)

        # 1) 페이지 준비 실패
        if not await self.is_ready():
            return PageCheckResult(
                ok=False,
                url=self.page.url,
                status=status,
                load_ms=load_ms,
                detail=f"{self.__class__.__name__} not ready (locators not visible)",
            )

        # 2) 페이지가 너무 느린 경우
        if slow_ms and load_ms > slow_ms:
            return PageCheckResult(
                ok=False,
                url=self.page.url,
                status=status,
                load_ms=load_ms,
                detail=f"Slow {self.__class__.__name__}: {load_ms}ms > {slow_ms}ms",
            )

        # 3) 정상 로딩
        return PageCheckResult(
            ok=True, url=self.page.url, status=status, load_ms=load_ms
        )
