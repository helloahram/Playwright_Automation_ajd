## src/pages/ajd_recommend_page.py
from playwright.async_api import Page
from .base_page import BasePage


class AjdInternetRecommend(BasePage):
    """
    AJD 인터넷 추천 페이지
    핵심 카피/ CTA가 보이면 '서비스가 떴다'로 판정
    URL: https://www.ajd.co.kr/internet/recommend
    """

    def __init__(self, page: Page) -> None:
        super().__init__(page, "https://www.ajd.co.kr/internet/recommend")

    async def is_ready(self) -> bool:
        """
        안정적인 텍스트 2가지를 우선 시도,
        그래도 안 보이면 푸터 정책 링크로 보강
        """
        t1 = self.page.get_by_text("가입하려는 통신사가 있으신가요?", exact=False)
        t2 = self.page.get_by_text("3개의 질문에만 답하면 돼요", exact=False)
        try:
            if await t1.is_visible():
                return True
            if await t2.is_visible():
                return True
            # 폴백: 공용 푸터의 정책 링크
            footer = self.page.get_by_text("개인정보처리방침", exact=False)
            return await footer.is_visible()
        except:
            return False
