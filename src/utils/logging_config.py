## src/utils/logging_config.py
import logging, os, pathlib, re
from logging.handlers import RotatingFileHandler


SLACK_URL_RE = re.compile(r"https://hooks\.slack\.com/services/[A-Za-z0-9/_-]+")


class RedactFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = SLACK_URL_RE.sub(
                "https://hooks.slack.com/services/REDACTED", record.msg
            )
        # args에도 URL이 들어있을 수 있음
        if record.args:
            new_args = []
            for a in record.args:
                if isinstance(a, str):
                    new_args.append(
                        SLACK_URL_RE.sub("https://hooks.slack.com/services/REDACTED", a)
                    )
                else:
                    new_args.append(a)
            record.args = tuple(new_args)
        return True


def init_logging(log_dir: str = "logs") -> None:
    """
    콘솔 + 파일(회전) 로그 설정
    logs/monitor.log에 기록, 1MB 넘어가면 3개까지 백업 보관
    """
    os.makedirs(log_dir, exist_ok=True)
    log_path = pathlib.Path(log_dir) / "monitor.log"

    fmt = "%(asctime)s | %(levelname)s | %(message)s"
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    fh = RotatingFileHandler(
        log_path, maxBytes=2_000_000, backupCount=5, encoding="utf-8"
    )
    ch = logging.StreamHandler()

    formatter = logging.Formatter(fmt)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # 레닥트 필터 장착
    fh.addFilter(RedactFilter())
    ch.addFilter(RedactFilter())

    root.handlers.clear()
    root.addHandler(fh)
    root.addHandler(ch)

    # httpx / httpcore 로거 침묵
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
