# ⚡ 빠른 시작 명령어 모음

## 🎯 한 번에 실행하기

### 백엔드 시작
```bash
cd backend && uvicorn main:app --reload --port 8000
```

### 프론트엔드 시작  
```bash
cd frontend && npm run dev
```

### 두 서버 동시 시작 (각각 다른 터미널에서)
```bash
# 터미널 1
cd backend && uvicorn main:app --reload --port 8000

# 터미널 2  
cd frontend && npm run dev
```

## 🔍 상태 확인 명령어

### API 헬스체크
```bash
curl http://localhost:8000/api/health
```

### 데이터베이스 통계 확인
```bash
curl http://localhost:8000/api/stats
```

### 프로세스 확인
```bash
# 포트 8000 사용 프로세스 확인
lsof -i :8000

# 포트 5173 사용 프로세스 확인  
lsof -i :5173
```

## 🛑 서버 종료

### 특정 포트 프로세스 종료
```bash
# 백엔드 종료 (포트 8000)
lsof -ti:8000 | xargs kill -9

# 프론트엔드 종료 (포트 5173)
lsof -ti:5173 | xargs kill -9
``` 