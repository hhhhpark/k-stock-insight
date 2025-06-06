#!/usr/bin/env python3
"""
K-Stock Insight 데이터 업데이트 스크립트

각 테이블의 마지막 날짜부터 어제까지의 데이터를 수집하여 업데이트합니다.
- 일별 자동 실행에 최적화
- 효율적인 증분 업데이트
- 누락 데이터 자동 보완

사용법:
    python scripts/data_updater.py
"""

import os
import sys
import pandas as pd
import psycopg2
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
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
        logging.FileHandler('data_update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 데이터베이스 연결 설정
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'k_stock_insight'),
    'user': os.getenv('DB_USER', 'hhhhp'),
    'password': os.getenv('DB_PASSWORD', '')
}

# 처리 설정
BATCH_SIZE = 100  # 업데이트용으로 배치 크기 증가
MAX_RETRIES = 3
API_DELAY = 1  # API 호출 간격 (초)

class DataUpdater:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
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
    
    def get_last_date(self, table_name: str, date_column: str = 'date') -> Optional[str]:
        """테이블에서 마지막 날짜 조회"""
        try:
            query = f"SELECT MAX({date_column}) FROM {table_name}"
            self.cursor.execute(query)
            result = self.cursor.fetchone()[0]
            
            if result:
                return result.strftime('%Y%m%d')
            else:
                logger.warning(f"{table_name} 테이블이 비어있습니다.")
                return None
                
        except Exception as e:
            logger.error(f"{table_name} 테이블 마지막 날짜 조회 실패: {e}")
            return None
    
    def get_update_period(self, table_name: str) -> tuple:
        """업데이트할 기간 계산"""
        last_date = self.get_last_date(table_name)
        
        if not last_date:
            # 테이블이 비어있으면 최근 30일간 데이터 수집
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
            logger.info(f"{table_name}: 테이블이 비어있어 최근 30일 데이터 수집")
        else:
            # 마지막 날짜 다음날부터
            last_dt = datetime.strptime(last_date, '%Y%m%d')
            start_date = (last_dt + timedelta(days=1)).strftime('%Y%m%d')
        
        end_date = self.yesterday
        
        # 업데이트할 데이터가 있는지 확인
        if start_date > end_date:
            logger.info(f"{table_name}: 업데이트할 데이터가 없습니다 (마지막: {last_date}, 어제: {end_date})")
            return None, None
        
        return start_date, end_date
    
    def get_stock_tickers(self) -> List[str]:
        """기존 종목 리스트 가져오기"""
        self.cursor.execute("SELECT ticker FROM stocks ORDER BY ticker")
        tickers = [row[0] for row in self.cursor.fetchall()]
        logger.info(f"📊 대상 종목 수: {len(tickers)}개")
        return tickers
    
    def update_daily_prices(self, tickers: List[str]) -> int:
        """일별 시세 데이터 업데이트"""
        logger.info("📈 일별 시세 데이터 업데이트 시작...")
        
        start_date, end_date = self.get_update_period('daily_prices')
        if not start_date:
            return 0
        
        logger.info(f"📅 업데이트 기간: {start_date} ~ {end_date}")
        
        total_saved = 0
        processed_count = 0
        
        pbar = tqdm(tickers, desc="시세 업데이트", unit="종목")
        
        for ticker in pbar:
            try:
                df = stock.get_market_ohlcv_by_date(start_date, end_date, ticker)
                
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
                        total_saved += 1
                    
                    pbar.set_postfix({'records': f'{total_saved:,}'})
                
                processed_count += 1
                
                # 배치마다 커밋
                if processed_count % BATCH_SIZE == 0:
                    self.conn.commit()
                
                # API 호출 간격
                time.sleep(API_DELAY)
                    
            except Exception as e:
                logger.warning(f"종목 {ticker} 시세 업데이트 실패: {e}")
                continue
        
        # 최종 커밋
        self.conn.commit()
        logger.info(f"✅ 일별 시세 {total_saved:,}개 레코드 업데이트 완료!")
        return total_saved
    
    def update_investor_trends(self, tickers: List[str]) -> int:
        """투자자 동향 데이터 업데이트"""
        logger.info("👥 투자자 동향 데이터 업데이트 시작...")
        
        start_date, end_date = self.get_update_period('investor_trends')
        if not start_date:
            return 0
        
        logger.info(f"📅 업데이트 기간: {start_date} ~ {end_date}")
        
        total_saved = 0
        processed_count = 0
        
        pbar = tqdm(tickers, desc="투자자 동향 업데이트", unit="종목")
        
        for ticker in pbar:
            try:
                df = stock.get_market_net_purchases_of_equities_by_ticker(start_date, end_date, ticker)
                
                if not df.empty:
                    df = df.reset_index()
                    
                    # 각 날짜별로 처리
                    for _, row in df.iterrows():
                        date_val = row['날짜'] if '날짜' in row else row.name
                        
                        # 투자자 유형별 데이터 추출 및 저장
                        investor_data = []
                        
                        # 외국인
                        if '외국인계' in row:
                            investor_data.append({
                                'investor_type': '외국인',
                                'net_value': int(row['외국인계']) if pd.notna(row['외국인계']) else 0
                            })
                        
                        # 기관
                        if '기관계' in row:
                            investor_data.append({
                                'investor_type': '기관',
                                'net_value': int(row['기관계']) if pd.notna(row['기관계']) else 0
                            })
                        
                        # 개인
                        if '개인' in row:
                            investor_data.append({
                                'investor_type': '개인',
                                'net_value': int(row['개인']) if pd.notna(row['개인']) else 0
                            })
                        
                        # 기타법인
                        if '기타법인' in row:
                            investor_data.append({
                                'investor_type': '기타법인',
                                'net_value': int(row['기타법인']) if pd.notna(row['기타법인']) else 0
                            })
                        
                        # DB에 저장
                        for investor in investor_data:
                            query = """
                            INSERT INTO investor_trends 
                            (ticker, date, investor_type, buy_value, sell_value, net_value) 
                            VALUES (%s, %s, %s, %s, %s, %s) 
                            ON CONFLICT (ticker, date, investor_type) DO UPDATE SET 
                            net_value = EXCLUDED.net_value
                            """
                            
                            self.cursor.execute(query, (
                                ticker, date_val, investor['investor_type'],
                                0, 0, investor['net_value']  # buy/sell은 0으로 설정
                            ))
                            total_saved += 1
                
                processed_count += 1
                pbar.set_postfix({'records': f'{total_saved:,}'})
                
                # 배치마다 커밋
                if processed_count % BATCH_SIZE == 0:
                    self.conn.commit()
                
                # API 호출 간격
                time.sleep(API_DELAY)
                    
            except Exception as e:
                logger.warning(f"종목 {ticker} 투자자 동향 업데이트 실패: {e}")
                continue
        
        # 최종 커밋
        self.conn.commit()
        logger.info(f"✅ 투자자 동향 {total_saved:,}개 레코드 업데이트 완료!")
        return total_saved
    
    def update_sector_prices(self) -> int:
        """업종별 시세 데이터 업데이트"""
        logger.info("🏢 업종별 시세 데이터 업데이트 시작...")
        
        start_date, end_date = self.get_update_period('sector_prices')
        if not start_date:
            return 0
        
        logger.info(f"📅 업데이트 기간: {start_date} ~ {end_date}")
        
        total_saved = 0
        
        try:
            sector_codes = stock.get_index_ticker_list(market="KOSPI")
            logger.info(f"📊 대상 업종 수: {len(sector_codes)}개")
            
            pbar = tqdm(sector_codes, desc="업종 시세 업데이트", unit="업종")
            
            for sector_code in pbar:
                try:
                    sector_name = stock.get_index_ticker_name(sector_code)
                    df = stock.get_index_ohlcv_by_date(start_date, end_date, sector_code)
                    
                    if not df.empty:
                        df = df.reset_index()
                        
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
                            total_saved += 1
                        
                        pbar.set_postfix({'records': f'{total_saved:,}'})
                    
                    # API 호출 간격
                    time.sleep(API_DELAY)
                            
                except Exception as e:
                    logger.warning(f"업종 {sector_code} 시세 업데이트 실패: {e}")
                    continue
            
            # 최종 커밋
            self.conn.commit()
            logger.info(f"✅ 업종별 시세 {total_saved:,}개 레코드 업데이트 완료!")
            
        except Exception as e:
            logger.error(f"업종 시세 업데이트 중 오류: {e}")
            
        return total_saved
    
    def update_status_summary(self):
        """업데이트 상태 요약"""
        logger.info("\n📋 업데이트 완료 상태:")
        
        tables = ['daily_prices', 'investor_trends', 'sector_prices']
        
        for table in tables:
            try:
                # 총 레코드 수
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                total = self.cursor.fetchone()[0]
                
                # 최신 날짜
                last_date = self.get_last_date(table)
                
                # 오늘 업데이트된 레코드 수 (created_at 기준)
                self.cursor.execute(f"""
                    SELECT COUNT(*) FROM {table} 
                    WHERE created_at >= CURRENT_DATE
                """)
                today_updates = self.cursor.fetchone()[0]
                
                logger.info(f"📊 {table}: {total:,}개 (최신: {last_date}, 오늘 업데이트: {today_updates:,}개)")
                
            except Exception as e:
                logger.error(f"{table} 상태 확인 실패: {e}")

