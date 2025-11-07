# 🎨 Dashboard Deployment Guide

## 📍 현재 상태

**GitHub Repository:** https://github.com/Softbank-mango/deplight-platform-v3

**현재 실행 중인 앱:**
- URL: http://delightful-deploy-alb-796875577.ap-northeast-2.elb.amazonaws.com/
- 앱: E-Commerce FastAPI Application
- 상태: 🟢 실행 중

---

## 🚀 대시보드 배포 방법

### **방법 1: GitHub Actions 자동 배포 (권장)**

#### 준비사항
1. GitHub에서 `deplight-platform-v3` 레포에 AWS secrets 설정
2. OIDC Role ARN 설정

#### 배포 단계
```bash
# 1. GitHub에 코드 푸시 (이미 완료됨 ✅)
git push origin main

# 2. GitHub Actions에서 Deploy Dashboard 워크플로우 수동 실행
# https://github.com/Softbank-mango/deplight-platform-v3/actions/workflows/deploy-dashboard.yml
# "Run workflow" 버튼 클릭

# 3. 배포 진행 상황 모니터링
# GitHub Actions 페이지에서 실시간 로그 확인

# 4. 완료! (약 5-10분 소요)
# Dashboard URL: http://delightful-deploy-alb-796875577.ap-northeast-2.elb.amazonaws.com/
```

#### GitHub Actions Workflow
- 파일: `.github/workflows/deploy-dashboard.yml`
- 트리거:
  - `mango/dashboard/` 경로 변경 시 자동
  - 수동 실행 (`workflow_dispatch`)

#### 배포 과정
```
1. ✅ Checkout code
2. ✅ Configure AWS credentials (OIDC)
3. ✅ Login to ECR
4. ✅ Build Docker image (UV + BuildKit)
5. ✅ Push to ECR
6. ✅ Update ECS task definition
7. ✅ Update ECS service
8. ✅ Wait for stability
9. ✅ Health check
```

---

### **방법 2: 로컬에서 수동 배포**

#### 전제조건
- Docker Desktop 실행 중
- AWS CLI 설정 완료
- `.env` 파일 설정

#### 배포 스크립트 실행
```bash
# Dashboard 배포 스크립트
./scripts/deploy_dashboard.sh
```

#### 스크립트 동작
1. ECR 로그인
2. ALB DNS 확인
3. Docker 이미지 빌드 (UV + BuildKit)
4. ECR에 이미지 푸시
5. ECS Task Definition 업데이트
6. ECS 서비스 재시작
7. Health Check

---

### **방법 3: 간단한 재배포 (이미지가 ECR에 있는 경우)**

```bash
# Python 스크립트로 간단 재배포
python3 scripts/deploy_dashboard_simple.py
```

⚠️ **주의**: 현재 ECS 서비스가 CodeDeploy를 사용 중이므로 `forceNewDeployment`가 작동하지 않습니다.

**해결 방법:**
1. Terraform에서 `enable_blue_green_deployment = false`로 설정
2. `terraform apply`로 인프라 업데이트
3. 이후 간단한 재배포 가능

---

## 🏗️ 현재 인프라 설정

### ECS Service 구성
```
Cluster: delightful-deploy-cluster
Service: delightful-deploy-service
Deployment Controller: CODE_DEPLOY (Blue-Green)
Desired Tasks: 2
Current Tasks: 2 running
```

### Task Definition
```
Family: delightful-deploy
CPU: 256
Memory: 512
Container Port: 8000
Health Check: /api/health
```

### ALB
```
Name: delightful-deploy-alb
DNS: delightful-deploy-alb-796875577.ap-northeast-2.elb.amazonaws.com
Port: 80 (HTTP)
Health Check: /health
```

---

## 🔄 배포 전환 (E-Commerce → Dashboard)

현재 E-Commerce API가 실행 중이므로, Dashboard로 전환하려면:

### Option A: CodeDeploy를 사용한 안전한 전환
```bash
# 1. Dashboard Docker 이미지 빌드
cd mango/dashboard
docker build -t 513348493870.dkr.ecr.ap-northeast-2.amazonaws.com/delightful-deploy:dashboard-latest .

# 2. ECR에 푸시
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin 513348493870.dkr.ecr.ap-northeast-2.amazonaws.com
docker push 513348493870.dkr.ecr.ap-northeast-2.amazonaws.com/delightful-deploy:dashboard-latest

# 3. CodeDeploy 배포 생성
aws deploy create-deployment \
  --application-name delightful-deploy-app \
  --deployment-group-name delightful-deploy-dg \
  --deployment-config-name CodeDeployDefault.ECSCanary10Percent5Minutes \
  --description "Deploy Dashboard"
```

### Option B: GitHub Actions 자동 배포 (권장)
```bash
# GitHub에서 workflow 실행
https://github.com/Softbank-mango/deplight-platform-v3/actions
→ Deploy Dashboard
→ Run workflow
```

