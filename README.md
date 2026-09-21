# lunit_dart — Lunit DART financial analysis

DART 공시 원문에서 루닛의 연간 재무제표를 수집하고 주요 재무비율을 계산합니다.

## 준비
1. DART Open API 인증키 발급: https://opendart.fss.or.kr/
2. `.env.example`을 `.env`로 복사하고 `DART_API_KEY` 입력
3. Python 3.10+ 환경에서:
   ```bash
   pip install -r requirements.txt
   python src/fetch_dart.py --years 5
   python src/analyze.py
   ```

## 결과
- `data/raw/`: DART API 원천 응답(JSON)
- `data/processed/`: 표준화한 재무데이터 및 비율(CSV)
- `reports/`: 요약 분석(Markdown)

## 주의
- 기본은 사업보고서(연간), 연결(CFS) 우선이며 연결 데이터가 없으면 별도(OFS)를 확인합니다.
- DART 계정과목은 회사/연도별로 달라 자동 매핑이 누락될 수 있습니다. `src/analyze.py`의 계정명 매핑을 검증하세요.
- 재무상태표는 기말잔액, 손익/현금흐름은 기간금액입니다. ROA·ROE·회전율은 평균 잔액이 필요하며, 첫 연도는 전기 잔액이 없어 일부 비율이 비어 있을 수 있습니다.
- 공시 원문과 수치의 출처(접수번호·계정명)를 함께 보존하고, 최종 분석 전 사업보고서 주석과 대조하세요.
- DART API 키는 절대 GitHub에 커밋하지 마세요.
