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

def delete_cloudwatch_log_groups():
    """CloudWatch Log Group 삭제"""
    print_step("3", "Checking CloudWatch Log Groups...")

    logs = boto3.client('logs', region_name=AWS_REGION)

    log_groups = [
        f"/aws/ecs/{APP_NAME}-dashboard",
        f"/aws/ecs/{APP_NAME}",
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
    print("   • 2 CloudWatch log groups")
    print("\nType 'DELETE' to confirm: ", end='')

    confirmation = input().strip()

    if confirmation != 'DELETE':
        print("\n❌ Deletion cancelled")
        sys.exit(0)

    print("\n✅ Confirmation received, proceeding with deletion...")

    try:
        # Delete resources
        delete_xray_sampling_rule()
        delete_dynamodb_tables()
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
        print("  • CloudWatch log groups (2):")
        print(f"    - /aws/ecs/{APP_NAME}")
        print(f"    - /aws/ecs/{APP_NAME}-dashboard")
        print("\nNext step: Run Terraform apply")
        print("  https://github.com/Softbank-mango/deplight-platform-v3/actions")

    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
