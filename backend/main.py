# FastAPI main application 
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import logging
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="K-Stock Insight API",
    description="한국 주식 시장 분석 및 투자자 동향 API",
    version="1.0.0"
)

# CORS 설정 - 환경에 따라 다르게 설정
ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vue.js 개발 서버
    "http://127.0.0.1:5173",  # Vue.js 개발 서버 (대안)
    "https://your-frontend-app.onrender.com",  # Render 프론트엔드 도메인 (배포 후 수정 필요)
]

# 환경 변수에서 추가 도메인 허용
if additional_origins := os.getenv('ALLOWED_ORIGINS'):
    ALLOWED_ORIGINS.extend(additional_origins.split(','))

# 개발 환경에서는 모든 도메인 허용
if os.getenv('ENVIRONMENT') == 'development':
    ALLOWED_ORIGINS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 설정
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # DATABASE_URL이 있는 경우 이를 사용
    def get_db_connection():
        """데이터베이스 연결 생성 (DATABASE_URL 사용)"""
        try:
            conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
            return conn
        except Exception as e:
            logger.error(f"데이터베이스 연결 실패: {e}")
            raise HTTPException(status_code=500, detail="데이터베이스 연결 실패")
else:
    # 개별 설정 사용
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'k_stock_insight'),
        'user': os.getenv('DB_USER', 'hhhhp'),
        'password': os.getenv('DB_PASSWORD', '')
    }

    def get_db_connection():
        """데이터베이스 연결 생성"""
        try:
            conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
            return conn
        except Exception as e:
            logger.error(f"데이터베이스 연결 실패: {e}")
            raise HTTPException(status_code=500, detail="데이터베이스 연결 실패")

@app.get("/")
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "K-Stock Insight API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy", 
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@app.get("/api/stats")
async def get_database_stats():
    """데이터베이스 통계 정보"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 각 테이블별 레코드 수 조회
        stats = {}
        
        tables = ['stocks', 'daily_prices', 'sector_prices', 'investor_trends']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            result = cursor.fetchone()
            stats[table] = result['count']
        
        # 추가 통계
        cursor.execute("SELECT COUNT(DISTINCT ticker) as unique_stocks FROM daily_prices")
        stats['unique_stocks_with_prices'] = cursor.fetchone()['unique_stocks']
        
        cursor.execute("SELECT MIN(date) as min_date, MAX(date) as max_date FROM daily_prices")
        date_range = cursor.fetchone()
        stats['date_range'] = {
            'start': date_range['min_date'].isoformat() if date_range['min_date'] else None,
            'end': date_range['max_date'].isoformat() if date_range['max_date'] else None
        }
        
        conn.close()
        return stats
        
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")

@app.get("/api/stocks")
async def get_stocks(
    limit: int = 100,
    offset: int = 0,
    market: Optional[str] = None,
    search: Optional[str] = None
):
    """종목 목록 조회"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 기본 쿼리 - sectors 테이블과 JOIN
        query = """
            SELECT s.ticker, s.name, s.market, sec.sector_name
            FROM stocks s 
            LEFT JOIN sectors sec ON s.ticker = sec.ticker
            WHERE 1=1
        """
        params = []
        
        # 시장 필터
        if market:
            query += " AND s.market = %s"
            params.append(market)
        
        # 검색 필터
        if search:
            query += " AND (s.name ILIKE %s OR s.ticker ILIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])
        
        # 정렬 및 페이징
        query += " ORDER BY s.ticker LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        stocks = cursor.fetchall()
        
        # 전체 개수 조회
        count_query = """
            SELECT COUNT(*) as total 
            FROM stocks s 
            LEFT JOIN sectors sec ON s.ticker = sec.ticker
            WHERE 1=1
        """
        count_params = []
        
        if market:
            count_query += " AND s.market = %s"
            count_params.append(market)
            
        if search:
            count_query += " AND (s.name ILIKE %s OR s.ticker ILIKE %s)"
            count_params.extend([f"%{search}%", f"%{search}%"])
        
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()['total']
        
        conn.close()
        
        return {
            "stocks": [dict(stock) for stock in stocks],
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"종목 조회 실패: {str(e)}")