### Option C: Circuit Breaker로 빠른 배포 (설정 변경 필요)
```bash
# 1. Terraform 설정 변경
# mango/infrastructure/terraform/variables.tf
# enable_blue_green_deployment = false

# 2. Terraform 적용
cd mango/infrastructure/terraform
terraform apply

# 3. 이후 빠른 재배포 가능
python3 ../../scripts/deploy_dashboard_simple.py
```

---

## 📊 대시보드 접속 후 확인 사항

배포 완료 후 다음 URL들을 확인:

### 1. **메인 대시보드**
```
http://delightful-deploy-alb-796875577.ap-northeast-2.elb.amazonaws.com/
```

**예상 화면:**
- Glassmorphism 다크 테마
- 통계 카드 (실행 중인 서비스, 배포 중, 평균 배포 시간, 비용)
- 배포된 서비스 목록 (카드 형태)
- "새 배포" 버튼

### 2. **API Health Check**
```
http://delightful-deploy-alb-796875577.ap-northeast-2.elb.amazonaws.com/api/health
```

**예상 응답:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-07T...",
  "service": "dashboard-api"
}
```

### 3. **서비스 목록 API**
```
http://delightful-deploy-alb-796875577.ap-northeast-2.elb.amazonaws.com/api/services
```

**예상 응답:**
```json
{
  "success": true,
  "count": 1,
  "services": [
    {
      "id": "...",
      "name": "...",
      "framework": "FastAPI",
      "status": "healthy",
      ...
    }
  ]
}
```

---

## 🐛 문제 해결

### 문제 1: CodeDeploy 오류
```
Error: Cannot force a new deployment on services with a CODE_DEPLOY deployment controller
```

**해결책:**
1. Terraform에서 Circuit Breaker로 전환
2. 또는 CodeDeploy API 사용

### 문제 2: Docker 데몬이 실행되지 않음
```
Error: Cannot connect to the Docker daemon
```

**해결책:**
1. Docker Desktop 시작
2. 또는 GitHub Actions 사용 (Docker 불필요)

### 문제 3: ECR 로그인 실패
```
Error: no basic auth credentials
```

**해결책:**
```bash
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin 513348493870.dkr.ecr.ap-northeast-2.amazonaws.com
```

### 문제 4: Health Check 실패
```
Health check failed after 10 attempts
```

**해결책:**
1. ECS Tasks 로그 확인
```bash
python3 mango/scripts/check_ecs_tasks.py
```

2. CloudWatch Logs 확인
```bash
aws logs tail /aws/ecs/delightful-deploy --follow
```

3. Security Group 확인
```bash
# ALB → ECS 통신이 열려있는지 확인
```

---

## 📝 배포 후 TODO

### 즉시
- [ ] Health Check 확인
- [ ] Dashboard UI 접속 확인
- [ ] API 엔드포인트 테스트

### 단기 (1주일)
- [ ] DynamoDB에서 실제 배포 데이터 로드 확인
- [ ] GitHub Actions를 통한 새 배포 테스트
- [ ] 배포 진행 상황 실시간 업데이트 확인

### 중기 (1개월)
- [ ] Multi-Service 아키텍처 구현 (Path-based routing)
- [ ] Custom Domain 설정 (deplight.com)
- [ ] HTTPS/SSL 인증서 적용

---

## 🎯 다음 단계

### 1. **GitHub Actions Secrets 설정**
```
Repository Settings → Secrets and variables → Actions

필요한 Secrets:
- AWS_ROLE_ARN: arn:aws:iam::513348493870:role/github-actions-role
- GITHUB_TOKEN: (자동 생성됨)
```

### 2. **Dashboard 배포 실행**
```bash
# GitHub Actions에서
https://github.com/Softbank-mango/deplight-platform-v3/actions/workflows/deploy-dashboard.yml
→ Run workflow 클릭
```

### 3. **배포 완료 후 접속**
```
http://delightful-deploy-alb-796875577.ap-northeast-2.elb.amazonaws.com/
```

---

## ✅ 요약

1. **v3 코드 GitHub 푸시**: ✅ 완료
   - https://github.com/Softbank-mango/deplight-platform-v3

2. **대시보드 배포 준비**: ✅ 완료
   - Dockerfile 생성
   - GitHub Actions workflow 생성
   - 배포 스크립트 작성

3. **대시보드 배포 실행**: ⏳ 대기 중
   - GitHub Actions에서 수동 실행 필요
   - 또는 로컬에서 `./scripts/deploy_dashboard.sh` 실행

4. **현재 실행 중**: E-Commerce API
   - URL: http://delightful-deploy-alb-796875577.ap-northeast-2.elb.amazonaws.com/
   - Dashboard로 전환하려면 새 배포 필요

---

**🚀 Dashboard를 AWS에서 계속 돌아가도록 하려면:**

1. GitHub Actions에서 `deploy-dashboard.yml` workflow 실행
2. 또는 Docker Desktop 시작 후 `./scripts/deploy_dashboard.sh` 실행
3. 배포 완료 후 URL 접속하여 확인

**모든 준비가 완료되었습니다!** 🎉
