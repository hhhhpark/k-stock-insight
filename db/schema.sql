-- KRX Data Ingest Database Schema
-- PostgreSQL database schema for Korean stock market data 

-- K-Stock Insight Database Schema
-- PostgreSQL database schema for Korean stock market data

-- 1. 상장 종목 정보 테이블
CREATE TABLE IF NOT EXISTS stocks (
    ticker VARCHAR(6) PRIMARY KEY,
    name TEXT NOT NULL,
    market TEXT NOT NULL CHECK (market IN ('KOSPI', 'KOSDAQ')),
    sector TEXT,
    listed_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 일별 시세 테이블
CREATE TABLE IF NOT EXISTS daily_prices (
    ticker VARCHAR(6) NOT NULL,
    date DATE NOT NULL,
    open INTEGER NOT NULL,
    high INTEGER NOT NULL,
    low INTEGER NOT NULL,
    close INTEGER NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ticker, date),
    FOREIGN KEY (ticker) REFERENCES stocks(ticker) ON DELETE CASCADE
);

-- 3. 매매 주체별 동향 테이블
CREATE TABLE IF NOT EXISTS investor_trends (
    ticker VARCHAR(6) NOT NULL,
    date DATE NOT NULL,
    investor_type TEXT NOT NULL,
    buy_value BIGINT DEFAULT 0,
    sell_value BIGINT DEFAULT 0,
    net_value BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ticker, date, investor_type),
    FOREIGN KEY (ticker) REFERENCES stocks(ticker) ON DELETE CASCADE
);

-- 4. 업종(섹터) 정의 테이블 (수정된 버전)
CREATE TABLE IF NOT EXISTS sectors (
    id SERIAL PRIMARY KEY,
    sector_code VARCHAR(10) NOT NULL,
    sector_name TEXT NOT NULL,
    ticker VARCHAR(6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticker) REFERENCES stocks(ticker) ON DELETE CASCADE,
    UNIQUE(sector_code, ticker)
);

-- 5. 업종별 시세 테이블
CREATE TABLE IF NOT EXISTS sector_prices (
    sector_code VARCHAR(10) NOT NULL,
    sector_name TEXT NOT NULL,
    date DATE NOT NULL,
    open INTEGER NOT NULL,
    high INTEGER NOT NULL,
    low INTEGER NOT NULL,
    close INTEGER NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (sector_code, date)
);

-- 인덱스 생성 (조회 성능 최적화)
CREATE INDEX IF NOT EXISTS idx_daily_prices_date ON daily_prices(date);
CREATE INDEX IF NOT EXISTS idx_daily_prices_ticker ON daily_prices(ticker);
CREATE INDEX IF NOT EXISTS idx_investor_trends_date ON investor_trends(date);
CREATE INDEX IF NOT EXISTS idx_investor_trends_ticker ON investor_trends(ticker);
CREATE INDEX IF NOT EXISTS idx_investor_trends_type ON investor_trends(investor_type);
CREATE INDEX IF NOT EXISTS idx_sector_prices_date ON sector_prices(date);
CREATE INDEX IF NOT EXISTS idx_sectors_code ON sectors(sector_code);
CREATE INDEX IF NOT EXISTS idx_sectors_ticker ON sectors(ticker);

-- 테이블 정보 조회용 뷰
CREATE OR REPLACE VIEW stocks_summary AS
SELECT 
    market,
    COUNT(*) as stock_count,
    MIN(listed_date) as earliest_listing,
    MAX(listed_date) as latest_listing
FROM stocks 
WHERE listed_date IS NOT NULL
GROUP BY market;

-- 최근 거래일 조회용 뷰
CREATE OR REPLACE VIEW latest_trading_date AS
SELECT 
    MAX(date) as latest_date,
    COUNT(DISTINCT ticker) as stocks_with_data
FROM daily_prices; 