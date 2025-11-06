#!/usr/bin/env bash
set -euo pipefail

AWS_REGION=${AWS_REGION:-ap-northeast-2}
export AWS_REGION

STACKS=(delightful-pipeline-dev delightful-analyzer-dev delightful-ecs-dev)

echo "[teardown] deleting stacks: ${STACKS[*]}"
for s in "${STACKS[@]}"; do
  if aws cloudformation describe-stacks --stack-name "$s" >/dev/null 2>&1; then
    aws cloudformation delete-stack --stack-name "$s"
    echo "[wait] $s"
    aws cloudformation wait stack-delete-complete --stack-name "$s" || true
  fi
done

echo "[optional] delete artifacts bucket (set ARTIFACT_BUCKET to enable)"
if [[ -n "${ARTIFACT_BUCKET:-}" ]]; then
  aws s3 rm "s3://$ARTIFACT_BUCKET" --recursive || true
  aws s3 rb "s3://$ARTIFACT_BUCKET" --force || true
fi

if [[ -n "${ECR_REPO_NAME:-}" ]]; then
  echo "[optional] purge ECR images for $ECR_REPO_NAME"
  IDS=$(aws ecr list-images --repository-name "$ECR_REPO_NAME" --query 'imageIds' --output json || echo '[]')
  if [[ "$IDS" != "[]" ]]; then
    aws ecr batch-delete-image --repository-name "$ECR_REPO_NAME" --image-ids "$IDS" || true
  fi
  if [[ "${DELETE_ECR_REPO:-false}" == "true" ]]; then
    aws ecr delete-repository --repository-name "$ECR_REPO_NAME" --force || true
  fi
fi

echo "[done] teardown complete"

