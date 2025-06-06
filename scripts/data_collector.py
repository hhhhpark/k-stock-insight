#!/usr/bin/env python3
"""
K-Stock Insight 데이터 수집 스크립트

pykrx를 사용해서 한국 주식 시장 데이터를 수집하고 PostgreSQL에 저장합니다.
- 종목 정보 (stocks)
- 일별 시세 (daily_prices) 
- 투자자 동향 (investor_trends)
- 섹터 정보 (sectors)
- 섹터별 시세 (sector_prices)

Features:
- 진행률 실시간 표시 (tqdm)
- 중간 저장 결과 체크
- 배치별 커밋으로 안정성 확보
- 에러 처리 및 재시도
- 설정 가능한 수집 기간
"""

import os
import sys
import pandas as pd
import psycopg2
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
import time
from tqdm import tqdm

# pykrx 모듈 import
try:
    from pykrx import stock
except ImportError:
    print("pykrx 모듈이 설치되지 않았습니다. 'pip install pykrx' 명령어로 설치해주세요.")
    sys.exit(1)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================
# 🔧 설정 변수 (쉽게 변경 가능)
# ============================

# 데이터 수집 기간 설정 (2025년 1월 1일부터)
START_DATE = '20250101'  # 2025년 1월 1일부터
END_DATE = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')  # 어제까지

# 데이터베이스 연결 설정
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'k_stock_insight'),
    'user': os.getenv('DB_USER', 'hhhhp'),
    'password': os.getenv('DB_PASSWORD', '')
}

# 수집할 시장 구분
MARKETS = ['KOSPI', 'KOSDAQ']

# 처리 설정
BATCH_SIZE = 50  # 배치 크기 (메모리 사용량 조절)
CHECK_INTERVAL = 100  # 100개마다 저장 상태 체크
MAX_RETRIES = 3  # 최대 재시도 횟수

