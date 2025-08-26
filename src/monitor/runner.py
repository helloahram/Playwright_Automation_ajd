# src/monitor/runner.py
from __future__ import annotations
import asyncio, os, logging, datetime, pathlib
from dotenv import load_dotenv
from playwright.async_api import async_playwright

from src.utils.logging_config import init_logging
from src.utils.slack_notifier import get_slack_config, send_alert
from src.pages.ajd_internet_recommend_page import AjdInternetRecommend


def env_int(key: str, default: int) -> int:
    """환경변수 정수형 안전 파싱 (없거나 형식 오류면 기본값)"""
    try:
        return int(os.getenv(key, str(default)))
    except Exception:
        return default


def env_bool(key: str, default: bool = False) -> bool:
    """환경변수 불리언형 안전 파싱 (1/ true/ yes/ on = True)"""
    v = os.getenv(key)
    return default if v is None else v.strip().lower() in ("1", "true", "yes", "on")


async def snap(page, artifacts_dir: str, name: str, ok: bool = False) -> None:
    """
    전체 페이지 스크린샷 저장
    ok=True면 파일명에 '_ok' 접미사를 붙여 성공 캡처임을 구분
    """
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = "_ok" if ok else ""
    path = pathlib.Path(artifacts_dir) / f"{ts}_{name}{suffix}.png".replace(" ", "_")
    await page.screenshot(path=str(path), full_page=True)
    (logging.info if ok else logging.error)("Saved screenshot: %s", path)


async def check_once(
    browser,
    interval: int,
    artifacts_dir: str,
    timeout_ms: int,
    slow_ms: int,
    always_ss: bool,
    notify_ok: bool,
    alert_slow: bool,
    slack_cfg,
) -> bool:
    """
    한 번의 점검 라운드:
    1) 단일 브라우저 컨텍스트/ 페이지 생성
    2) 타겟 페이지(AJD-Recommend) 순회
    3) 결과에 따라 로그/ 스크린샷/ 슬랙 전송
    반환값: 라운드 전체의 OK 여부 (둘 다 OK면 True)
    """
    ok_all = True
    context = await browser.new_context(viewport={"width": 1280, "height": 900})
    page = await context.new_page()
    try:
        targets = [
            ("AJD-Internet-Recommend", AjdInternetRecommend(page)),
        ]

        for name, pobj in targets:
            # 각 PageObject 의 check() 는 HTTP/ 핵심요소/ 성능(slow_ms)까지 판단
            res = await pobj.check(timeout_ms=timeout_ms, slow_ms=slow_ms)

            # 느림 경고는 detail 이 "Slow ..." 로 시작하는 케이스로 식별
            is_slow = (not res.ok) and res.detail.startswith("Slow")

            if res.ok:
                logging.info("OK  | %-13s | %s | %dms", name, res.url, res.load_ms)

                # (옵션) 성공 케이스 스샷도 보관
                if always_ss:
                    try:
                        await snap(page, artifacts_dir, name, ok=True)
                    except Exception as e:
                        logging.error("Screenshot failed: %r", e)

                # 정상 상태도 슬랙 통지 (표현/포맷은 notifier가 담당)
                if notify_ok:
                    await send_alert(
                        slack_cfg,
                        severity="ok",
                        name=name,
                        url=res.url,
                        status=res.status,
                        load_ms=res.load_ms,
                    )

            else:
                ok_all = False
                logging.error(
                    "FAIL| %-13s | %s | %s | %dms",
                    name,
                    res.url,
                    res.detail,
                    res.load_ms,
                )

                # 실패/ 느림 스샷 저장(증적)
                try:
                    await snap(page, artifacts_dir, name, ok=False)
                except Exception as e:
                    logging.error("Screenshot failed: %r", e)

                # 느림 경고 vs 완전 실패 구분하여 notifier 에 위임
                if is_slow and alert_slow:
                    await send_alert(
                        slack_cfg,
                        severity="slow",
                        name=name,
                        url=res.url,
                        status=res.status,
                        load_ms=res.load_ms,
                        detail=res.detail,
                    )
                else:
                    await send_alert(
                        slack_cfg,
                        severity="fail",
                        name=name,
                        url=res.url,
                        status=res.status,
                        load_ms=res.load_ms,
                        detail=res.detail,
                    )
    finally:
        await context.close()

    logging.info("Next check in %ss ...", interval)
    return ok_all


async def main() -> None:
    """프로세스 Entry Point: 설정 로드, 로그 초기화, 무한 모니터링 루프"""
    load_dotenv()
    init_logging(log_dir="logs")

    # 모니터링 파라미터 (환경변수로 제어)
    interval = env_int("CHECK_INTERVAL_SEC", 60)
    timeout_ms = env_int("NAVIGATION_TIMEOUT_MS", 10_000)
    slow_ms = env_int("SLOW_THRESHOLD_MS", 3_000)
    headless = os.getenv("HEADLESS", "true").lower() != "false"
    always_ss = env_bool("ALWAYS_SCREENSHOT", False)
    notify_ok = env_bool("NOTIFY_ON_OK", False)
    alert_slow = env_bool("ALERT_ON_SLOW", True)

    # Slack 설정은 notifier 가 한 번만 읽어서 구조체로 보관
    slack_cfg = get_slack_config()

    logging.info(
        "Starting monitor | interval=%ss timeout=%sms slow=%sms headless=%s",
        interval,
        timeout_ms,
        slow_ms,
        headless,
    )

    # Playwright 세션 시작
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        try:
            while True:
                try:
                    await check_once(
                        browser=browser,
                        interval=interval,
                        artifacts_dir="artifacts",
                        timeout_ms=timeout_ms,
                        slow_ms=slow_ms,
                        always_ss=always_ss,
                        notify_ok=notify_ok,
                        alert_slow=alert_slow,
                        slack_cfg=slack_cfg,
                    )
                except Exception as e:
                    # 어떤 예외가 나도 루프는 계속 (모니터는 죽지 않게)
                    logging.exception("Top-level check_once error: %r", e)
                await asyncio.sleep(interval)
        finally:
            await browser.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped by user")
