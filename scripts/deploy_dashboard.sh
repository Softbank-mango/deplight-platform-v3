#!/bin/bash

# Deplight Dashboard 배포 스크립트
# AWS ECS Fargate에 대시보드를 배포합니다

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🚀 Deplight Dashboard 배포 시작${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 프로젝트 루트 디렉토리
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# .env 파일 로드
ENV_FILE="$PROJECT_ROOT/.env"
if [ -f "$ENV_FILE" ]; then
    echo -e "${GREEN}✓ Loading .env file${NC}"
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    echo -e "${RED}✗ .env file not found at $ENV_FILE${NC}"
    exit 1
fi

# 필수 환경변수 확인
if [ -z "$AWS_REGION" ] || [ -z "$ECR_REPOSITORY" ]; then
    echo -e "${RED}✗ Required environment variables not set${NC}"
    echo "Required: AWS_REGION, ECR_REPOSITORY"
    exit 1
fi

# AWS 계정 ID 가져오기
echo -e "${YELLOW}⏳ Getting AWS account ID...${NC}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "${GREEN}✓ AWS Account ID: $AWS_ACCOUNT_ID${NC}"

# ECR Repository URI
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
ECR_REPO_URI="${ECR_REGISTRY}/${ECR_REPOSITORY}"

echo ""
echo -e "${BLUE}📦 Configuration:${NC}"
echo -e "  Region: ${AWS_REGION}"
echo -e "  ECR: ${ECR_REPO_URI}"
echo -e "  Cluster: delightful-deploy-cluster"
echo -e "  Service: delightful-deploy-service"
echo ""

# Step 1: ECR 로그인
echo -e "${YELLOW}⏳ Step 1/6: Logging in to ECR...${NC}"
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
echo -e "${GREEN}✓ ECR login successful${NC}"
echo ""

# Step 2: ALB DNS 가져오기
echo -e "${YELLOW}⏳ Step 2/6: Getting ALB DNS...${NC}"
ALB_DNS=$(aws elbv2 describe-load-balancers \
    --names delightful-deploy-alb \
    --region ${AWS_REGION} \
    --query 'LoadBalancers[0].DNSName' \
    --output text)
echo -e "${GREEN}✓ ALB DNS: ${ALB_DNS}${NC}"
echo ""

# Step 3: Docker 이미지 빌드
echo -e "${YELLOW}⏳ Step 3/6: Building Docker image...${NC}"
DASHBOARD_DIR="$PROJECT_ROOT/mango/dashboard"
IMAGE_TAG="dashboard-$(git rev-parse --short HEAD)"

cd "$DASHBOARD_DIR"

docker build \
    --build-arg PORT=8000 \
    --build-arg AWS_REGION=${AWS_REGION} \
    --build-arg ALB_DNS=${ALB_DNS} \
    -t ${ECR_REPO_URI}:${IMAGE_TAG} \
    -t ${ECR_REPO_URI}:dashboard-latest \
    .

echo -e "${GREEN}✓ Docker image built: ${IMAGE_TAG}${NC}"
echo ""

# Step 4: ECR에 푸시
echo -e "${YELLOW}⏳ Step 4/6: Pushing to ECR...${NC}"
docker push ${ECR_REPO_URI}:${IMAGE_TAG}
docker push ${ECR_REPO_URI}:dashboard-latest
echo -e "${GREEN}✓ Image pushed to ECR${NC}"
echo ""

# Step 5: 현재 Task Definition 가져오기 및 업데이트
echo -e "${YELLOW}⏳ Step 5/6: Updating ECS Task Definition...${NC}"

TASK_DEF_ARN=$(aws ecs describe-services \
    --cluster delightful-deploy-cluster \
    --services delightful-deploy-service \
    --region ${AWS_REGION} \
    --query 'services[0].taskDefinition' \
    --output text)

echo "Current task definition: $TASK_DEF_ARN"

# Task Definition 다운로드 및 정리
aws ecs describe-task-definition \
    --task-definition ${TASK_DEF_ARN} \
    --region ${AWS_REGION} \
    --query 'taskDefinition' > /tmp/task-def.json

cat /tmp/task-def.json | jq 'del(.taskDefinitionArn, .revision, .status, .requiresAttributes, .compatibilities, .registeredAt, .registeredBy)' > /tmp/task-def-clean.json

# 이미지 업데이트
NEW_IMAGE="${ECR_REPO_URI}:${IMAGE_TAG}"
cat /tmp/task-def-clean.json | jq \
    --arg IMAGE "$NEW_IMAGE" \
    '.containerDefinitions[0].image = $IMAGE' > /tmp/task-def-updated.json

# 새 Task Definition 등록
NEW_TASK_DEF_ARN=$(aws ecs register-task-definition \
    --cli-input-json file:///tmp/task-def-updated.json \
    --region ${AWS_REGION} \
    --query 'taskDefinition.taskDefinitionArn' \
    --output text)

echo -e "${GREEN}✓ New task definition registered: ${NEW_TASK_DEF_ARN}${NC}"
echo ""

# Step 6: ECS 서비스 업데이트
echo -e "${YELLOW}⏳ Step 6/6: Updating ECS service...${NC}"
aws ecs update-service \
    --cluster delightful-deploy-cluster \
    --service delightful-deploy-service \
    --task-definition ${NEW_TASK_DEF_ARN} \
    --force-new-deployment \
    --region ${AWS_REGION} \
    > /dev/null

echo -e "${GREEN}✓ ECS service update initiated${NC}"
echo ""

# 서비스 안정화 대기
echo -e "${YELLOW}⏳ Waiting for service to stabilize...${NC}"
aws ecs wait services-stable \
    --cluster delightful-deploy-cluster \
    --services delightful-deploy-service \
    --region ${AWS_REGION}

echo -e "${GREEN}✓ Service is stable!${NC}"
echo ""

# Health Check
echo -e "${YELLOW}⏳ Performing health check...${NC}"
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://${ALB_DNS}/api/health" --max-time 10 || echo "000")

    if [ "$HTTP_CODE" == "200" ]; then
        echo -e "${GREEN}✓ Health check passed! (HTTP $HTTP_CODE)${NC}"
        break
    fi

    echo "  Attempt $((RETRY_COUNT + 1))/$MAX_RETRIES - HTTP $HTTP_CODE, retrying..."
    RETRY_COUNT=$((RETRY_COUNT + 1))
    sleep 5
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}✗ Health check failed after $MAX_RETRIES attempts${NC}"
    exit 1
fi

# 완료
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Dashboard deployment successful!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📍 Dashboard URL:${NC}"
echo -e "   ${GREEN}http://${ALB_DNS}/${NC}"
echo ""
echo -e "${BLUE}🔍 API Health:${NC}"
echo -e "   ${GREEN}http://${ALB_DNS}/api/health${NC}"
echo ""
echo -e "${BLUE}📦 Image:${NC}"
echo -e "   ${ECR_REPO_URI}:${IMAGE_TAG}"
echo ""
echo -e "${BLUE}📝 Task Definition:${NC}"
echo -e "   ${NEW_TASK_DEF_ARN}"
echo ""

# 정리
rm -f /tmp/task-def*.json

echo -e "${BLUE}🎉 Done!${NC}"
