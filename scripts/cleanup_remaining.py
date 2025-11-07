#!/usr/bin/env python3
"""
남은 충돌 리소스 정리
"""

import boto3
import sys
from botocore.exceptions import ClientError

APP_NAME = "delightful-deploy"
AWS_REGION = "ap-northeast-2"

def main():
    print("=" * 60)
    print("  Cleanup Remaining Resources")
    print("=" * 60)
    print()

    # 1. Delete error-analysis query definition
    print("1. Deleting error-analysis Query Definition...")
    logs = boto3.client('logs', region_name=AWS_REGION)

    try:
        response = logs.describe_query_definitions()
        queries = response.get('queryDefinitions', [])

        error_query = next((q for q in queries if q['name'] == f"{APP_NAME}-error-analysis"), None)
        if error_query:
            query_id = error_query['queryDefinitionId']
            print(f"   🗑️  Deleting: {APP_NAME}-error-analysis")
            logs.delete_query_definition(queryDefinitionId=query_id)
            print(f"   ✅ Deleted")
        else:
            print(f"   ℹ️  Not found")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")

    # 2. Check and optionally delete ALB
    print("\n2. Checking ALB...")
    elbv2 = boto3.client('elbv2', region_name=AWS_REGION)

    try:
        response = elbv2.describe_load_balancers(Names=[f"{APP_NAME}-alb"])
        if response['LoadBalancers']:
            alb = response['LoadBalancers'][0]
            print(f"   Found ALB: {alb['LoadBalancerName']}")
            print(f"   DNS: {alb['DNSName']}")
            print(f"   State: {alb['State']['Code']}")

            print("\n   ⚠️  ALB already exists!")
            print("   Options:")
            print("   1. Delete and recreate (DOWNTIME)")
            print("   2. Import into Terraform (recommended)")
            print("   3. Skip (will cause Terraform error)")
            print("\n   Type 'DELETE' to delete ALB or anything else to skip: ", end='')

            choice = input().strip()

            if choice == 'DELETE':
                alb_arn = alb['LoadBalancerArn']

                # First, delete listeners
                print("\n   Deleting listeners...")
                listeners = elbv2.describe_listeners(LoadBalancerArn=alb_arn)
                for listener in listeners['Listeners']:
                    print(f"      Deleting listener on port {listener['Port']}...")
                    elbv2.delete_listener(ListenerArn=listener['ListenerArn'])

                # Delete ALB
                print(f"\n   🗑️  Deleting ALB...")
                elbv2.delete_load_balancer(LoadBalancerArn=alb_arn)
                print(f"   ✅ ALB deletion initiated (will take a few minutes)")

                # Delete target groups
                print("\n   Waiting 10 seconds before deleting target groups...")
                import time
                time.sleep(10)

                tg_names = [f"{APP_NAME}-blue-tg", f"{APP_NAME}-green-tg", f"{APP_NAME}-dashboard-tg"]
                for tg_name in tg_names:
                    try:
                        tg_response = elbv2.describe_target_groups(Names=[tg_name])
                        if tg_response['TargetGroups']:
                            tg_arn = tg_response['TargetGroups'][0]['TargetGroupArn']
                            print(f"   🗑️  Deleting target group: {tg_name}")
                            elbv2.delete_target_group(TargetGroupArn=tg_arn)
                            print(f"   ✅ Deleted")
                    except ClientError as e:
                        if e.response['Error']['Code'] != 'TargetGroupNotFound':
                            print(f"   ⚠️  Error deleting {tg_name}: {e}")
            else:
                print("\n   ℹ️  ALB deletion skipped")
                print("\n   To import into Terraform, run:")
                print(f"   terraform import aws_lb.main {alb['LoadBalancerArn']}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'LoadBalancerNotFound':
            print(f"   ℹ️  ALB not found")
        else:
            print(f"   ⚠️  Error: {e}")

    print("\n" + "=" * 60)
    print("  Done!")
    print("=" * 60)

if __name__ == "__main__":
    main()
