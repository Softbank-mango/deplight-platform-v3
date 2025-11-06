#!/usr/bin/env python3
"""
Force ECS service redeployment to pick up VPC endpoints
"""
import boto3

def force_redeploy():
    """Force a new deployment of the ECS service"""

    ecs = boto3.client('ecs', region_name='ap-northeast-2')

    print("Forcing ECS service redeployment...")
    print("=" * 80)

    try:
        response = ecs.update_service(
            cluster='delightful-deploy-cluster',
            service='delightful-deploy-service',
            forceNewDeployment=True
        )

        print(f"✅ New deployment initiated")
        print(f"   Service: {response['service']['serviceName']}")
        print(f"   Cluster: {response['service']['clusterArn'].split('/')[-1]}")
        print(f"   Desired Count: {response['service']['desiredCount']}")
        print()
        print("Waiting for new tasks to start with VPC endpoints...")
        print("This may take 1-2 minutes as tasks pull Docker images.")
        print()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    force_redeploy()
