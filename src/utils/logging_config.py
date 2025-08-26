## src/utils/logging_config.py
import logging
from logging.handlers import RotatingFileHandler
import os


def init_logging(log_dir: str) -> None:
    """
    콘솔 + 파일(회전) 로그 설정
    logs/monitor.log에 기록, 1MB 넘어가면 3개까지 백업 보관
    """
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "monitor.log")

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    # 콘솔 로그
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # 파일 로그 (회전)
    fh = RotatingFileHandler(
        log_path, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    fh.setFormatter(fmt)
    logger.addHandler(fh)
