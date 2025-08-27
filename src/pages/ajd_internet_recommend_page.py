## src/pages/ajd_internet_recommend_page.py
from playwright.async_api import Page
from src.base.base_page import BasePage, PageCheckResult


class AjdInternetRecommend(BasePage):
    """
    AJD 인터넷 추천 페이지
    URL: https://www.ajd.co.kr/internet/recommend
    핵심 질문 카피 또는 푸터 정책 링크가 보이면 정상 판정
    """

    def __init__(self, page: Page) -> None:
        super().__init__(page, "https://www.ajd.co.kr/internet/recommend")

    async def is_ready(self) -> bool:
        # 1) 첫 질문 타이틀
        q1 = self.page.get_by_text("가입하려는 통신사가 있으신가요?", exact=False)
        if await self._try_visible(q1):
            return True

        # 2) 상단 진행 카피
        progress = self.page.get_by_text("3개의 질문에만 답하면 돼요", exact=False)
        if await self._try_visible(progress):
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
                detail="Recommend not ready (copy/policy not visible)",
            )

        if slow_ms and load_ms > slow_ms:
            return PageCheckResult(
                ok=False,
                url=self.page.url,
                status=status,
                load_ms=load_ms,
                detail=f"Slow recommend page: {load_ms}ms > {slow_ms}ms",
            )

        return PageCheckResult(
            ok=True, url=self.page.url, status=status, load_ms=load_ms
        )