@app.get("/api/stocks/{ticker}")
async def get_stock_detail(ticker: str):
    """특정 종목 상세 정보"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 종목 기본 정보 - sectors 테이블과 JOIN
        cursor.execute("""
            SELECT s.ticker, s.name, s.market, s.listed_date, sec.sector_name
            FROM stocks s 
            LEFT JOIN sectors sec ON s.ticker = sec.ticker
            WHERE s.ticker = %s
        """, (ticker,))
        
        stock = cursor.fetchone()
        if not stock:
            raise HTTPException(status_code=404, detail="종목을 찾을 수 없습니다")
        
        # 최근 주가 정보 (복수개)
        cursor.execute("""
            SELECT date, open, high, low, close, volume
            FROM daily_prices 
            WHERE ticker = %s 
            ORDER BY date DESC 
            LIMIT 20
        """, (ticker,))
        
        recent_prices = cursor.fetchall()
        
        # 투자자 동향 정보
        cursor.execute("""
            SELECT investor_type, SUM(net_value) as total_net
            FROM investor_trends 
            WHERE ticker = %s 
            GROUP BY investor_type
            ORDER BY total_net DESC
        """, (ticker,))
        
        investor_trends = cursor.fetchall()
        
        conn.close()
        
        return {
            "stock": dict(stock),
            "recent_prices": [dict(price) for price in recent_prices],
            "investor_trends": [dict(trend) for trend in investor_trends]
        }
        
    except HTTPException:
        conn.close()
        raise
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"종목 상세 조회 실패: {str(e)}")

@app.get("/api/stocks/{ticker}/prices")
async def get_stock_prices(
    ticker: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100
):
    """종목별 주가 데이터"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
            SELECT date, open, high, low, close, volume
            FROM daily_prices 
            WHERE ticker = %s
        """
        params = [ticker]
        
        if start_date:
            query += " AND date >= %s"
            params.append(start_date)
            
        if end_date:
            query += " AND date <= %s"
            params.append(end_date)
        
        query += " ORDER BY date DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        prices = cursor.fetchall()
        
        conn.close()
        
        return {
            "ticker": ticker,
            "prices": [dict(price) for price in prices]
        }
        
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"주가 데이터 조회 실패: {str(e)}")

@app.get("/api/stocks/{ticker}/investor-trends")
async def get_stock_investor_trends(
    ticker: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """종목별 투자자 동향 데이터"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
            SELECT date, investor_type, buy_value, sell_value, net_value
            FROM investor_trends 
            WHERE ticker = %s
        """
        params = [ticker]
        
        if start_date:
            query += " AND date >= %s"
            params.append(start_date)
            
        if end_date:
            query += " AND date <= %s"
            params.append(end_date)
        
        query += " ORDER BY date DESC, investor_type"
        
        cursor.execute(query, params)
        trends = cursor.fetchall()
        
        conn.close()
        
        return {
            "ticker": ticker,
            "investor_trends": [dict(trend) for trend in trends]
        }
        
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"투자자 동향 조회 실패: {str(e)}")

@app.get("/api/sectors")
async def get_sectors():
    """섹터 목록 및 최신 가격"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT DISTINCT sector_code, sector_name
            FROM sector_prices 
            ORDER BY sector_name
        """)
        
        sectors = cursor.fetchall()
        
        # 각 섹터의 최신 가격 정보
        sector_latest = []
        for sector in sectors:
            cursor.execute("""
                SELECT sector_code, sector_name, date, close, volume
                FROM sector_prices 
                WHERE sector_code = %s 
                ORDER BY date DESC 
                LIMIT 1
            """, (sector['sector_code'],))
            
            latest = cursor.fetchone()
            if latest:
                sector_latest.append(dict(latest))
        
        conn.close()
        
        return {
            "sectors": sector_latest
        }
        
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"섹터 데이터 조회 실패: {str(e)}")

@app.get("/api/dashboard")
async def get_dashboard_data():
    """대시보드용 요약 데이터"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        dashboard_data = {}
        
        # 주요 통계
        cursor.execute("""
            SELECT 
                COUNT(*) as total_stocks,
                COUNT(CASE WHEN market = 'KOSPI' THEN 1 END) as kospi_stocks,
                COUNT(CASE WHEN market = 'KOSDAQ' THEN 1 END) as kosdaq_stocks
            FROM stocks
        """)
        dashboard_data['market_stats'] = dict(cursor.fetchone())
        
        # 최근 활발한 종목 (거래량 기준)
        cursor.execute("""
            SELECT s.ticker, s.name, dp.close, dp.volume, dp.date
            FROM daily_prices dp
            JOIN stocks s ON dp.ticker = s.ticker
            WHERE dp.date = (SELECT MAX(date) FROM daily_prices)
            ORDER BY dp.volume DESC
            LIMIT 10
        """)
        dashboard_data['top_volume_stocks'] = [dict(row) for row in cursor.fetchall()]
        
        # 투자자별 순매수 상위 종목
        cursor.execute("""
            SELECT 
                it.ticker, 
                s.name,
                it.investor_type,
                SUM(it.net_value) as total_net_value
            FROM investor_trends it
            JOIN stocks s ON it.ticker = s.ticker
            WHERE it.date >= (SELECT MAX(date) - INTERVAL '7 days' FROM investor_trends)
            GROUP BY it.ticker, s.name, it.investor_type
            HAVING SUM(it.net_value) > 0
            ORDER BY total_net_value DESC
            LIMIT 10
        """)
        dashboard_data['top_net_purchases'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return dashboard_data
        
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"대시보드 데이터 조회 실패: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 