# Render PostgreSQL Database Configuration
# 프로덕션 환경용 데이터베이스 설정

import os

# Render PostgreSQL 데이터베이스 설정
DB_CONFIG_PRODUCTION = {
    'host': 'dpg-d117riidbo4c739o703g-a.oregon-postgres.render.com',
    'port': '5432',
    'database': 'k_stock_db',
    'user': 'k_stock_db_user',
    'password': 'D0mPVuWhsdVqGJ5XYsrP0Yv0OjoBHNmQ'
}

# 환경변수 설정 함수
def set_production_env():
    """프로덕션 환경변수 설정"""
    os.environ['DB_HOST'] = DB_CONFIG_PRODUCTION['host']
    os.environ['DB_PORT'] = DB_CONFIG_PRODUCTION['port']
    os.environ['DB_NAME'] = DB_CONFIG_PRODUCTION['database']
    os.environ['DB_USER'] = DB_CONFIG_PRODUCTION['user']
    os.environ['DB_PASSWORD'] = DB_CONFIG_PRODUCTION['password']
    os.environ['ENVIRONMENT'] = 'production'

# 개발 환경 설정
DB_CONFIG_DEVELOPMENT = {
    'host': 'localhost',
    'port': '5432',
    'database': 'k_stock_insight',
    'user': 'hhhhp',
    'password': ''
}

def set_development_env():
    """개발 환경변수 설정"""
    os.environ['DB_HOST'] = DB_CONFIG_DEVELOPMENT['host']
    os.environ['DB_PORT'] = DB_CONFIG_DEVELOPMENT['port']
    os.environ['DB_NAME'] = DB_CONFIG_DEVELOPMENT['database']
    os.environ['DB_USER'] = DB_CONFIG_DEVELOPMENT['user']
    os.environ['DB_PASSWORD'] = DB_CONFIG_DEVELOPMENT['password']
    os.environ['ENVIRONMENT'] = 'development' 