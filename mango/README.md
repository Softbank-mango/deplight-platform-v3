# 🍊 Mango - Delightful Deploy

> AI 기반 자동 배포 시스템 - SoftBank 2025 Hackathon

## 📁 프로젝트 구조

```
mango/
├── README.md                          # 이 파일
├── .github/
│   └── workflows/
│       ├── analyzer.yml               # AI Analyzer 워크플로우
│       └── deploy.yml                 # CI/CD 배포 워크플로우
│
├── infrastructure/
│   └── terraform/                     # Terraform 인프라 코드
│       ├── main.tf                    # 메인 설정
│       ├── ecs.tf                     # ECS Fargate
│       ├── lambda.tf                  # Lambda 함수
│       ├── dynamodb.tf                # DynamoDB 테이블
│       └── codedeploy.tf              # CodeDeploy Blue-Green
│
├── lambda/
│   └── ai_code_analyzer/              # AI 코드 분석 Lambda
│       ├── handler.py                 # Lambda 핸들러
│       ├── generators/                # Dockerfile/Terraform 생성
│       └── templates/                 # 템플릿
│
├── dashboard/                         # 웹 대시보드
│   ├── api/
│   │   └── main.py                    # FastAPI 백엔드
│   └── static/
│       ├── index.html                 # 대시보드 UI
│       └── deploy.html                # 배포 UI
│
├── deployer/                          # 배포 엔진 (모듈화)
│   ├── __init__.py
│   ├── engine.py                      # 메인 배포 엔진
│   ├── logger.py                      # DynamoDB 로거
│   └── modules/
│       ├── git_cloner.py              # Git Clone
│       ├── ai_analyzer.py             # Lambda 호출
│       ├── docker_builder.py          # Docker Build
│       ├── ecr_pusher.py              # ECR Push
│       ├── terraform_runner.py        # Terraform Apply
│       ├── codedeploy_manager.py      # CodeDeploy
│       └── health_checker.py          # Health Check
│
├── scripts/                           # 유틸리티 스크립트
│   ├── create_deployment_logs_table.py
│   ├── clear_dynamodb.py
│   └── ...
│
└── test/                              # 테스트 앱들
    └── scenario1/                     # FastAPI 테스트 앱
```

## 🎯 아키텍처

```
┌─────────────────┐
│   사용자         │
│  (Dashboard)    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│     FastAPI Backend                 │
│  (/api/deploy)                      │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Deployment Engine (deployer/)      │
│  ├─ Git Clone                       │
│  ├─ Lambda (AI Analysis)            │
│  ├─ Docker Build                    │
│  ├─ ECR Push                        │
│  ├─ Terraform Apply                 │
│  └─ Health Check                    │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│         AWS Services                │
│  ├─ Lambda (AI Analyzer)            │
│  ├─ ECR (Image Registry)            │
│  ├─ ECS Fargate                     │
│  ├─ CodeDeploy (Blue-Green)         │
│  └─ DynamoDB (Logs)                 │
└─────────────────────────────────────┘
```

## 🚀 배포 플로우

1. **Git Push 감지** - 사용자가 저장소 URL 입력
2. **AI 분석** - Lambda 함수가 GPT-5로 코드 분석
3. **프로젝트 감지** - 프레임워크, 언어, 의존성 감지
4. **설정 생성** - Dockerfile, Terraform 자동 생성
5. **Docker 빌드** - 이미지 빌드
6. **ECR 푸시** - Amazon ECR에 이미지 업로드
7. **ECS 배포** - Terraform Apply → CodeDeploy Blue-Green
8. **Health Check** - 서비스 상태 확인

## 📦 모듈 설명

### Deployer 모듈

각 배포 단계가 독립된 모듈로 분리되어 있습니다:

- **`GitCloner`**: GitHub 저장소 클론
- **`AIAnalyzer`**: Lambda 함수 호출 (GPT-5 분석)
- **`DockerBuilder`**: Docker 이미지 빌드
- **`ECRPusher`**: ECR 푸시
- **`TerraformRunner`**: Terraform apply 실행
- **`CodeDeployManager`**: CodeDeploy Blue-Green 배포
- **`HealthChecker`**: Health check 수행

### Dashboard API

- FastAPI 기반 REST API
- 실시간 배포 상태 폴링
- DynamoDB에서 로그 읽기

### Lambda AI Analyzer

- GPT-5 기반 코드 분석
- 자동 Dockerfile 생성
- Terraform 설정 생성

## 🛠 개발 가이드

### 환경 변수

```bash
# AWS
AWS_REGION=ap-northeast-2
ECR_REGISTRY=513348493870.dkr.ecr.ap-northeast-2.amazonaws.com
ECR_REPOSITORY=delightful-deploy
ECS_CLUSTER=delightful-deploy-cluster
ECS_SERVICE=delightful-deploy-service

# Lambda
AI_ANALYZER_LAMBDA=delightful-deploy-ai-analyzer

# DynamoDB
DEPLOYMENT_HISTORY_TABLE=delightful-deploy-deployment-history
DEPLOYMENT_LOGS_TABLE=delightful-deploy-deployment-logs
AI_ANALYSIS_TABLE=delightful-deploy-ai-analysis
```

### 로컬 실행

```bash
# Dashboard 실행
cd dashboard/api
python3 main.py

# 대시보드 접속
http://localhost:3000
```

## 📚 문서

- [아키텍처 설계](/docs/deployment_system.md)
- [개발 계획](/docs/dev_plan.md)
- [Garden 아이디어](/docs/DEPLOYMENT_GARDEN.md)

## ✅ 구현 상태

- ✅ Lambda AI Analyzer (GPT-5)
- ✅ Terraform Infrastructure (ECS, ALB, CodeDeploy)
- ✅ Dashboard UI (FastAPI)
- ✅ Deployer 모듈화 (완료)
  - ✅ GitCloner - Real Git clone
  - ✅ AIAnalyzer - Real Lambda invocation
  - ✅ DockerBuilder - Real Docker build
  - ✅ ECRPusher - Real ECR push
  - ✅ TerraformRunner - Real ECS service update
  - ✅ HealthChecker - Real HTTP health checks
  - ⏳ CodeDeployManager - Stub (Blue-Green 배포는 향후 구현)
- ⏳ GitHub Actions Workflows (TODO)

## 🚀 실행 방법

```bash
# 1. Mango 디렉토리로 이동
cd /Users/jaeseokhan/Desktop/Work/softbank/mango

# 2. 테스트: 모듈 import 확인
python3 test_import.py

# 3. Dashboard 실행
./run_dashboard.sh

# 또는 직접 실행:
cd dashboard/api
python3 main.py
```

Dashboard는 http://localhost:3000 에서 접속 가능합니다.

## 🎓 SoftBank 2025 Hackathon

**팀**: Delightful Deploy
**주제**: AI 기반 자동 배포 시스템
**기간**: 2025-11-01 ~ 2025-11-05
