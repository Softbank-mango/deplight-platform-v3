#!/bin/bash
# Terraform import script for existing AWS resources

set -e

TERRAFORM_DIR="/Users/jaeseokhan/Desktop/Work/softbank/deplight-platform/mango/infrastructure/terraform"
APP_NAME="delightful-deploy"
AWS_REGION="ap-northeast-2"
AWS_ACCOUNT_ID="513348493870"

echo "=================================================="
echo "  Terraform Import - Existing Resources"
echo "=================================================="
echo ""

cd "$TERRAFORM_DIR"

# Initialize if needed
if [ ! -d ".terraform" ]; then
    echo "Initializing Terraform..."
    terraform init
fi

echo ""
echo "Starting import process..."
echo ""

# Function to import resource safely
import_resource() {
    local tf_resource=$1
    local aws_resource=$2
    local description=$3

    echo "📥 Importing: $description"
    echo "   Terraform: $tf_resource"
    echo "   AWS: $aws_resource"

    if terraform import "$tf_resource" "$aws_resource" 2>&1; then
        echo "   ✅ Imported successfully"
    else
        echo "   ⚠️  Import failed (may already be in state or not exist)"
    fi
    echo ""
}

# 1. DynamoDB Tables
echo "1. Importing DynamoDB Tables..."
import_resource "aws_dynamodb_table.garden_state" \
    "${APP_NAME}-garden-state" \
    "Garden State Table"

import_resource "aws_dynamodb_table.ai_analysis" \
    "${APP_NAME}-ai-analysis" \
    "AI Analysis Table"

import_resource "aws_dynamodb_table.deployment_history" \
    "${APP_NAME}-deployment-history" \
    "Deployment History Table"

import_resource "aws_dynamodb_table.deployment_logs" \
    "${APP_NAME}-deployment-logs" \
    "Deployment Logs Table"

# 2. ALB Target Groups
echo "2. Importing ALB Target Groups..."
import_resource "aws_lb_target_group.blue" \
    "arn:aws:elasticloadbalancing:${AWS_REGION}:${AWS_ACCOUNT_ID}:targetgroup/${APP_NAME}-blue-tg/c951c82292c0e78d" \
    "Blue Target Group"

import_resource "aws_lb_target_group.green" \
    "arn:aws:elasticloadbalancing:${AWS_REGION}:${AWS_ACCOUNT_ID}:targetgroup/${APP_NAME}-green-tg/f86d9c95113cc641" \
    "Green Target Group"

import_resource "aws_lb_target_group.dashboard" \
    "arn:aws:elasticloadbalancing:${AWS_REGION}:${AWS_ACCOUNT_ID}:targetgroup/${APP_NAME}-dashboard-tg/XXXXXX" \
    "Dashboard Target Group"

# 3. Lambda Function
echo "3. Importing Lambda Function..."
import_resource "aws_lambda_function.ai_analyzer" \
    "${APP_NAME}-ai-analyzer" \
    "AI Analyzer Lambda"

# 4. CloudWatch Log Groups
echo "4. Importing CloudWatch Log Groups..."
import_resource "aws_cloudwatch_log_group.dashboard" \
    "/aws/ecs/${APP_NAME}-dashboard" \
    "Dashboard Log Group"

import_resource "aws_cloudwatch_log_group.lambda_analyzer" \
    "/aws/lambda/${APP_NAME}-ai-analyzer" \
    "Lambda Analyzer Log Group"

# 5. X-Ray Sampling Rule
echo "5. Importing X-Ray Sampling Rule..."
import_resource "aws_xray_sampling_rule.main[0]" \
    "${APP_NAME}-sampling-rule" \
    "X-Ray Sampling Rule"

# 6. CloudWatch Query Definitions
echo "6. Importing CloudWatch Query Definitions..."
# Note: Query definitions need their ID, which we'll get dynamically
TIMELINE_QUERY_ID=$(aws logs describe-query-definitions --region ${AWS_REGION} --query "queryDefinitions[?name=='${APP_NAME}-deployment-timeline'].queryDefinitionId" --output text 2>/dev/null || echo "")
if [ -n "$TIMELINE_QUERY_ID" ]; then
    import_resource "aws_cloudwatch_query_definition.deployment_timeline" \
        "$TIMELINE_QUERY_ID" \
        "Deployment Timeline Query"
fi

PERFORMANCE_QUERY_ID=$(aws logs describe-query-definitions --region ${AWS_REGION} --query "queryDefinitions[?name=='${APP_NAME}-performance-analysis'].queryDefinitionId" --output text 2>/dev/null || echo "")
if [ -n "$PERFORMANCE_QUERY_ID" ]; then
    import_resource "aws_cloudwatch_query_definition.performance_analysis" \
        "$PERFORMANCE_QUERY_ID" \
        "Performance Analysis Query"
fi

echo "=================================================="
echo "  Import completed!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Run: terraform plan"
echo "2. Verify no unexpected changes"
echo "3. Run: terraform apply (should show minimal changes)"
echo ""
echo "Or run via GitHub Actions:"
echo "  https://github.com/Softbank-mango/deplight-platform-v3/actions"