def main():
    """메인 실행 함수"""
    logger.info("🔄 K-Stock Insight 데이터 업데이트 시작")
    logger.info(f"📅 업데이트 대상: ~ {(datetime.now() - timedelta(days=1)).strftime('%Y%m%d')} (어제)")
    
    updater = DataUpdater()
    
    try:
        # 종목 리스트 가져오기
        tickers = updater.get_stock_tickers()
        
        if not tickers:
            logger.error("❌ 종목 데이터가 없습니다. 먼저 data_collector.py를 실행해주세요.")
            return
        
        start_time = time.time()
        
        # 1. 일별 시세 업데이트
        logger.info("=" * 50)
        prices_updated = updater.update_daily_prices(tickers)
        
        # 2. 투자자 동향 업데이트  
        logger.info("=" * 50)
        trends_updated = updater.update_investor_trends(tickers)
        
        # 3. 업종별 시세 업데이트
        logger.info("=" * 50)
        sectors_updated = updater.update_sector_prices()
        
        # 4. 업데이트 상태 요약
        logger.info("=" * 50)
        updater.update_status_summary()
        
        elapsed_time = time.time() - start_time
        total_updated = prices_updated + trends_updated + sectors_updated
        
        logger.info(f"✅ 업데이트 완료!")
        logger.info(f"📊 총 업데이트: {total_updated:,}개 레코드")
        logger.info(f"⏱️ 소요 시간: {elapsed_time/60:.1f}분")
        
    except KeyboardInterrupt:
        logger.info("🛑 사용자에 의해 중단되었습니다.")
    except Exception as e:
        logger.error(f"❌ 데이터 업데이트 중 오류 발생: {e}")
        
    finally:
        updater.close_db()

if __name__ == "__main__":
    main() 