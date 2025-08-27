## src/pages/ajd_main_page.py
from playwright.async_api import Page
from src.base.base_page import BasePage, PageCheckResult


class AjdMainPage(BasePage):
    """
    AJD 메인 페이지
    URL: https://www.ajd.co.kr/
    메인 배너 카피 또는 푸터 정책 링크가 보이면 정상 판정
    """

    def __init__(self, page: Page) -> None:
        super().__init__(page, "https://www.ajd.co.kr/")

    async def is_ready(self) -> bool:
        # 1) 메인 히어로 배너 (alt에 '생활지원금' 포함)
        hero_img = self.page.locator("img[alt*='생활지원금']")
        if await self._try_visible(hero_img):
            return True

        # 2) 메인 카피 텍스트
        copy1 = self.page.get_by_text("생활지원금 지킴이", exact=False)
        if await self._try_visible(copy1):
            return True

        # 3) 폴백: 푸터 정책 링크
        policy = self.page.get_by_text("개인정보처리방침", exact=False)
        return await self._try_visible(policy)

    async def check(self, timeout_ms: int, slow_ms: int) -> PageCheckResult:
        load_ms, status = await self._goto_and_measure(timeout_ms)

        if not await self.is_ready():
            return PageCheckResult(
                ok=False,
                url=self.page.url,
                status=status,
                load_ms=load_ms,
                detail="Main not ready (hero/copy/policy not visible)",
            )

        if slow_ms and load_ms > slow_ms:
            return PageCheckResult(
                ok=False,
                url=self.page.url,
                status=status,
                load_ms=load_ms,
                detail=f"Slow main page: {load_ms}ms > {slow_ms}ms",
            )

        return PageCheckResult(
            ok=True, url=self.page.url, status=status, load_ms=load_ms
        )
