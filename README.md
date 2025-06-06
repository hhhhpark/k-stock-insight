# K-Stock Insight

한국 주식 시장 분석 및 투자자 동향 분석 플랫폼

## 프로젝트 개요

K-Stock Insight는 한국 주식 시장의 데이터를 수집, 분석하여 투자자들에게 유용한 정보를 제공하는 웹 애플리케이션입니다.

### 주요 기능

- 📈 **주식 데이터 분석**: KOSPI/KOSDAQ 전 종목 일봉 데이터
- 💰 **투자자 동향 분석**: 투자자 유형별 매매 동향 추적
- 🏭 **섹터 분석**: 업종별 시장 동향 분석
- 📊 **실시간 대시보드**: 주요 지표 및 통계 정보

## 기술 스택

### Backend
- **FastAPI**: Python 웹 프레임워크
- **PostgreSQL**: 데이터베이스
- **pykrx**: 한국거래소 데이터 수집
- **psycopg2**: PostgreSQL 연결

### Frontend
- **Vue.js 3**: 프론트엔드 프레임워크
- **Vite**: 빌드 도구
- **Tailwind CSS**: 스타일링
- **Chart.js**: 데이터 시각화
- **Pinia**: 상태 관리

## 데이터 현황

- **종목 수**: 2,761개 (KOSPI + KOSDAQ)
- **일봉 데이터**: 276,647개 레코드
- **섹터 데이터**: 4,949개 레코드 (49개 섹터)
- **투자자 동향**: 2,105개 레코드
- **데이터 기간**: 2025-01-02 ~ 2025-06-04

## 설치 및 실행

### 사전 요구사항

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

### 백엔드 설정

```bash
# 백엔드 의존성 설치
cd backend
pip install -r requirements.txt

# 데이터베이스 설정 (PostgreSQL)
createdb k_stock_insight

# 백엔드 서버 실행
uvicorn main:app --reload --port 8000
```

### 프론트엔드 설정

```bash
# 프론트엔드 의존성 설치
cd frontend
npm install

# 프론트엔드 개발 서버 실행
npm run dev
```

### 접속

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

## API 엔드포인트

### 주요 API

- `GET /api/health` - 헬스 체크
- `GET /api/stats` - 데이터베이스 통계
- `GET /api/stocks` - 종목 목록 조회
- `GET /api/stocks/{ticker}` - 종목 상세 정보
- `GET /api/stocks/{ticker}/prices` - 종목별 주가 데이터
- `GET /api/stocks/{ticker}/investor-trends` - 투자자 동향 데이터
- `GET /api/sectors` - 섹터 분석 데이터
- `GET /api/dashboard` - 대시보드 요약 데이터

## 데이터베이스 스키마

### 주요 테이블

1. **stocks**: 종목 기본 정보
2. **daily_prices**: 일봉 데이터 (OHLCV)
3. **investor_trends**: 투자자 유형별 매매 동향
4. **sector_prices**: 섹터별 가격 데이터
5. **sectors**: 섹터 정보

## 개발 진행사항

### 완료된 기능
- ✅ 데이터 수집 시스템 구축
- ✅ 백엔드 API 개발
- ✅ 프론트엔드 기본 구조 구현
- ✅ 종목 검색 및 상세 정보 조회
- ✅ 섹터 분석 기능

### 개발 예정
- 🔄 투자자 동향 시각화
- 🔄 고급 검색 필터
- 🔄 개인화된 관심 종목 관리
- 🔄 실시간 데이터 업데이트

## 라이선스

MIT License

## 기여

이슈 리포트나 풀 리퀘스트는 언제든 환영합니다.

---

*본 프로젝트는 투자 참고용으로만 사용하시기 바라며, 투자 결정에 대한 책임은 본인에게 있습니다.* 