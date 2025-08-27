# AJD Site Uptime Monitor (Python + Playwright, POM)

> 2개 URL을 주기적으로 점검하고, 비정상 감지 시 슬랙 알림/로그/스크린샷을 남기는 경량 모니터링 스크립트

## 확인 대상
- `https://www.ajd.co.kr/internet/recommend`

## 기능 요약
- **POM (Page Object Model)** 기반: 각 페이지의 `is_ready()` 조건을 독립적으로 정의
- **정상 기준(기본값)**: HTTP 200, DOM 핵심 요소 렌더 완료, 초기 로드 시간(First Navigation) `<= 3,000ms`
- **결과물**: 실패 시 **슬랙 알림**, **로그 파일(`logs/monitor.log`)**, **스크린샷(`artifacts/*.png`)**
- **반복 실행**: `CHECK_INTERVAL_SEC`(기본 60초) 간격으로 무한 루프

## 빠른 시작

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Playwright 드라이버 설치
python -m playwright install

# 환경변수 세팅 (.env 파일 사용 권장)
cp .env.example .env
# .env 파일 열어 SLACK_WEBHOOK_URL 등을 설정

# 실행
python -m src.monitor.runner
```

## .env 설정
- `SLACK_WEBHOOK_URL`: 슬랙 Incoming Webhook URL (미설정 시 슬랙 전송 건너뜀)
- `CHECK_INTERVAL_SEC`: 반복 주기(초). 기본 60
- `NAVIGATION_TIMEOUT_MS`: 페이지 로드 타임아웃(ms). 기본 10000
- `SLOW_THRESHOLD_MS`: 느린 응답 임계치(ms). 기본 3000
- `HEADLESS`: `true`/`false`(기본 true)

## POM 구조
```
Project/
│
├─ base/                    # 기본 페이지 및 공통 동작
│   └─ base_page.py
│
├─ pages/                   # 페이지 오브젝트 정의 (POM)
│   └─ ajd_internet_recommend_page.py
│
├─ lib/                     # 공용 유틸리티
│   ├─ logging_config.py
│   └─ slack_notifier.py
│
├─ monitor/                 # 모니터링/실행 관련 모듈
│   └─ runner.py
```

## 품질 기준 (최상의 결과물 정의)
1) **가용성**: HTTP status 200 (리다이렉트 체인 최종 응답 기준)

2) **핵심 요소 렌더링**: 각 페이지의 고유 핵심 텍스트/요소 감지

3) **성능**: 최초 네비게이션 완료까지 3000ms 이하

4) **관측성**: 실패 시 슬랙 알림, 로그, 스크린샷 모두 남을 것

5) **안정성**: 예외 발생 시에도 루프가 끊기지 않고 다음 주기에 재시도

## 자체 검증 체크리스트
- [ ] 정상일 때 runner가 OK 로그를 남기고 종료 없이 루프 지속
- [ ] 의도적으로 URL을 오타내면(또는 셀렉터 변경) 슬랙 알림/스크린샷이 생성됨
- [ ] `.env` 미설정 시에도 로컬 로그/스크린샷은 동작
- [ ] Playwright 드라이버 미설치 시 사용자에게 설치 가이드가 보임
- [ ] 타임아웃/네트워크 오류 시에도 프로세스는 살아있음

---

> ⚠️ 본 저장소는 **실제 서비스에 부하를 주지 않도록** 기본 주기를 길게 잡았습니다. 단기간 과도한 부하는 피하세요.
