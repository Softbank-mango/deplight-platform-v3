#!/bin/bash
# Mango Dashboard Startup Script

cd "$(dirname "$0")"

echo "🚀 Starting Mango Dashboard..."

# Set environment variables
export AWS_REGION=ap-northeast-2
export ECR_REGISTRY=513348493870.dkr.ecr.ap-northeast-2.amazonaws.com
export ECR_REPOSITORY=delightful-deploy
export ECS_CLUSTER=delightful-deploy-cluster
export ECS_SERVICE=delightful-deploy-service
export S3_BUCKET=delightful-deploy-artifacts-1762083190
export AI_ANALYZER_LAMBDA=delightful-deploy-ai-analyzer
export ALB_DNS=delightful-deploy-alb-796875577.ap-northeast-2.elb.amazonaws.com

# Activate venv (use local first, then backup)
if [ -d "venv" ]; then
    echo "📦 Using local venv..."
    source venv/bin/activate
elif [ -d "../.backup_old_structure/app/venv" ]; then
    echo "📦 Using backup venv..."
    source ../.backup_old_structure/app/venv/bin/activate
fi

# Start the dashboard
cd dashboard/api
python3 main.py