class KRXDataCollector:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.total_processed = 0
        self.total_saved = 0
        self.total_failed = 0
        self.start_time = None
        self.connect_db()
        
    def connect_db(self):
        """PostgreSQL 데이터베이스 연결"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor()
            logger.info("✅ 데이터베이스 연결 성공")
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 실패: {e}")
            sys.exit(1)
    
    def close_db(self):
        """데이터베이스 연결 종료"""
        if self.conn:
            self.conn.close()
            logger.info("🔚 데이터베이스 연결 종료")
    
    def collect_stocks_info(self) -> pd.DataFrame:
        """1. 상장 종목 정보 수집"""
        logger.info("📊 상장 종목 정보 수집 시작...")
        
        all_stocks = []
        
        for market in MARKETS:
            try:
                # 종목 코드 리스트 가져오기
                tickers = stock.get_market_ticker_list(market=market)
                logger.info(f"{market} 종목 수: {len(tickers)}개")
                
                for ticker in tqdm(tickers, desc=f"{market} 종목 정보"):
                    try:
                        # 종목명 가져오기
                        name = stock.get_market_ticker_name(ticker)
                        
                        all_stocks.append({
                            'ticker': ticker,
                            'name': name,
                            'market': market,
                            'listed_date': None  # pykrx에서 직접 제공하지 않음
                        })
                        
                    except Exception as e:
                        logger.warning(f"종목 {ticker} 정보 수집 실패: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"{market} 종목 리스트 수집 실패: {e}")
                continue
        
        df = pd.DataFrame(all_stocks)
        logger.info(f"총 {len(df)}개 종목 정보 수집 완료")
        return df
    
    def collect_daily_prices(self, tickers: List[str]) -> int:
        """2. 일별 시세 데이터 수집 (전체 종목)"""
        logger.info("📈 일별 시세 데이터 수집 시작...")
        
        # 수집 기간 계산
        start_dt = datetime.strptime(START_DATE, '%Y%m%d')
        end_dt = datetime.strptime(END_DATE, '%Y%m%d')
        period_days = (end_dt - start_dt).days + 1
        
        logger.info(f"📅 수집 기간: {START_DATE} ~ {END_DATE} ({period_days}일)")
        
        self.start_time = time.time()
        total_saved_records = 0
        processed_count = 0
        batch_saved = 0
        
        # 진행률 표시를 위한 tqdm 사용
        pbar = tqdm(tickers, desc="시세 데이터 수집", unit="종목")
        
        for ticker in pbar:
            try:
                # 종목별 OHLCV 데이터 수집
                df = stock.get_market_ohlcv_by_date(START_DATE, END_DATE, ticker)
                
                if not df.empty:
                    df = df.reset_index()
                    df['ticker'] = ticker
                    
                    # 컬럼명 매핑
                    df.rename(columns={
                        '날짜': 'date',
                        '시가': 'open',
                        '고가': 'high', 
                        '저가': 'low',
                        '종가': 'close',
                        '거래량': 'volume'
                    }, inplace=True)
                    
                    # DB 저장
                    saved_count = 0
                    for _, row in df.iterrows():
                        query = """
                        INSERT INTO daily_prices (ticker, date, open, high, low, close, volume) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s) 
                        ON CONFLICT (ticker, date) DO UPDATE SET 
                        open = EXCLUDED.open, high = EXCLUDED.high, low = EXCLUDED.low, 
                        close = EXCLUDED.close, volume = EXCLUDED.volume
                        """
                        
                        self.cursor.execute(query, (
                            row['ticker'], row['date'], row['open'], 
                            row['high'], row['low'], row['close'], row['volume']
                        ))
                        saved_count += 1
                    
                    total_saved_records += saved_count
                    batch_saved += saved_count
                    
                    # tqdm 설명 업데이트
                    pbar.set_postfix({
                        'records': f'{total_saved_records:,}',
                        'failed': self.total_failed
                    })
                    
                else:
                    self.total_failed += 1
                
                processed_count += 1
                
                # 배치마다 커밋
                if processed_count % BATCH_SIZE == 0:
                    self.conn.commit()
                    logger.info(f"💾 배치 커밋: {batch_saved}개 레코드 저장")
                    batch_saved = 0
                
                # 주기적 진행 상황 체크
                if processed_count % CHECK_INTERVAL == 0:
                    self.check_progress(processed_count, len(tickers), total_saved_records)
                    
            except Exception as e:
                self.total_failed += 1
                logger.warning(f"종목 {ticker} 시세 수집 실패: {e}")
                continue
        
        # 최종 커밋
        self.conn.commit()
        
        logger.info(f"✅ 총 {total_saved_records:,}개 시세 데이터 저장 완료!")
        return total_saved_records
    
    def check_progress(self, processed: int, total: int, saved_records: int):
        """진행률 및 저장 상태 체크"""
        elapsed_time = time.time() - self.start_time
        progress_percent = (processed / total) * 100
        
        # 예상 완료 시간 계산
        if processed > 0:
            avg_time_per_ticker = elapsed_time / processed
            remaining_tickers = total - processed
            estimated_remaining = remaining_tickers * avg_time_per_ticker
            
            logger.info(f"📈 진행률: {processed}/{total} ({progress_percent:.1f}%)")
            logger.info(f"⏱️ 경과 시간: {elapsed_time/60:.1f}분")
            logger.info(f"🕐 예상 남은 시간: {estimated_remaining/60:.1f}분")
            logger.info(f"💾 저장된 레코드: {saved_records:,}개")
            logger.info(f"❌ 실패한 종목: {self.total_failed}개")
        
        # 현재 DB 상태 확인
        self.cursor.execute("SELECT COUNT(*) FROM daily_prices")
        total_db_records = self.cursor.fetchone()[0]
        
        # 최근 저장된 종목들
        self.cursor.execute("""
            SELECT ticker, COUNT(*) as records, MAX(date) as latest_date
            FROM daily_prices 
            GROUP BY ticker 
            ORDER BY MAX(created_at) DESC 
            LIMIT 5
        """)
        
        recent_data = self.cursor.fetchall()
        logger.info(f"🗄️ DB 총 레코드: {total_db_records:,}개")
        logger.info("📅 최근 저장된 종목들:")
        for ticker, records, latest_date in recent_data:
            logger.info(f"  - {ticker}: {records}개, 최신일 {latest_date}")
        
        logger.info("-" * 50)
    
    def collect_investor_trends(self, tickers: List[str]) -> int:
        """3. 투자자 동향 데이터 수집"""
        logger.info("👥 투자자 동향 데이터 수집 시작...")
        
        # 수집 기간 계산
        start_dt = datetime.strptime(START_DATE, '%Y%m%d')
        end_dt = datetime.strptime(END_DATE, '%Y%m%d')
        period_days = (end_dt - start_dt).days + 1
        
        logger.info(f"📅 수집 기간: {START_DATE} ~ {END_DATE} ({period_days}일)")
        
        total_saved_records = 0
        processed_count = 0
        batch_saved = 0
        
        # 진행률 표시를 위한 tqdm 사용
        pbar = tqdm(tickers, desc="투자자 동향 수집", unit="종목")
        
        for ticker in pbar:
            try:
                # 투자자별 거래 데이터 수집
                df = stock.get_market_net_purchases_of_equities_by_ticker(START_DATE, END_DATE, ticker)
                
                if not df.empty:
                    df = df.reset_index()
                    df['ticker'] = ticker
                    
                    # 컬럼명 확인 및 매핑
                    logger.debug(f"투자자 동향 데이터 컬럼: {list(df.columns)}")
                    
                    # pykrx 컬럼명을 DB 컬럼명으로 매핑
                    column_mapping = {
                        '날짜': 'date',
                        '기관계': 'institution_net',
                        '기타법인': 'other_corp_net', 
                        '개인': 'individual_net',
                        '외국인계': 'foreign_net',
                        '전체': 'total_net'
                    }
                    
                    # 실제 존재하는 컬럼만 매핑
                    existing_mapping = {k: v for k, v in column_mapping.items() if k in df.columns}
                    df.rename(columns=existing_mapping, inplace=True)
                    
                    # DB 저장
                    saved_count = 0
                    for _, row in df.iterrows():
                        # 기본값 설정
                        data_dict = {
                            'ticker': row['ticker'],
                            'date': row.get('date', row.name if 'date' not in row else None),
                            'foreign_buy': 0,
                            'foreign_sell': 0,
                            'foreign_net': row.get('foreign_net', 0),
                            'institution_buy': 0,
                            'institution_sell': 0, 
                            'institution_net': row.get('institution_net', 0),
                            'individual_buy': 0,
                            'individual_sell': 0,
                            'individual_net': row.get('individual_net', 0)
                        }
                        
                        query = """
                        INSERT INTO investor_trends 
                        (ticker, date, foreign_buy, foreign_sell, foreign_net, 
                         institution_buy, institution_sell, institution_net,
                         individual_buy, individual_sell, individual_net) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                        ON CONFLICT (ticker, date) DO UPDATE SET 
                        foreign_net = EXCLUDED.foreign_net,
                        institution_net = EXCLUDED.institution_net,
                        individual_net = EXCLUDED.individual_net
                        """
                        
                        try:
                            self.cursor.execute(query, (
                                data_dict['ticker'], data_dict['date'],
                                data_dict['foreign_buy'], data_dict['foreign_sell'], data_dict['foreign_net'],
                                data_dict['institution_buy'], data_dict['institution_sell'], data_dict['institution_net'],
                                data_dict['individual_buy'], data_dict['individual_sell'], data_dict['individual_net']
                            ))
                            saved_count += 1
                        except Exception as e:
                            logger.warning(f"종목 {ticker} 날짜 {data_dict['date']} 저장 실패: {e}")
                            continue
                    
                    total_saved_records += saved_count
                    batch_saved += saved_count
                    
                    # tqdm 설명 업데이트
                    pbar.set_postfix({
                        'records': f'{total_saved_records:,}',
                        'failed': self.total_failed
                    })
                    
                else:
                    self.total_failed += 1
                
                processed_count += 1
                
                # 배치마다 커밋
                if processed_count % BATCH_SIZE == 0:
                    self.conn.commit()
                    logger.info(f"💾 투자자 동향 배치 커밋: {batch_saved}개 레코드 저장")
                    batch_saved = 0
                
                # 주기적 진행 상황 체크
                if processed_count % CHECK_INTERVAL == 0:
                    self.check_investor_progress(processed_count, len(tickers), total_saved_records)
                    
            except Exception as e:
                self.total_failed += 1
                logger.warning(f"종목 {ticker} 투자자 동향 수집 실패: {e}")
                continue
        
        # 최종 커밋
        self.conn.commit()
        
        logger.info(f"✅ 총 {total_saved_records:,}개 투자자 동향 데이터 저장 완료!")
        return total_saved_records
    
    def check_investor_progress(self, processed: int, total: int, saved_records: int):
        """투자자 동향 수집 진행률 체크"""
        progress_percent = (processed / total) * 100
        
        logger.info(f"👥 투자자 동향 진행률: {processed}/{total} ({progress_percent:.1f}%)")
        logger.info(f"💾 저장된 투자자 동향 레코드: {saved_records:,}개")
        
        # 현재 DB 상태 확인
        self.cursor.execute("SELECT COUNT(*) FROM investor_trends")
        total_db_records = self.cursor.fetchone()[0]
        
        logger.info(f"🗄️ 투자자 동향 DB 총 레코드: {total_db_records:,}개")
        logger.info("-" * 50)
    
    def collect_sectors_info(self) -> pd.DataFrame:
        """4. 섹터(업종) 정보 수집"""
        logger.info("🏢 섹터 정보 수집 시작...")
        
        all_sectors = []
        
        try:
            # 업종 지수 리스트 가져오기
            sector_codes = stock.get_index_ticker_list(market="KOSPI")
            
            for sector_code in tqdm(sector_codes, desc="섹터 정보 수집"):
                try:
                    # 섹터명 가져오기
                    sector_name = stock.get_index_ticker_name(sector_code)
                    
                    all_sectors.append({
                        'sector_code': sector_code,
                        'sector_name': sector_name,
                        'ticker': None  # 구성종목은 별도 처리
                    })
                        
                except Exception as e:
                    logger.warning(f"섹터 {sector_code} 정보 수집 실패: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"섹터 리스트 수집 실패: {e}")
        
        df = pd.DataFrame(all_sectors)
        logger.info(f"총 {len(df)}개 섹터 데이터 수집 완료")
        return df
    
    def collect_sector_prices(self) -> int:
        """5. 업종별 시세 데이터 수집"""
        logger.info("🏢 업종별 시세 데이터 수집 시작...")
        
        start_dt = datetime.strptime(START_DATE, '%Y%m%d')
        end_dt = datetime.strptime(END_DATE, '%Y%m%d')
        period_days = (end_dt - start_dt).days + 1
        
        logger.info(f"📅 수집 기간: {START_DATE} ~ {END_DATE} ({period_days}일)")
        
        total_saved_records = 0
        
        try:
            # 업종 지수 리스트 가져오기
            sector_codes = stock.get_index_ticker_list(market="KOSPI")
            logger.info(f"📊 대상 업종 수: {len(sector_codes)}개")
            
            pbar = tqdm(sector_codes, desc="업종 시세 수집", unit="업종")
            
            for sector_code in pbar:
                try:
                    # 업종명 가져오기
                    sector_name = stock.get_index_ticker_name(sector_code)
                    
                    # 업종별 OHLCV 데이터 수집
                    df = stock.get_index_ohlcv_by_date(START_DATE, END_DATE, sector_code)
                    
                    if not df.empty:
                        df = df.reset_index()
                        
                        # 각 날짜별로 저장
                        for _, row in df.iterrows():
                            date_val = row['날짜'] if '날짜' in row else row.name
                            
                            query = """
                            INSERT INTO sector_prices 
                            (sector_code, sector_name, date, open, high, low, close, volume) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                            ON CONFLICT (sector_code, date) DO UPDATE SET 
                            sector_name = EXCLUDED.sector_name,
                            open = EXCLUDED.open, high = EXCLUDED.high, 
                            low = EXCLUDED.low, close = EXCLUDED.close, 
                            volume = EXCLUDED.volume
                            """
                            
                            # 컬럼명 매핑
                            open_val = row['시가'] if '시가' in row else row.get('open', 0)
                            high_val = row['고가'] if '고가' in row else row.get('high', 0)
                            low_val = row['저가'] if '저가' in row else row.get('low', 0)
                            close_val = row['종가'] if '종가' in row else row.get('close', 0)
                            volume_val = row['거래량'] if '거래량' in row else row.get('volume', 0)
                            
                            self.cursor.execute(query, (
                                sector_code, sector_name, date_val,
                                int(open_val), int(high_val), int(low_val), 
                                int(close_val), int(volume_val)
                            ))
                            total_saved_records += 1
                        
                        # 진행률 업데이트
                        pbar.set_postfix({'records': f'{total_saved_records:,}'})
                        
                        # 주기적 커밋
                        if total_saved_records % 1000 == 0:
                            self.conn.commit()
                            
                except Exception as e:
                    logger.warning(f"업종 {sector_code} 시세 수집 실패: {e}")
                    continue
            
            # 최종 커밋
            self.conn.commit()
            logger.info(f"✅ 총 {total_saved_records:,}개 업종 시세 레코드 저장 완료!")
            
        except Exception as e:
            logger.error(f"업종 시세 수집 중 오류: {e}")
            
        return total_saved_records
    
    def save_to_db(self, df: pd.DataFrame, table_name: str):
        """데이터프레임을 PostgreSQL 테이블에 저장"""
        if df.empty:
            logger.warning(f"{table_name} 테이블에 저장할 데이터가 없습니다.")
            return
        
        try:
            cursor = self.conn.cursor()
            
            # 테이블별 INSERT 쿼리 생성
            if table_name == 'stocks':
                query = """
                INSERT INTO stocks (ticker, name, market, listed_date) 
                VALUES (%s, %s, %s, %s) 
                ON CONFLICT (ticker) DO UPDATE SET 
                name = EXCLUDED.name, market = EXCLUDED.market
                """
                data = [(row['ticker'], row['name'], row['market'], row['listed_date']) 
                       for _, row in df.iterrows()]
                
            elif table_name == 'sectors':
                query = """
                INSERT INTO sectors (sector_code, sector_name, ticker) 
                VALUES (%s, %s, %s) 
                ON CONFLICT (sector_code, ticker) DO NOTHING
                """
                data = [(row['sector_code'], row['sector_name'], row['ticker']) 
                       for _, row in df.iterrows()]
                
            else:
                logger.warning(f"테이블 {table_name}에 대한 INSERT 쿼리가 구현되지 않았습니다.")
                return
            
            cursor.executemany(query, data)
            self.conn.commit()
            logger.info(f"✅ {table_name} 테이블에 {len(data)}개 레코드 저장 완료")
            
        except Exception as e:
            logger.error(f"❌ {table_name} 테이블 저장 실패: {e}")
            self.conn.rollback()
    
    def final_database_check(self):
        """최종 데이터베이스 상태 확인"""
        logger.info("\n📋 최종 데이터베이스 상태:")
        
        # 일별 시세 데이터 상태
        self.cursor.execute("SELECT COUNT(*) FROM daily_prices")
        total_prices = self.cursor.fetchone()[0]
        
        # 투자자 동향 데이터 상태  
        self.cursor.execute("SELECT COUNT(*) FROM investor_trends")
        total_trends = self.cursor.fetchone()[0]
        
        # 업종별 시세 데이터 상태
        self.cursor.execute("SELECT COUNT(*) FROM sector_prices")
        total_sectors = self.cursor.fetchone()[0]
        
        # 종목별 통계
        self.cursor.execute("""
            SELECT COUNT(DISTINCT ticker) as unique_tickers,
                   MIN(date) as earliest_date,
                   MAX(date) as latest_date,
                   AVG(volume) as avg_volume
            FROM daily_prices
        """)
        stats = self.cursor.fetchone()
        
        logger.info(f"📈 일별 시세 레코드: {total_prices:,}개")
        logger.info(f"👥 투자자 동향 레코드: {total_trends:,}개")
        logger.info(f"🏢 업종별 시세 레코드: {total_sectors:,}개")
        logger.info(f"📊 수집된 종목 수: {stats[0]:,}개")
        logger.info(f"📅 데이터 기간: {stats[1]} ~ {stats[2]}")
        logger.info(f"💹 평균 거래량: {int(stats[3]):,}주")
        
        # 상위 거래량 종목들
        self.cursor.execute("""
            SELECT s.ticker, s.name, AVG(dp.volume) as avg_volume
            FROM daily_prices dp
            JOIN stocks s ON dp.ticker = s.ticker
            GROUP BY s.ticker, s.name
            ORDER BY avg_volume DESC
            LIMIT 5
        """)
        
        top_volume = self.cursor.fetchall()
        logger.info("\n🔥 평균 거래량 상위 5개 종목:")
        for ticker, name, avg_vol in top_volume:
            logger.info(f"  {ticker} ({name}): {int(avg_vol):,}주")
        
        # 투자자 동향 샘플 확인
        self.cursor.execute("""
            SELECT ticker, date, investor_type, net_value
            FROM investor_trends 
            ORDER BY date DESC, ABS(net_value) DESC
            LIMIT 5
        """)
        
        top_trends = self.cursor.fetchall()
        if top_trends:
            logger.info("\n👥 최근 순매수 상위 5개:")
            for ticker, date, investor_type, net_value in top_trends:
                logger.info(f"  {ticker} ({date}): {investor_type} {net_value:,}")
        
        # 업종별 시세 샘플 확인
        self.cursor.execute("""
            SELECT sector_code, sector_name, COUNT(*) as records,
                   MIN(date) as start_date, MAX(date) as end_date
            FROM sector_prices 
            GROUP BY sector_code, sector_name
            ORDER BY records DESC
            LIMIT 5
        """)
        
        top_sectors = self.cursor.fetchall()
        if top_sectors:
            logger.info("\n🏢 업종별 시세 상위 5개:")
            for sector_code, sector_name, records, start_date, end_date in top_sectors:
                logger.info(f"  {sector_code} ({sector_name}): {records:,}개 ({start_date} ~ {end_date})")

def main():
    """메인 실행 함수"""
    # 수집 기간 계산
    start_dt = datetime.strptime(START_DATE, '%Y%m%d')
    end_dt = datetime.strptime(END_DATE, '%Y%m%d')
    period_days = (end_dt - start_dt).days + 1
    
    logger.info("🚀 K-Stock Insight 데이터 수집 시작")
    logger.info(f"📅 수집 기간: {START_DATE} ~ {END_DATE} ({period_days}일)")
    
    collector = KRXDataCollector()
    
    try:
        # 1. 종목 정보 수집 (처음에만 필요)
        stocks_df = collector.collect_stocks_info()
        if not stocks_df.empty:
            collector.save_to_db(stocks_df, 'stocks')
            tickers = stocks_df['ticker'].tolist()
        else:
            # 이미 저장된 종목 리스트 사용
            collector.cursor.execute("SELECT ticker FROM stocks ORDER BY ticker")
            tickers = [row[0] for row in collector.cursor.fetchall()]
            logger.info(f"기존 저장된 {len(tickers)}개 종목 사용")
        
        if not tickers:
            logger.error("❌ 종목 정보를 가져올 수 없습니다.")
            return
        
        # 2. 일별 시세 수집 (메인 작업)
        total_saved = collector.collect_daily_prices(tickers)
        
        # 3. 투자자 동향 수집
        investor_saved = collector.collect_investor_trends(tickers)
        
        # 4. 섹터 정보 수집
        sectors_df = collector.collect_sectors_info()
        if not sectors_df.empty:
            collector.save_to_db(sectors_df, 'sectors')
        
        # 5. 업종별 시세 수집
        sector_saved = collector.collect_sector_prices()
        
        # 6. 최종 상태 확인
        collector.final_database_check()
        
        logger.info("✅ 모든 데이터 수집 완료!")
        
    except KeyboardInterrupt:
        logger.info("🛑 사용자에 의해 중단되었습니다.")
    except Exception as e:
        logger.error(f"❌ 데이터 수집 중 오류 발생: {e}")
        
    finally:
        collector.close_db()

if __name__ == "__main__":
    main() 