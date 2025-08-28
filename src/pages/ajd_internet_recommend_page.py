## src/pages/ajd_internet_recommend_page.py
from playwright.async_api import Page
from src.base.base_page import BasePage, PageCheckResult


class AjdInternetRecommend(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(
            page,
            "https://www.ajd.co.kr/internet/recommend",
            ready_locators=[
                page.get_by_text("가입하려는 통신사가 있으신가요?", exact=False),
                page.get_by_text("3개의 질문에만 답하면 돼요", exact=False),
                page.get_by_text("개인정보처리방침", exact=False),
            ],
        )
