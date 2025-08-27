## src/pages/ajd_recommend_page.py
from playwright.async_api import Page
from ..base.base_page import BasePage


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

    async def verify_url(self) -> bool:
        """현재 페이지가 올바른 URL인지 확인"""
        return self.page.url.startswith(self.url)

    async def click_cta(self) -> bool:
        """
        메인 CTA 버튼('추천받기') 클릭 후 다음 화면 진입 확인
        """
        cta = self.page.get_by_role("button", name="추천받기")
        await cta.click()
        # CTA 클릭 후 결과 페이지나 섹션 확인
        result = self.page.get_by_text("추천 결과", exact=False)
        return await result.is_visible()

    async def answer_question(self, q_text: str, answer: str) -> bool:
        """
        특정 질문 텍스트를 찾아 답변 선택
        q_text: 질문 텍스트 일부
        answer: 버튼/옵션 텍스트
        """
        q = self.page.get_by_text(q_text, exact=False)
        if not await q.is_visible():
            return False
        option = self.page.get_by_role("button", name=answer)
        await option.click()
        return True

    async def verify_footer_links(self) -> bool:
        """
        푸터의 주요 정책 링크 확인
        """
        privacy = self.page.get_by_text("개인정보처리방침", exact=False)
        terms = self.page.get_by_text("이용약관", exact=False)
        return (await privacy.is_visible()) and (await terms.is_visible())
