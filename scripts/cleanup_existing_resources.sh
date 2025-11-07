#!/bin/bash
# Script to cleanup existing AWS resources that conflict with Terraform

set -e

APP_NAME="delightful-deploy"
AWS_REGION="ap-northeast-2"

echo "=================================================="
echo "  Cleaning up existing AWS resources"
echo "  App: ${APP_NAME}"
echo "  Region: ${AWS_REGION}"
echo "=================================================="
echo ""

# Function to check if resource exists
resource_exists() {
    local check_command="$1"
    if eval "$check_command" &>/dev/null; then
        return 0
    else
        return 1
    fi
}

# 1. Delete X-Ray Sampling Rule
echo "1. Checking X-Ray Sampling Rule..."
XRAY_RULE_NAME="${APP_NAME}-sampling-rule"
if aws xray get-sampling-rules --region ${AWS_REGION} 2>/dev/null | grep -q "${XRAY_RULE_NAME}"; then
    echo "   Deleting X-Ray sampling rule: ${XRAY_RULE_NAME}"
    aws xray delete-sampling-rule \
        --rule-name "${XRAY_RULE_NAME}" \
        --region ${AWS_REGION} || echo "   ⚠️  Failed to delete X-Ray sampling rule (may not exist)"
    echo "   ✅ X-Ray sampling rule deleted"
else
    echo "   ℹ️  X-Ray sampling rule not found, skipping"
fi
echo ""

# 2. Delete DynamoDB Tables
echo "2. Checking DynamoDB Tables..."
DYNAMODB_TABLES=(
    "${APP_NAME}-garden-state"
    "${APP_NAME}-ai-analysis"
    "${APP_NAME}-deployment-history"
    "${APP_NAME}-deployment-logs"
)

for TABLE_NAME in "${DYNAMODB_TABLES[@]}"; do
    if aws dynamodb describe-table --table-name "${TABLE_NAME}" --region ${AWS_REGION} &>/dev/null; then
        echo "   Deleting DynamoDB table: ${TABLE_NAME}"
        aws dynamodb delete-table \
            --table-name "${TABLE_NAME}" \
            --region ${AWS_REGION}
        echo "   ✅ Table ${TABLE_NAME} deletion initiated"
    else
        echo "   ℹ️  Table ${TABLE_NAME} not found, skipping"
    fi
done

# Wait for DynamoDB tables to be deleted
echo ""
echo "   Waiting for DynamoDB tables to be deleted..."
for TABLE_NAME in "${DYNAMODB_TABLES[@]}"; do
    if aws dynamodb describe-table --table-name "${TABLE_NAME}" --region ${AWS_REGION} &>/dev/null; then
        echo "   Waiting for ${TABLE_NAME}..."
        aws dynamodb wait table-not-exists \
            --table-name "${TABLE_NAME}" \
            --region ${AWS_REGION} 2>/dev/null || echo "   (table already deleted)"
    fi
done
echo "   ✅ All DynamoDB tables deleted"
echo ""

# 3. Delete CloudWatch Log Group
echo "3. Checking CloudWatch Log Groups..."
LOG_GROUP="/aws/ecs/${APP_NAME}-dashboard"
if aws logs describe-log-groups \
    --log-group-name-prefix "${LOG_GROUP}" \
    --region ${AWS_REGION} 2>/dev/null | grep -q "${LOG_GROUP}"; then
    echo "   Deleting CloudWatch log group: ${LOG_GROUP}"
    aws logs delete-log-group \
        --log-group-name "${LOG_GROUP}" \
        --region ${AWS_REGION}
    echo "   ✅ Log group deleted"
else
    echo "   ℹ️  Log group ${LOG_GROUP} not found, skipping"
fi
echo ""

# Also check for main app log group
LOG_GROUP_MAIN="/aws/ecs/${APP_NAME}"
if aws logs describe-log-groups \
    --log-group-name-prefix "${LOG_GROUP_MAIN}" \
    --region ${AWS_REGION} 2>/dev/null | grep -q "\"${LOG_GROUP_MAIN}\""; then
    echo "   Found additional log group: ${LOG_GROUP_MAIN}"
    read -p "   Delete this log group too? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        aws logs delete-log-group \
            --log-group-name "${LOG_GROUP_MAIN}" \
            --region ${AWS_REGION}
        echo "   ✅ Log group deleted"
    else
        echo "   ⏭️  Skipping ${LOG_GROUP_MAIN}"
    fi
fi
echo ""

echo "=================================================="
echo "  Cleanup completed!"
echo "=================================================="
echo ""
echo "You can now run Terraform apply:"
echo "  cd mango/infrastructure/terraform"
echo "  terraform init"
echo "  terraform plan"
echo "  terraform apply"
echo ""
echo "Or trigger the GitHub Actions workflow:"
echo "  https://github.com/Softbank-mango/deplight-platform-v3/actions"
