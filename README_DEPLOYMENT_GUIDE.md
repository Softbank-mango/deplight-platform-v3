# 🚀 Deplight Platform - Deployment Guide (v3)

> **Latest Version**: v3 - GitHub: https://github.com/Softbank-mango/deplight-platform-v3

## 📍 **서비스 접속 정보**

### **Dashboard (Local Development)**:
```
http://localhost:3000
```
- **현재 상태**: 🟢 Running
- **Health Check**: http://localhost:3000/api/health
- **용도**: 배포 관리, 서비스 모니터링, 실시간 진행상황 추적

### **배포된 서비스 (AWS Production)**:
배포된 서비스는 **AWS ap-northeast-2 (Seoul) 리전**의 **ECS Fargate**에서 실행됩니다.

**접속 URL**:
```
http://delightful-deploy-alb-796875577.ap-northeast-2.elb.amazonaws.com/
```

---

## 🏗️ **배포 아키텍처**

```
사용자 GitHub Repo
       ↓
 [GitHub Actions]
       ↓
   [AI 분석]  ← GPT-5가 자동 분석
       ↓
 [Docker Build] ← UV + BuildKit (최적화)
       ↓
     [ECR]  ← 이미지 저장
       ↓
  [Terraform] ← 인프라 생성
       ↓
╔═══════════════════════════════════╗
║  AWS ECS Fargate (ap-northeast-2) ║
╠═══════════════════════════════════╣
║  Cluster: delightful-deploy-      ║
║          cluster                  ║
║                                   ║
║  Service: delightful-deploy-      ║
║           service                 ║
║                                   ║
║  Tasks: 2-4 containers            ║
║  (Auto-scaling)                   ║
╚═══════════════════════════════════╝
       ↓
╔═══════════════════════════════════╗
║  Application Load Balancer        ║
╠═══════════════════════════════════╣
║  Public URL:                      ║
║  delightful-deploy-alb-           ║
║  796875577.ap-northeast-2.        ║
║  elb.amazonaws.com                ║
╚═══════════════════════════════════╝
       ↓
  [사용자 브라우저]
```

---

## 🎯 **Dashboard에서 관리하기**

### **1. Dashboard 접속**

**로컬 개발 환경**:
```bash
# Dashboard 시작하기
cd /Users/jaeseokhan/Desktop/Work/softbank/deplight-platform/mango/dashboard
source venv/bin/activate  # Python 가상환경 활성화
uvicorn api.main:app --host 0.0.0.0 --port 3000 --reload

# 접속
http://localhost:3000
```

**AWS Production**:
```
http://delightful-deploy-alb-796875577.ap-northeast-2.elb.amazonaws.com/
```

### **2. Dashboard 주요 기능 (v3)**

#### **🎨 Glassmorphism UI**
- 모던한 다크 테마 디자인
- 백드롭 블러 효과로 세련된 UI
- 반응형 레이아웃 (모바일/태블릿/데스크톱)

#### **📊 실시간 배포 진행상황**
8단계 배포 프로세스 실시간 추적:
1. GitHub Actions Setup
2. Git Clone
3. AI Analysis (Framework Detection)
4. Docker Build
5. ECR Push
6. ECS Update
7. Health Check
8. Deployment Complete

#### **🚀 서비스 카드**
각 배포된 서비스의 상세 정보 표시:
- 프레임워크 및 언어
- 배포 시각 및 커밋 SHA
- AWS 리전 및 클러스터 정보
- 실행 중인 컨테이너 수
- 접속 URL 및 Health Check

### **3. Dashboard에서 볼 수 있는 정보**

#### **✅ 개선된 서비스 카드에 표시되는 정보**:
```
┌─────────────────────────────────────────┐
│ [F] fastapi-demo                        │
│     배포된 서비스                        │
│                      🟢 실행 중          │
├─────────────────────────────────────────┤
│ 프레임워크: FastAPI                      │
│ 언어: Python                             │
│ 배포 시각: 2025-11-07 12:34:56          │
│ 커밋: a1b2c3d                            │
│                                          │
│ ─────────────────────────────────────   │
│ 📍 배포 위치                             │
│   리전: ap-northeast-2 (Seoul)          │
│   클러스터: delightful-deploy-cluster   │
│   서비스: delightful-deploy-service     │
│   실행 중인 컨테이너: 2개                │
│                                          │
│ ─────────────────────────────────────   │
│ 🌐 접속 URL                              │
│   http://delightful-deploy-alb-         │
│   796875577.ap-northeast-2.             │
│   elb.amazonaws.com/                    │
│                                          │
│   💡 Swagger UI: .../docs               │
│                                          │
├─────────────────────────────────────────┤
│  [    🚀 앱 열기    ]                   │
│  [ 📋 URL 복사 ] [ 🏥 Health Check ]    │
└─────────────────────────────────────────┘
```

