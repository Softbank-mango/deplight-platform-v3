#!/usr/bin/env bash
set -euo pipefail

# Bootstrap dev environment: ECS+ALB Blue/Green, Pipeline, Analyzer Lambda
# Prereqs: awscli v2, jq, zip; AWS_PROFILE/REGION configured; VPC/Subnets/ECR exist

echo "[bootstrap] starting dev bootstrap"

AWS_REGION=${AWS_REGION:-ap-northeast-2}
export AWS_REGION

STACK_APP=${STACK_APP:-delightful-ecs-dev}
STACK_PIPE=${STACK_PIPE:-delightful-pipeline-dev}
STACK_ANZ=${STACK_ANZ:-delightful-analyzer-dev}

# Required env
: "${VPC_ID:?set VPC_ID}"
: "${PUBLIC_SUBNETS:?set PUBLIC_SUBNETS as comma separated}"
: "${PRIVATE_SUBNETS:?set PRIVATE_SUBNETS as comma separated}"
: "${ECR_REPO_URI:?set ECR_REPO_URI (account.dkr.ecr.region.amazonaws.com/repo)}"

APP_NAME=${APP_NAME:-delightful-dev}
CONTAINER_PORT=${CONTAINER_PORT:-8000}
CODECOMMIT_REPO=${CODECOMMIT_REPO:-delightful-repo}
ECR_REPO_NAME=${ECR_REPO_NAME:-delightful-repo}

TAGS=(Project=DelightfulDeploy Env=dev)

echo "[1/3] Deploy ECS+ALB Blue/Green stack: $STACK_APP"
aws cloudformation deploy \
  --stack-name "$STACK_APP" \
  --template-file infra/cloudformation/ecs_alb_bluegreen.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    AppName="$APP_NAME" \
    VpcId="$VPC_ID" \
    PublicSubnets="$PUBLIC_SUBNETS" \
    PrivateSubnets="$PRIVATE_SUBNETS" \
    ContainerPort="$CONTAINER_PORT" \
    EcrRepositoryUri="$ECR_REPO_URI" \
  $(printf -- '--tags %s ' "${TAGS[@]}")

echo "[outputs] $STACK_APP"
aws cloudformation describe-stacks --stack-name "$STACK_APP" \
  --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' --output table

CLUSTER_NAME=$(aws cloudformation describe-stacks --stack-name "$STACK_APP" --query 'Stacks[0].Outputs[?OutputKey==`ClusterName`].OutputValue' --output text)
SERVICE_NAME=$(aws cloudformation describe-stacks --stack-name "$STACK_APP" --query 'Stacks[0].Outputs[?OutputKey==`ServiceName`].OutputValue' --output text)
TG_BLUE_ARN=$(aws cloudformation describe-stacks --stack-name "$STACK_APP" --query 'Stacks[0].Outputs[?OutputKey==`TargetGroupBlueArn`].OutputValue' --output text)
TG_GREEN_ARN=$(aws cloudformation describe-stacks --stack-name "$STACK_APP" --query 'Stacks[0].Outputs[?OutputKey==`TargetGroupGreenArn`].OutputValue' --output text)
LISTENER_PROD_ARN=$(aws cloudformation describe-stacks --stack-name "$STACK_APP" --query 'Stacks[0].Outputs[?OutputKey==`ListenerProdArn`].OutputValue' --output text)
LISTENER_TEST_ARN=$(aws cloudformation describe-stacks --stack-name "$STACK_APP" --query 'Stacks[0].Outputs[?OutputKey==`ListenerTestArn`].OutputValue' --output text)

echo "[2/3] Deploy Pipeline bootstrap: $STACK_PIPE"
aws cloudformation deploy \
  --stack-name "$STACK_PIPE" \
  --template-file infra/cloudformation/codedeploy_pipeline_bootstrap_codecommit.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    AppName="$APP_NAME" \
    CodeCommitRepositoryName="$CODECOMMIT_REPO" \
    EcrRepositoryName="$ECR_REPO_NAME" \
    ClusterName="$CLUSTER_NAME" \
    ServiceName="$SERVICE_NAME" \
    TargetGroupBlueArn="$TG_BLUE_ARN" \
    TargetGroupGreenArn="$TG_GREEN_ARN" \
    ListenerProdArn="$LISTENER_PROD_ARN" \
    ListenerTestArn="$LISTENER_TEST_ARN" \
    BranchName=main \
  $(printf -- '--tags %s ' "${TAGS[@]}")

echo "[outputs] $STACK_PIPE"
aws cloudformation describe-stacks --stack-name "$STACK_PIPE" \
  --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' --output table

echo "[3/3] Deploy Analyzer (EventBridge -> Lambda) stack: $STACK_ANZ"
ZIP_PATH=${ZIP_PATH:-build/ai_analyzer.zip}
S3_BUCKET=${S3_BUCKET:?set S3_BUCKET for lambda code}
S3_KEY=${S3_KEY:-build/ai_analyzer.zip}

./scripts/package_lambda.sh lambda/ai_code_analyzer "$ZIP_PATH"
aws s3 cp "$ZIP_PATH" "s3://$S3_BUCKET/$S3_KEY"

aws cloudformation deploy \
  --stack-name "$STACK_ANZ" \
  --template-file infra/cloudformation/eventbridge_lambda.yaml \
  --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
  --parameter-overrides \
    AppName="$APP_NAME" \
    LambdaS3Bucket="$S3_BUCKET" \
    LambdaS3Key="$S3_KEY" \
    LetsurApiKeyParam=/delightful/letsur/api_key \
  $(printf -- '--tags %s ' "${TAGS[@]}")

echo "[done] bootstrap complete"

