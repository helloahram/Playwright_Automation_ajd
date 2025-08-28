## src/pages/ajd_main_page.py
from playwright.async_api import Page
from src.base.base_page import BasePage, PageCheckResult


class AjdMainPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(
            page,
            "https://www.ajd.co.kr/",
            ready_locators=[
                page.locator("img[alt*='생활지원금']"),
                page.get_by_text("생활지원금 지킴이", exact=False),
                page.get_by_text("개인정보처리방침", exact=False),
            ],
        )
