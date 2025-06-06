# 🚀 K-Stock Insight 서버 실행 규칙

## ⚠️ 중요: 서버 실행 시 반드시 준수해야 할 규칙

### 📋 실행 전 체크리스트
- [ ] 올바른 디렉토리에서 실행하는지 확인
- [ ] 포트 충돌이 없는지 확인
- [ ] 환경변수가 제대로 설정되어 있는지 확인

### 🖥️ 백엔드 서버 실행 규칙

**⚠️ 반드시 준수: 백엔드는 반드시 backend 디렉토리에서 실행**

```bash
# 올바른 실행 방법
cd backend && uvicorn main:app --reload --port 8000
```

**❌ 잘못된 실행 방법:**
```bash
# 루트 디렉토리에서 실행 - 절대 금지!
uvicorn main:app --reload --port 8000
```

**실행 후 확인사항:**
- 서버가 http://localhost:8000에서 실행되는지 확인
- /api/health 엔드포인트로 헬스체크 수행
- 데이터베이스 연결 상태 확인

### 🌐 프론트엔드 서버 실행 규칙

**⚠️ 반드시 준수: 프론트엔드는 반드시 frontend 디렉토리에서 실행**

```bash
# 올바른 실행 방법
cd frontend && npm run dev
```

**❌ 잘못된 실행 방법:**
```bash
# 루트 디렉토리에서 실행 - 절대 금지!
npm run dev
```

**실행 후 확인사항:**
- 서버가 http://localhost:5173에서 실행되는지 확인
- Vue.js 개발 서버가 정상 시작되는지 확인
- HMR(Hot Module Replacement)이 작동하는지 확인

### 🔧 포트 정보
- **백엔드**: localhost:8000
- **프론트엔드**: localhost:5173

### 📝 환경변수 확인
- 백엔드: `.env` 파일에 DATABASE_URL 설정 확인
- 프론트엔드: VITE_API_BASE_URL 설정 확인

### 🚨 문제 해결
1. **포트 충돌 시**: `lsof -i :[포트번호]`로 프로세스 확인 후 종료
2. **모듈 에러 시**: 올바른 디렉토리에서 실행하는지 확인
3. **데이터베이스 연결 실패**: 환경변수 설정 확인

---
**🎯 기억하세요: 항상 적절한 디렉토리에서 서버를 시작해야 합니다!** 

VITE_API_BASE_URL = https://k-stock-insight-api.onrender.com 