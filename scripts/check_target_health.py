#!/usr/bin/env python3
"""
Check ALB target group health
"""
import boto3

def check_target_health():
    """Check health of targets in ALB target groups"""

    elbv2 = boto3.client('elbv2', region_name='ap-northeast-2')

    print("=" * 80)
    print("ALB TARGET GROUP HEALTH CHECK")
    print("=" * 80)
    print()

    try:
        # Get target groups
        target_groups = elbv2.describe_target_groups(
            Names=['delightful-deploy-blue-tg']
        )

        for tg in target_groups['TargetGroups']:
            print(f"Target Group: {tg['TargetGroupName']}")
            print(f"Health Check:")
            print(f"   Protocol: {tg.get('HealthCheckProtocol', 'N/A')}")
            print(f"   Path: {tg.get('HealthCheckPath', 'N/A')}")
            print(f"   Port: {tg.get('HealthCheckPort', 'N/A')}")
            print(f"   Interval: {tg.get('HealthCheckIntervalSeconds', 'N/A')}s")
            print(f"   Timeout: {tg.get('HealthCheckTimeoutSeconds', 'N/A')}s")
            print(f"   Healthy Threshold: {tg.get('HealthyThresholdCount', 'N/A')}")
            print(f"   Unhealthy Threshold: {tg.get('UnhealthyThresholdCount', 'N/A')}")
            print()

            # Get target health
            health = elbv2.describe_target_health(
                TargetGroupArn=tg['TargetGroupArn']
            )

            print(f"Registered Targets:")
            if health.get('TargetHealthDescriptions'):
                for target in health['TargetHealthDescriptions']:
                    target_id = target['Target']['Id']
                    port = target['Target']['Port']
                    state = target['TargetHealth']['State']
                    reason = target['TargetHealth'].get('Reason', 'N/A')
                    description = target['TargetHealth'].get('Description', '')

                    status_emoji = {
                        'healthy': '✅',
                        'unhealthy': '❌',
                        'initial': '⏳',
                        'draining': '⚠️',
                        'unavailable': '❌'
                    }.get(state, '❓')

                    print(f"   {status_emoji} Target: {target_id}:{port}")
                    print(f"      State: {state}")
                    if reason != 'N/A':
                        print(f"      Reason: {reason}")
                    if description:
                        print(f"      Description: {description}")
                    print()

                # Summary
                healthy_count = sum(1 for t in health['TargetHealthDescriptions']
                                  if t['TargetHealth']['State'] == 'healthy')
                total_count = len(health['TargetHealthDescriptions'])

                print(f"Summary: {healthy_count}/{total_count} targets healthy")
                if healthy_count == 0:
                    print()
                    print("ℹ️  Targets are still initializing. Wait for health checks to pass.")
                    print("   This typically takes 1-2 minutes for new tasks.")

            else:
                print("   No targets registered")

    except Exception as e:
        print(f"❌ Error: {e}")

    print()
    print("=" * 80)

if __name__ == '__main__':
    check_target_health()
