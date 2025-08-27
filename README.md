# Site Uptime Monitor (Python + Playwright, POM)

> URL 을 주기적으로 점검하고, 비정상 감지 시 슬랙 알림/ 로그/ 스크린샷을 남기는 경량 모니터링 스크립트

## 기능 요약
- **POM (Page Object Model)** 기반: 각 페이지의 `is_ready()` 조건을 독립적으로 정의
- **정상 기준 (기본값)**: HTTP 200, DOM 핵심 요소 렌더 완료, 초기 로드 시간(First Navigation) `<= 3,000ms`
- **결과물**: 실패 시 **슬랙 알림**, **로그 파일(`logs/monitor.log`)**, **스크린샷(`artifacts/*.png`)**
- **반복 실행**: `CHECK_INTERVAL_SEC` 간격으로 무한 루프

## 빠른 시작

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 환경변수 세팅 
cp .env.example .env
# .env 파일 열어 SLACK_WEBHOOK_URL 등을 설정

# 실행
python -m src.monitor.runner
```

## 프로젝트 구조 (POM)
```
Project/
│
├─ base/                    # 기본 페이지 및 공통 동작
│   └─ base_page.py
│
├─ pages/                   # 페이지 오브젝트 정의 (POM)
│   ├─ ajd_main_page.py
│   └─ ajd_internet_recommend_page.py
│
├─ lib/                     # 공용 유틸리티 (로깅/알림 등 공통 기능 모듈)
│   ├─ logging_config.py    # 로그 포맷/ 파일 회전/ Slack URL 마스킹 등 로깅 설정
│   └─ slack_notifier.py    # Slack 알림 발송 유틸리티 (Webhook 사용)
│
├─ monitor/                 # 모니터링/실행 관련 모듈
│   └─ runner.py
│
├─ .env.example             # 환경 변수 예시 파일
```