## src/pages/base_page.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from playwright.async_api import Page, Response
import time


@dataclass
class CheckResult:
    """페이지 체크 결과를 담는 데이터 구조"""

    url: str  # 요청한 URL
    ok: bool  # 정상 여부
    status: Optional[int]  # HTTP 상태 코드
    load_ms: int  # 로드 시간(ms)
    detail: str  # 실패 원인/부가 설명


class BasePage:
    """모든 Page Object가 상속받는 기본 클래스"""

    def __init__(self, page: Page, url: str) -> None:
        self.page = page
        self.url = url

    async def goto(self, timeout_ms: int) -> Response | None:
        """
        지정된 URL로 이동.
        - timeout_ms: 페이지 로드 제한 시간
        - return: Response 객체 (없을 수도 있음)
        """
        return await self.page.goto(
            self.url, timeout=timeout_ms, wait_until="domcontentloaded"
        )

    async def is_ready(self) -> bool:
        """
        각 페이지별 '핵심 요소가 정상적으로 로드됐는지' 판정하는 메서드.
        서브클래스에서 반드시 override 해야 함.
        """
        raise NotImplementedError

    async def check(self, timeout_ms: int, slow_ms: int) -> CheckResult:
        """
        페이지를 열고 정상 여부를 판정
        1) HTTP 상태 코드
        2) is_ready() 결과
        3) 로드 속도(slow_ms 기준)
        """
        start = time.perf_counter()
        status = None
        ok = True
        detail = "OK"

        try:
            resp = await self.goto(timeout_ms=timeout_ms)
            if resp is not None:
                status = resp.status
                if status != 200:
                    ok = False
                    detail = f"HTTP status {status}"
            else:
                ok = False
                detail = "No Response Object"

            # 핵심 요소 로드 여부 확인
            if not await self.is_ready():
                ok = False
                detail = f"Core content not ready for {self.url}"

        except Exception as e:
            ok = False
            detail = f"Exception during navigation: {e!r}"

        load_ms = int((time.perf_counter() - start) * 1000)

        # 성능 임계치 초과 체크
        if ok and load_ms > slow_ms:
            ok = False
            detail = f"Slow load: {load_ms}ms > threshold {slow_ms}ms"

        return CheckResult(self.url, ok, status, load_ms, detail)
