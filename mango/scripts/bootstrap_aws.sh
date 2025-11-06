#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load environment variables from .env file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"

if [ -f "$ENV_FILE" ]; then
  echo -e "${GREEN}Loading configuration from .env file...${NC}"
  export $(grep -v '^#' "$ENV_FILE" | xargs)
else
  echo -e "${RED}Error: .env file not found at $ENV_FILE${NC}"
  echo -e "${YELLOW}Please create .env file from .env.example${NC}"
  exit 1
fi

# Configuration (loaded from .env)
REGION="${AWS_REGION:-ap-northeast-2}"
S3_BUCKET="${S3_ARTIFACTS_BUCKET:-delightful-deploy-artifacts-1762083190}"
ECR_REPO="${ECR_REPOSITORY:-delightful-deploy}"
LETSUR_API_KEY="${LETSUR_API_KEY}"
SSM_PARAM_NAME="${SSM_LETSUR_API_KEY:-/delightful/letsur/api_key}"

# Validate required environment variables
if [ -z "$LETSUR_API_KEY" ]; then
  echo -e "${RED}Error: LETSUR_API_KEY is not set in .env file${NC}"
  exit 1
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Delightful Deploy - AWS Bootstrap${NC}"
echo -e "${GREEN}========================================${NC}"

# 1. Create S3 Bucket
echo -e "\n${YELLOW}📦 Creating S3 bucket...${NC}"
aws s3 mb s3://${S3_BUCKET} --region ${REGION} 2>/dev/null || echo "  ℹ️  Bucket already exists or error"
aws s3api put-bucket-versioning \
  --bucket ${S3_BUCKET} \
  --versioning-configuration Status=Enabled \
  --region ${REGION} 2>/dev/null || true
echo -e "${GREEN}  ✅ S3 bucket ready: ${S3_BUCKET}${NC}"

# 2. Create ECR Repository
echo -e "\n${YELLOW}🐳 Creating ECR repository...${NC}"
aws ecr create-repository \
  --repository-name ${ECR_REPO} \
  --region ${REGION} \
  --image-scanning-configuration scanOnPush=true 2>/dev/null || echo "  ℹ️  Repository already exists or error"
echo -e "${GREEN}  ✅ ECR repository ready: ${ECR_REPO}${NC}"

# 3. Create SSM Parameter for Letsur API Key
echo -e "\n${YELLOW}🔑 Creating SSM parameter for Letsur API key...${NC}"
aws ssm put-parameter \
  --name ${SSM_PARAM_NAME} \
  --value ${LETSUR_API_KEY} \
  --type SecureString \
  --region ${REGION} \
  --overwrite 2>/dev/null || true
echo -e "${GREEN}  ✅ SSM parameter created: ${SSM_PARAM_NAME}${NC}"

# 4. Get VPC and Subnet information
echo -e "\n${YELLOW}🌐 Getting VPC and subnet information...${NC}"
VPC_ID=$(aws ec2 describe-vpcs \
  --region ${REGION} \
  --filters "Name=isDefault,Values=true" \
  --query 'Vpcs[0].VpcId' \
  --output text)

if [ "$VPC_ID" == "None" ] || [ -z "$VPC_ID" ]; then
  VPC_ID=$(aws ec2 describe-vpcs \
    --region ${REGION} \
    --query 'Vpcs[0].VpcId' \
    --output text)
fi

PUBLIC_SUBNETS=$(aws ec2 describe-subnets \
  --region ${REGION} \
  --filters "Name=vpc-id,Values=${VPC_ID}" "Name=map-public-ip-on-launch,Values=true" \
  --query 'Subnets[*].SubnetId' \
  --output text | tr '\t' ',')

if [ -z "$PUBLIC_SUBNETS" ]; then
  # If no public subnets found, use all subnets
  PUBLIC_SUBNETS=$(aws ec2 describe-subnets \
    --region ${REGION} \
    --filters "Name=vpc-id,Values=${VPC_ID}" \
    --query 'Subnets[*].SubnetId' \
    --output text | tr '\t' ',')
fi

echo -e "${GREEN}  ✅ VPC ID: ${VPC_ID}${NC}"
echo -e "${GREEN}  ✅ Subnets: ${PUBLIC_SUBNETS}${NC}"

# Save to environment file
cat > /tmp/aws_env.sh << EOF
export AWS_REGION="${REGION}"
export VPC_ID="${VPC_ID}"
export PUBLIC_SUBNETS="${PUBLIC_SUBNETS}"
export S3_BUCKET="${S3_BUCKET}"
export ECR_REPO="${ECR_REPO}"
export ECR_REPO_URI="$(aws sts get-caller-identity --query Account --output text).dkr.ecr.${REGION}.amazonaws.com/${ECR_REPO}"
EOF

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Bootstrap Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\nEnvironment variables saved to: ${YELLOW}/tmp/aws_env.sh${NC}"
echo -e "Source it with: ${YELLOW}source /tmp/aws_env.sh${NC}"
