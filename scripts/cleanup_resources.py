#!/usr/bin/env python3
"""
AWS 리소스 정리 스크립트
Terraform과 충돌하는 기존 리소스들을 삭제합니다.
"""

import boto3
import time
import sys
from botocore.exceptions import ClientError

APP_NAME = "delightful-deploy"
AWS_REGION = "ap-northeast-2"

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def print_step(step_num, text):
    print(f"\n{step_num}. {text}")

def delete_xray_sampling_rule():
    """X-Ray Sampling Rule 삭제"""
    print_step("1", "Checking X-Ray Sampling Rule...")

    xray = boto3.client('xray', region_name=AWS_REGION)
    rule_name = f"{APP_NAME}-sampling-rule"

    try:
        response = xray.get_sampling_rules()
        rules = response.get('SamplingRuleRecords', [])

        rule_exists = any(r['SamplingRule']['RuleName'] == rule_name for r in rules)

        if rule_exists:
            print(f"   🗑️  Deleting X-Ray sampling rule: {rule_name}")
            xray.delete_sampling_rule(RuleName=rule_name)
            print(f"   ✅ X-Ray sampling rule deleted")
        else:
            print(f"   ℹ️  X-Ray sampling rule not found")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"   ℹ️  X-Ray sampling rule not found")
        else:
            print(f"   ⚠️  Error: {e}")

def delete_dynamodb_tables():
    """DynamoDB 테이블 삭제"""
    print_step("2", "Checking DynamoDB Tables...")

    dynamodb = boto3.client('dynamodb', region_name=AWS_REGION)

    tables = [
        f"{APP_NAME}-garden-state",
        f"{APP_NAME}-ai-analysis",
        f"{APP_NAME}-deployment-history",
        f"{APP_NAME}-deployment-logs",
    ]

    deleted_tables = []

    for table_name in tables:
        try:
            dynamodb.describe_table(TableName=table_name)
            print(f"   🗑️  Deleting DynamoDB table: {table_name}")
            dynamodb.delete_table(TableName=table_name)
            deleted_tables.append(table_name)
            print(f"   ✅ Table {table_name} deletion initiated")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"   ℹ️  Table {table_name} not found")
            else:
                print(f"   ⚠️  Error deleting {table_name}: {e}")

    # Wait for tables to be deleted
    if deleted_tables:
        print("\n   ⏳ Waiting for tables to be deleted...")
        for table_name in deleted_tables:
            try:
                waiter = dynamodb.get_waiter('table_not_exists')
                print(f"      Waiting for {table_name}...")
                waiter.wait(
                    TableName=table_name,
                    WaiterConfig={'Delay': 5, 'MaxAttempts': 40}
                )
            except Exception as e:
                print(f"      ⚠️  Error waiting for {table_name}: {e}")
        print("   ✅ All DynamoDB tables deleted")

def delete_alb_target_groups():
    """ALB Target Groups 삭제"""
    print_step("3", "Checking ALB Target Groups...")

    elbv2 = boto3.client('elbv2', region_name=AWS_REGION)

    target_groups = [
        f"{APP_NAME}-blue-tg",
        f"{APP_NAME}-green-tg",
        f"{APP_NAME}-dashboard-tg",
    ]

    for tg_name in target_groups:
        try:
            response = elbv2.describe_target_groups(Names=[tg_name])
            if response['TargetGroups']:
                tg_arn = response['TargetGroups'][0]['TargetGroupArn']
                print(f"   🗑️  Deleting target group: {tg_name}")
                elbv2.delete_target_group(TargetGroupArn=tg_arn)
                print(f"   ✅ Target group deleted")
        except ClientError as e:
            if e.response['Error']['Code'] == 'TargetGroupNotFound':
                print(f"   ℹ️  Target group {tg_name} not found")
            else:
                print(f"   ⚠️  Error: {e}")

def delete_lambda_function():
    """Lambda Function 삭제"""
    print_step("4", "Checking Lambda Function...")

    lambda_client = boto3.client('lambda', region_name=AWS_REGION)
    function_name = f"{APP_NAME}-ai-analyzer"

    try:
        lambda_client.get_function(FunctionName=function_name)
        print(f"   🗑️  Deleting Lambda function: {function_name}")
        lambda_client.delete_function(FunctionName=function_name)
        print(f"   ✅ Lambda function deleted")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"   ℹ️  Lambda function not found")
        else:
            print(f"   ⚠️  Error: {e}")

