# K-Stock Insight Configuration
import os
from datetime import datetime, timedelta

# 데이터베이스 설정
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'k_stock_insight'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password')
}

# 데이터 수집 설정
DATA_COLLECTION = {
    'default_period_days': 14,  # 기본 수집 기간 (일)
    'batch_size': 100,          # 배치 크기
    'max_retries': 3,           # 재시도 횟수
    'delay_between_requests': 0.1,  # 요청 간 지연 시간 (초)
}

# 시장 설정
MARKETS = ['KOSPI', 'KOSDAQ']

# 투자자 유형 매핑
INVESTOR_TYPES = {
    '금융투자': 'securities',
    '보험': 'insurance', 
    '투신': 'investment_trust',
    '사모': 'private_equity',
    '은행': 'bank',
    '기타금융': 'other_financial',
    '연기금': 'pension_fund',
    '기관합계': 'institutional_total',
    '기타법인': 'other_corporate',
    '개인': 'individual',
    '외국인': 'foreign',
    '기타외국인': 'other_foreign'
}

# 로깅 설정
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'k_stock_insight.log'
}

# FastAPI 설정
API_CONFIG = {
    'host': '0.0.0.0',
    'port': 8000,
    'debug': os.getenv('DEBUG', 'False').lower() == 'true',
    'reload': os.getenv('RELOAD', 'False').lower() == 'true'
}

# 프론트엔드 설정
FRONTEND_CONFIG = {
    'dev_server_port': 3000,
    'api_base_url': os.getenv('API_BASE_URL', 'http://localhost:8000')
} 