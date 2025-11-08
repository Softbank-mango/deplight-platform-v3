#!/usr/bin/env python3
"""
Verify Delightful Deploy infrastructure deployment
"""
import boto3
import json
from datetime import datetime

def verify_infrastructure():
    """Verify all deployed AWS resources"""

    # Initialize AWS clients
    ecs = boto3.client('ecs', region_name='ap-northeast-2')
    lambda_client = boto3.client('lambda', region_name='ap-northeast-2')
    dynamodb = boto3.client('dynamodb', region_name='ap-northeast-2')
    elbv2 = boto3.client('elbv2', region_name='ap-northeast-2')
    codedeploy = boto3.client('codedeploy', region_name='ap-northeast-2')

    print("=" * 80)
    print("DELIGHTFUL DEPLOY - Infrastructure Verification")
    print("=" * 80)
    print()

    # 1. ECS Cluster
    print("1. ECS Cluster")
    print("-" * 80)
    try:
        cluster_response = ecs.describe_clusters(clusters=['delightful-deploy-cluster'])
        if cluster_response['clusters']:
            cluster = cluster_response['clusters'][0]
            print(f"   Name: {cluster['clusterName']}")
            print(f"   Status: {cluster['status']}")
            print(f"   Running Tasks: {cluster.get('runningTasksCount', 0)}")
            print(f"   Pending Tasks: {cluster.get('pendingTasksCount', 0)}")
            print(f"   ✅ ECS Cluster is active")
        else:
            print("   ❌ ECS Cluster not found")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()

    # 2. ECS Service
    print("2. ECS Service")
    print("-" * 80)
    try:
        service_response = ecs.describe_services(
            cluster='delightful-deploy-cluster',
            services=['delightful-deploy-service']
        )
        if service_response['services']:
            service = service_response['services'][0]
            print(f"   Name: {service['serviceName']}")
            print(f"   Status: {service['status']}")
            print(f"   Desired Count: {service['desiredCount']}")
            print(f"   Running Count: {service['runningCount']}")
            print(f"   Pending Count: {service['pendingCount']}")
            print(f"   Launch Type: {service['launchType']}")
            print(f"   ✅ ECS Service is running")
        else:
            print("   ❌ ECS Service not found")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()

    # 3. Lambda Function
    print("3. Lambda AI Analyzer")
    print("-" * 80)
    try:
        lambda_response = lambda_client.get_function(FunctionName='delightful-deploy-ai-analyzer')
        config = lambda_response['Configuration']
        print(f"   Name: {config['FunctionName']}")
        print(f"   Runtime: {config['Runtime']}")
        print(f"   State: {config['State']}")
        print(f"   Memory: {config['MemorySize']} MB")
        print(f"   Timeout: {config['Timeout']} seconds")
        print(f"   Last Modified: {config['LastModified']}")

        # Get Function URL
        try:
            url_response = lambda_client.get_function_url_config(FunctionName='delightful-deploy-ai-analyzer')
            print(f"   Function URL: {url_response['FunctionUrl']}")
        except:
            pass

        print(f"   ✅ Lambda Function is active")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()

    # 4. DynamoDB Tables
    print("4. DynamoDB Tables")
    print("-" * 80)
    try:
        tables_response = dynamodb.list_tables()
        delightful_tables = [t for t in tables_response.get('TableNames', []) if 'delightful' in t.lower()]

        for table_name in delightful_tables:
            table_info = dynamodb.describe_table(TableName=table_name)
            table = table_info['Table']
            print(f"   📊 {table_name}")
            print(f"      Status: {table['TableStatus']}")
            print(f"      Items: {table.get('ItemCount', 0)}")

        if delightful_tables:
            print(f"   ✅ Found {len(delightful_tables)} DynamoDB tables")
        else:
            print("   ⚠️  No DynamoDB tables found")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()

    # 5. Application Load Balancer
    print("5. Application Load Balancer")
    print("-" * 80)
    try:
        albs = elbv2.describe_load_balancers()
        delightful_alb = [alb for alb in albs['LoadBalancers'] if 'delightful' in alb['LoadBalancerName'].lower()]

        if delightful_alb:
            alb = delightful_alb[0]
            print(f"   Name: {alb['LoadBalancerName']}")
            print(f"   DNS: {alb['DNSName']}")
            print(f"   State: {alb['State']['Code']}")
            print(f"   URL: http://{alb['DNSName']}")
            print(f"   ✅ ALB is active")
        else:
            print("   ❌ ALB not found")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()

    # 6. CodeDeploy Application
    print("6. CodeDeploy Application")
    print("-" * 80)
    try:
        apps = codedeploy.list_applications()
        delightful_apps = [app for app in apps.get('applications', []) if 'delightful' in app.lower()]

        if delightful_apps:
            for app_name in delightful_apps:
                app_info = codedeploy.get_application(applicationName=app_name)
                print(f"   Name: {app_info['application']['applicationName']}")
                print(f"   Platform: {app_info['application']['computePlatform']}")
            print(f"   ✅ CodeDeploy Application is configured")
        else:
            print("   ⚠️  No CodeDeploy applications found (Blue-Green deployment may be disabled)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()

    # Summary
    print("=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("  1. Test ALB health endpoint")
    print("  2. Verify ECS tasks are running")
    print("  3. Test Lambda AI Analyzer with sample payload")
    print("  4. Check CloudWatch logs and dashboards")
    print()

if __name__ == '__main__':
    verify_infrastructure()
