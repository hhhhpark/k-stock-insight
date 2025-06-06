# 📦 데이터베이스 스키마 정의 (`k-stock-insight`)

pykrx로부터 수집한 한국 주식 관련 데이터를 PostgreSQL에 저장하기 위한 테이블 정의 문서입니다.  
시세, 종목 정보, 투자자 동향, 업종/섹터 시세 및 구성 등 다양한 분석용 테이블로 구성됩니다.

---

## 📁 테이블 구조

### 1. `stocks` – 상장 종목 정보

| 컬럼명      | 타입        | 설명             |
|-------------|-------------|------------------|
| ticker      | VARCHAR(6)  | 종목 코드         |
| name        | TEXT        | 종목명            |
| market      | TEXT        | KOSPI / KOSDAQ 구분 |
| listed_date | DATE        | 상장일            |
| PRIMARY KEY | (ticker)    |

---

### 2. `daily_prices` – 일별 시세 테이블

| 컬럼명   | 타입        | 설명         |
|----------|-------------|--------------|
| ticker   | VARCHAR(6)  | 종목 코드     |
| date     | DATE        | 거래일        |
| open     | INTEGER     | 시가          |
| high     | INTEGER     | 고가          |
| low      | INTEGER     | 저가          |
| close    | INTEGER     | 종가          |
| volume   | BIGINT      | 거래량        |
| PRIMARY KEY | (ticker, date) |

---

### 3. `investor_trends` – 매매 주체별 동향

| 컬럼명       | 타입        | 설명                 |
|--------------|-------------|----------------------|
| ticker        | VARCHAR(6)  | 종목 코드             |
| date          | DATE        | 거래일                |
| investor_type | TEXT        | 투자자 구분 (개인, 외국인, 기관 등) |
| buy_value     | BIGINT      | 매수 금액             |
| sell_value    | BIGINT      | 매도 금액             |
| net_value     | BIGINT      | 순매수 금액           |
| PRIMARY KEY   | (ticker, date, investor_type) |

---

### 4. `sectors` – 업종(섹터) 정의 테이블

| 컬럼명      | 타입        | 설명                        |
|-------------|-------------|-----------------------------|
| sector_code | VARCHAR(10) | KRX 업종/지수 코드            |
| sector_name | TEXT        | 섹터명 (예: 유통업, 전기전자 등) |
| ticker      | VARCHAR(6)  | 섹터에 포함된 종목 코드         |
| PRIMARY KEY | (sector_code, ticker) |

> ⛳ 한 섹터에 여러 종목이 포함되며, 한 종목이 여러 섹터에 포함될 수도 있음

---

### 5. `sector_prices` – 업종별 시세 테이블

| 컬럼명      | 타입        | 설명                  |
|-------------|-------------|-----------------------|
| sector_code | VARCHAR(10) | KRX 업종/지수 코드      |
| sector_name | TEXT        | 섹터명                |
| date        | DATE        | 시세 기준 일자          |
| open        | INTEGER     | 시가                  |
| high        | INTEGER     | 고가                  |
| low         | INTEGER     | 저가                  |
| close       | INTEGER     | 종가                  |
| volume      | BIGINT      | 거래량                |
| PRIMARY KEY | (sector_code, date) |

---

## 📌 참고 사항

- 모든 테이블은 PostgreSQL 기준으로 설계되었으며, UTC가 아닌 KST 기준 일자 기준으로 수집됨
- `sector_code`는 pykrx의 `get_index_ticker_list()`로 조회한 값 사용
- 섹터 정보는 pykrx의 `get_index_portfolio_deposit_file()`으로 종목 구성 확인 가능

---

## 🛠️ 데이터 수집 방식 요약

| 테이블명        | 수집 함수 예시 (pykrx)                                      |
|-----------------|-------------------------------------------------------------|
| stocks          | `get_market_ticker_list()`, `get_market_ticker_name()`     |
| daily_prices    | `get_market_ohlcv_by_ticker()`                              |
| investor_trends | `get_market_trading_value_by_investor()`                   |
| sectors         | `get_index_ticker_list()`, `get_index_portfolio_deposit_file()` |
| sector_prices   | `get_index_ohlcv_by_date()`                                 |

---

## ⏱️ 향후 추가 예정

- `anomalous_stocks`: 작전주/세력주 추정 종목 관리
- `stock_patterns`: 특정 룰/패턴 부합 종목 기록
- `recommendations`: 종목 추천 결과 및 근거 저장