def delete_cloudwatch_query_definitions():
    """CloudWatch Query Definitions 삭제"""
    print_step("5", "Checking CloudWatch Query Definitions...")

    logs = boto3.client('logs', region_name=AWS_REGION)

    query_names = [
        f"{APP_NAME}-deployment-timeline",
        f"{APP_NAME}-performance-analysis",
    ]

    try:
        response = logs.describe_query_definitions()
        existing_queries = response.get('queryDefinitions', [])

        for query_name in query_names:
            matching_queries = [q for q in existing_queries if q['name'] == query_name]
            if matching_queries:
                query_id = matching_queries[0]['queryDefinitionId']
                print(f"   🗑️  Deleting query definition: {query_name}")
                logs.delete_query_definition(queryDefinitionId=query_id)
                print(f"   ✅ Query definition deleted")
            else:
                print(f"   ℹ️  Query definition {query_name} not found")
    except ClientError as e:
        print(f"   ⚠️  Error: {e}")

def delete_cloudwatch_log_groups():
    """CloudWatch Log Group 삭제"""
    print_step("6", "Checking CloudWatch Log Groups...")

    logs = boto3.client('logs', region_name=AWS_REGION)

    log_groups = [
        f"/aws/ecs/{APP_NAME}-dashboard",
        f"/aws/ecs/{APP_NAME}",
        f"/aws/lambda/{APP_NAME}-ai-analyzer",
    ]

    for log_group_name in log_groups:
        try:
            response = logs.describe_log_groups(
                logGroupNamePrefix=log_group_name,
                limit=1
            )

            if response['logGroups']:
                # Check exact match
                if any(lg['logGroupName'] == log_group_name for lg in response['logGroups']):
                    print(f"   🗑️  Deleting log group: {log_group_name}")
                    logs.delete_log_group(logGroupName=log_group_name)
                    print(f"   ✅ Log group deleted")
                else:
                    print(f"   ℹ️  Log group {log_group_name} not found")
            else:
                print(f"   ℹ️  Log group {log_group_name} not found")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"   ℹ️  Log group {log_group_name} not found")
            else:
                print(f"   ⚠️  Error: {e}")

def main():
    print_header("AWS Resources Cleanup")
    print(f"App: {APP_NAME}")
    print(f"Region: {AWS_REGION}")

    # Confirm deletion
    print("\n⚠️  WARNING: This will delete the following resources:")
    print("   • X-Ray sampling rule")
    print("   • 4 DynamoDB tables (ALL DATA WILL BE LOST)")
    print("   • 3 ALB Target Groups")
    print("   • 1 Lambda function")
    print("   • 2 CloudWatch Query Definitions")
    print("   • 3 CloudWatch log groups")
    print("\nType 'DELETE' to confirm: ", end='')

    confirmation = input().strip()

    if confirmation != 'DELETE':
        print("\n❌ Deletion cancelled")
        sys.exit(0)

    print("\n✅ Confirmation received, proceeding with deletion...")

    try:
        # Delete resources in order
        delete_xray_sampling_rule()
        delete_dynamodb_tables()
        delete_alb_target_groups()
        delete_lambda_function()
        delete_cloudwatch_query_definitions()
        delete_cloudwatch_log_groups()

        # Summary
        print_header("Cleanup Completed Successfully! 🎉")
        print("Deleted resources:")
        print(f"  • X-Ray sampling rule: {APP_NAME}-sampling-rule")
        print("  • DynamoDB tables (4):")
        print(f"    - {APP_NAME}-garden-state")
        print(f"    - {APP_NAME}-ai-analysis")
        print(f"    - {APP_NAME}-deployment-history")
        print(f"    - {APP_NAME}-deployment-logs")
        print("  • ALB Target Groups (3):")
        print(f"    - {APP_NAME}-blue-tg")
        print(f"    - {APP_NAME}-green-tg")
        print(f"    - {APP_NAME}-dashboard-tg")
        print(f"  • Lambda function:")
        print(f"    - {APP_NAME}-ai-analyzer")
        print("  • CloudWatch Query Definitions (2):")
        print(f"    - {APP_NAME}-deployment-timeline")
        print(f"    - {APP_NAME}-performance-analysis")
        print("  • CloudWatch log groups (3):")
        print(f"    - /aws/ecs/{APP_NAME}")
        print(f"    - /aws/ecs/{APP_NAME}-dashboard")
        print(f"    - /aws/lambda/{APP_NAME}-ai-analyzer")
        print("\nNext step: Run Terraform apply")
        print("  https://github.com/Softbank-mango/deplight-platform-v3/actions")

    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
