#!/usr/bin/env python3
"""
ALB 및 관련 리소스 강제 정리 스크립트
Target Groups가 Listener에 연결되어 있어서 삭제 안될 때 사용
"""

import boto3
import sys
from botocore.exceptions import ClientError

APP_NAME = "delightful-deploy"
AWS_REGION = "ap-northeast-2"

def main():
    print("=" * 60)
    print("  ALB & Target Groups Force Cleanup")
    print("=" * 60)
    print()

    elbv2 = boto3.client('elbv2', region_name=AWS_REGION)

    # 1. Find ALB
    print("1. Checking ALB...")
    try:
        response = elbv2.describe_load_balancers(
            Names=[f"{APP_NAME}-alb"]
        )

        if response['LoadBalancers']:
            alb = response['LoadBalancers'][0]
            alb_arn = alb['LoadBalancerArn']
            print(f"   Found ALB: {alb['LoadBalancerName']}")
            print(f"   ARN: {alb_arn}")

            # 2. Get Listeners
            print("\n2. Checking Listeners...")
            listeners_response = elbv2.describe_listeners(LoadBalancerArn=alb_arn)

            for listener in listeners_response['Listeners']:
                listener_arn = listener['ListenerArn']
                listener_port = listener['Port']
                print(f"   Found Listener on port {listener_port}")

                # Get rules
                rules_response = elbv2.describe_rules(ListenerArn=listener_arn)

                for rule in rules_response['Rules']:
                    if rule['IsDefault']:
                        continue  # Skip default rule

                    rule_arn = rule['RuleArn']
                    print(f"      Deleting rule: {rule['Priority']}")
                    try:
                        elbv2.delete_rule(RuleArn=rule_arn)
                        print(f"      ✅ Rule deleted")
                    except ClientError as e:
                        print(f"      ⚠️  Error: {e}")

                # Delete listener
                print(f"   🗑️  Deleting listener on port {listener_port}")
                try:
                    elbv2.delete_listener(ListenerArn=listener_arn)
                    print(f"   ✅ Listener deleted")
                except ClientError as e:
                    print(f"   ⚠️  Error: {e}")

            # 3. Delete Target Groups
            print("\n3. Deleting Target Groups...")
            target_groups = [
                f"{APP_NAME}-blue-tg",
                f"{APP_NAME}-green-tg",
                f"{APP_NAME}-dashboard-tg",
            ]

            for tg_name in target_groups:
                try:
                    tg_response = elbv2.describe_target_groups(Names=[tg_name])
                    if tg_response['TargetGroups']:
                        tg_arn = tg_response['TargetGroups'][0]['TargetGroupArn']
                        print(f"   🗑️  Deleting target group: {tg_name}")
                        elbv2.delete_target_group(TargetGroupArn=tg_arn)
                        print(f"   ✅ Target group deleted")
                except ClientError as e:
                    if e.response['Error']['Code'] == 'TargetGroupNotFound':
                        print(f"   ℹ️  Target group {tg_name} not found")
                    else:
                        print(f"   ⚠️  Error: {e}")

            # 4. Optionally delete ALB
            print("\n4. ALB Deletion")
            print(f"   ALB: {alb['LoadBalancerName']}")
            print(f"   DNS: {alb['DNSName']}")
            print("\n   ⚠️  Do you want to delete the ALB as well?")
            print("   This will cause downtime for your application!")
            print("   Type 'DELETE-ALB' to confirm: ", end='')

            confirmation = input().strip()

            if confirmation == 'DELETE-ALB':
                print(f"\n   🗑️  Deleting ALB: {alb['LoadBalancerName']}")
                elbv2.delete_load_balancer(LoadBalancerArn=alb_arn)
                print(f"   ✅ ALB deletion initiated")
                print(f"   ⏳ ALB will be deleted in a few minutes...")
            else:
                print("\n   ℹ️  ALB deletion skipped")
                print("   ℹ️  Target Groups are now deleted, Terraform can recreate them")

        else:
            print(f"   ℹ️  ALB not found: {APP_NAME}-alb")

    except ClientError as e:
        if e.response['Error']['Code'] == 'LoadBalancerNotFound':
            print(f"   ℹ️  ALB not found: {APP_NAME}-alb")
            print("\n   Trying to delete Target Groups directly...")

            # Try to delete target groups anyway
            target_groups = [
                f"{APP_NAME}-blue-tg",
                f"{APP_NAME}-green-tg",
                f"{APP_NAME}-dashboard-tg",
            ]

            for tg_name in target_groups:
                try:
                    tg_response = elbv2.describe_target_groups(Names=[tg_name])
                    if tg_response['TargetGroups']:
                        tg_arn = tg_response['TargetGroups'][0]['TargetGroupArn']
                        print(f"   🗑️  Deleting target group: {tg_name}")
                        elbv2.delete_target_group(TargetGroupArn=tg_arn)
                        print(f"   ✅ Target group deleted")
                except ClientError as e2:
                    if e2.response['Error']['Code'] == 'TargetGroupNotFound':
                        print(f"   ℹ️  Target group {tg_name} not found")
                    else:
                        print(f"   ⚠️  Error: {e2}")
        else:
            print(f"   ⚠️  Error: {e}")

    print("\n" + "=" * 60)
    print("  Cleanup completed!")
    print("=" * 60)
    print("\nNext: Run Terraform apply to recreate resources")

if __name__ == "__main__":
    main()
