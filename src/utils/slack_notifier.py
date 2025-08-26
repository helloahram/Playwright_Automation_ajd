## src/utils/slack_notifier.py
from __future__ import annotations
from dataclasses import dataclass
import os, time, httpx


@dataclass(frozen=True)
class SlackConfig:
    webhook: str
    mention: str = ""
    enable_markdown: bool = True


def get_slack_config() -> SlackConfig:
    """환경변수에서 Slack 설정 로드 (한 곳에서만 읽음)"""
    return SlackConfig(
        webhook=os.getenv("SLACK_WEBHOOK_URL", "").strip(),
        mention=os.getenv("SLACK_MENTION", "").strip(),
        enable_markdown=True,
    )


def _payload(title: str, title_link: str, text: str, color: str, cfg: SlackConfig):
    txt = (cfg.mention + " " if cfg.mention else "") + (text or "")
    att = {
        "color": color,
        "title": title,
        "title_link": title_link,
        "text": txt,
        "footer": "AJD Monitor",
        "ts": int(time.time()),
    }
    if cfg.enable_markdown:
        att["mrkdwn_in"] = ["text"]
    return {"attachments": [att]}


async def send_alert(
    cfg: SlackConfig,
    *,
    severity: str,
    name: str,
    url: str,
    status: int | None,
    load_ms: int,
    detail: str | None = None,
) -> bool:
    """
    severity: 'ok' | 'slow' | 'fail'
    """
    if not cfg.webhook:
        return False

    # 공통 한 줄 메트릭
    s = status if status is not None else "?"
    metrics = f"*HTTP* {s} | *Load* {load_ms} ms"

    # 타이틀/색상/본문
    if severity == "ok":
        title, color, text = (
            f"✅ OK — {name}",
            "#2eb886",
            f"All checks passed.  •  {metrics}",
        )
    elif severity == "slow":
        title, color, text = (
            f"⚠️ SLOW — {name}",
            "#ECB22E",
            f"{detail or 'Slow'}  •  {metrics}",
        )
    else:
        title, color, text = (
            f"❌ FAIL — {name}",
            "#E01E5A",
            f"{detail or 'Failure'}  •  {metrics}",
        )

    payload = _payload(title, url, text, color, cfg)
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(cfg.webhook, json=payload)
        return resp.status_code in (200, 204)
    except Exception:
        return False