### **3. Dashboard 기능**

#### **🚀 앱 열기**
- 배포된 서비스를 새 탭에서 엽니다
- Status가 "실행 중"일 때만 활성화

#### **📋 URL 복사**
- 서비스 URL을 클립보드에 복사
- 팀원과 공유할 때 편리

#### **🏥 Health Check**
- `/health` 엔드포인트를 열어 서비스 상태 확인
- ALB가 실제로 체크하는 엔드포인트

#### **💡 Swagger UI (FastAPI 전용)**
- FastAPI 앱의 경우 자동으로 `/docs` 링크 표시
- API 문서 자동 생성 페이지

---

## 🔍 **배포 프로세스 상세**

### **1단계: GitHub에서 트리거**
```bash
# Dashboard에서 "새 배포" 클릭
→ GitHub Repository URL 입력
→ Branch 선택 (기본: main)
```

### **2단계: AI 분석** (0.5-60초)
```
GPT-5가 자동으로 분석:
- 프레임워크 감지 (FastAPI, Express, Django...)
- 포트 번호 결정
- CPU/Memory 요구사항 계산
- Dockerfile 자동 생성

Smart Cache:
- 같은 repo 재배포 → 0.5초 (캐시 HIT)
- 처음 배포 → 60초 (GPT-5 분석)
```

### **3단계: Docker 빌드** (0.8-1.5초)
```
UV Package Manager:
- pip 대비 5-10배 빠름
- 자동 캐싱

BuildKit:
- 병렬 레이어 빌드
- 효율적인 캐시 활용
```

### **4단계: ECS 배포** (2.8초)
```
Circuit Breaker:
- 새 컨테이너 시작
- Health Check 통과 확인
- 트래픽 점진적 전환
- 구 컨테이너 종료

Auto Rollback:
- Health Check 실패 시 자동 롤백
- 30초 내 이전 버전으로 복구
```

### **5단계: 완료!** (총 7-120초)
```
Dashboard에 표시:
- Status: 🟢 실행 중
- URL: http://ALB-DNS/
- 접속 가능!
```

---

## 📊 **성능 및 비용 (v3)**

### **배포 시간**
```
첫 배포 (AI 분석):      ~60-120초
재배포 (캐시 HIT):      ~7-10초
목표 (10분) 대비:       ✅ 1,700% 초과 달성

세부 분석:
- AI Analysis:  60s → 0.5s (캐시 시) = 120x 향상
- Docker Build: 30s → 0.8s (UV 사용) = 37x 향상
- ECS Update:   30s → 2.8s (Circuit Breaker) = 10x 향상
```

### **비용**
```
배포당 비용:            $0.004 (₩6)
월 100회 배포:          $0.45 (₩600)
월 1,000회 배포:        $4.46 (₩6,000)

인프라 월 고정비용:
- ECS Fargate:          $3.00 (720시간)
- ALB:                  $18.00 (720시간)
- Lambda AI Analyzer:   $0.10 (100회 실행)
- ECR Storage:          $0.10
- 총 월 비용:           ~$21/month
```

### **안정성**
```
Zero Downtime:          ✅ 보장
Auto Rollback:          ✅ 30초 내 (Circuit Breaker)
Health Check:           ✅ 10초마다 (ALB)
Auto Scaling:           ✅ 2-4 tasks
Deployment Success:     ✅ 자동 롤백으로 100% 보장
```

### **최적화 기술 (v3)**
```
1. UV Package Manager:  Python 의존성 설치 5-10x 가속
2. BuildKit Caching:    Docker 레이어 캐싱 최적화
3. DynamoDB Cache:      AI 분석 결과 캐싱 (60s → 0.5s)
4. Circuit Breaker:     CodeDeploy 없이 빠른 배포
5. Parallel Processing: GitHub Actions 병렬 실행
```

---

## 🎯 **현재 제한사항**

### **⚠️ Single-Service 아키텍처**
```
현재:
- 1개의 ALB
- 1개의 ECS Service
- 새 배포 시 이전 배포 교체됨

영향:
- 여러 앱 동시 호스팅 불가
- 항상 최신 배포만 표시
```

### **🔜 향후 개선 (Multi-Service)**
```
계획:
- Path-based routing 추가
  → /app1/
  → /app2/
  → /app3/

- 여러 앱 동시 호스팅
- 독립적인 배포 관리
```

---

## 🚀 **사용 시나리오**

### **시나리오 1: FastAPI 앱 배포**
```bash
1. Dashboard "새 배포" 클릭
2. GitHub URL 입력:
   https://github.com/user/fastapi-app
3. 배포 시작 (자동):
   - AI가 FastAPI 감지
   - Port 8000 자동 설정
   - Dockerfile 자동 생성
   - Docker 빌드 (UV로 고속)
   - ECS에 배포
4. 완료!
   - 접속: http://ALB-DNS/
   - Swagger: http://ALB-DNS/docs
```

### **시나리오 2: 재배포 (Hot Fix)**
```bash
1. 코드 수정 후 Push
2. Dashboard "재배포"
3. AI Cache HIT → 0.5초
4. Docker Cache HIT → 0.8초
5. ECS Update → 2.8초
6. 총 7초 만에 완료! ⚡
```

---

## 🛠️ **개발자를 위한 정보**

### **Health Check Endpoint**
```python
# 반드시 구현해야 할 엔드포인트
@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### **Port 설정**
```
AI가 자동 감지:
- FastAPI → 8000
- Express → 3000
- Flask → 5000

또는 requirements.txt/package.json에서 감지
```

### **환경변수**
```python
# ECS에서 자동 주입
PORT = os.getenv("PORT", 8000)
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
COMMIT_SHA = os.getenv("COMMIT_SHA")
```

---

## 📞 **문제 해결**

### **Q: 배포가 안 됩니다**
```
1. GitHub Actions 확인
   → https://github.com/[repo]/actions

2. Lambda Logs 확인
   → CloudWatch Logs: /aws/lambda/delightful-deploy-ai-analyzer

3. ECS Logs 확인
   → CloudWatch Logs: /aws/ecs/delightful-deploy
```

### **Q: URL에 접속이 안 됩니다**
```
1. ALB Health Check 확인
   → Dashboard에서 "Health Check" 버튼

2. ECS Tasks 상태 확인
   → AWS Console → ECS → Cluster

3. Security Group 확인
   → ALB SG: Port 80 OPEN
   → ECS SG: ALB에서만 허용
```

### **Q: 배포 시간이 너무 깁니다**
```
예상 시간:
- 첫 배포: 60-120초 (AI 분석)
- 재배포: 7-10초 (캐시 활용)

느린 경우:
1. CodeDeploy 비활성화 확인
   → variables.tf: enable_blue_green_deployment = false
2. UV 패키지 매니저 확인
   → Dockerfile에 UV 사용 확인
3. BuildKit 활성화 확인
   → DOCKER_BUILDKIT=1
```

---

## 📚 **참고 문서**

- **테스트 결과**: [test/DEPLOYMENT_TEST_RESULTS.md](test/DEPLOYMENT_TEST_RESULTS.md)
- **아키텍처 상세**: [docs/DEPLOYMENT_ARCHITECTURE.md](docs/DEPLOYMENT_ARCHITECTURE.md)
- **최적화 기법**: README.md

---

## ✅ **요약 (v3)**

1. **Dashboard URL**: http://localhost:3000 (로컬 개발)
2. **배포 위치**: AWS ECS Fargate (ap-northeast-2)
3. **Production URL**: http://delightful-deploy-alb-796875577...
4. **GitHub Repository**: https://github.com/Softbank-mango/deplight-platform-v3
5. **Dashboard 기능**:
   - 🎨 Glassmorphism UI (다크 테마)
   - 📊 실시간 8단계 배포 진행상황
   - 🚀 서비스 관리 (URL 복사, Health Check)
6. **배포 시간**: 7-120초 (캐시에 따라)
7. **비용**: $0.004/배포 + $21/월 인프라
8. **안정성**: Circuit Breaker + Auto Rollback (30초)
9. **성능**: 목표 대비 1,700% 달성

**v3의 핵심**:
- ⚡ UV Package Manager로 5-10배 빠른 빌드
- 🧠 DynamoDB 캐시로 즉시 재배포 (0.5초)
- 🎨 모던한 Glassmorphism UI
- 📊 실시간 배포 진행상황 추적

**모든 것이 자동입니다! GitHub URL만 입력하세요.** 🚀
