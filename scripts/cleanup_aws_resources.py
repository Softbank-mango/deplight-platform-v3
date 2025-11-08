#!/usr/bin/env python3
"""
AWS 리소스 정리 스크립트 - mango_sb 계정 (513348493870)
비용 절감을 위해 테스트 리소스 삭제
"""
import boto3
import os
from botocore.exceptions import ClientError

# mango_sb 계정 자격증명
AWS_ACCESS_KEY = "AKIAXPBPUMIXA5RFKXUR"
AWS_SECRET_KEY = "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"
AWS_REGION = "ap-northeast-2"

# boto3 클라이언트 초기화
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

ecs_client = session.client('ecs')
ecr_client = session.client('ecr')
dynamodb_client = session.client('dynamodb')
lambda_client = session.client('lambda')
s3_client = session.client('s3')
elbv2_client = session.client('elbv2')
codedeploy_client = session.client('codedeploy')
cloudformation_client = session.client('cloudformation')
iam_client = session.client('iam')

def list_resources():
    """모든 리소스 목록 확인"""
    print("=" * 80)
    print("현재 AWS 리소스 목록 (mango_sb 계정 - 513348493870)")
    print("=" * 80)

    resources = {
        'ecs_clusters': [],
        'ecs_services': [],
        'ecr_repositories': [],
        'dynamodb_tables': [],
        'lambda_functions': [],
        's3_buckets': [],
        'load_balancers': [],
        'target_groups': [],
        'cloudformation_stacks': []
    }

    # ECS Clusters
    try:
        clusters = ecs_client.list_clusters()
        resources['ecs_clusters'] = clusters.get('clusterArns', [])
        print(f"\n[ECS Clusters] {len(resources['ecs_clusters'])}개")
        for cluster in resources['ecs_clusters']:
            print(f"  - {cluster}")
            # Services in cluster
            try:
                services = ecs_client.list_services(cluster=cluster)
                service_arns = services.get('serviceArns', [])
                resources['ecs_services'].extend([(cluster, svc) for svc in service_arns])
                print(f"    Services: {len(service_arns)}개")
                for svc in service_arns:
                    print(f"      - {svc}")
            except Exception as e:
                print(f"    Error listing services: {e}")
    except Exception as e:
        print(f"[ECS Clusters] Error: {e}")

    # ECR Repositories
    try:
        repos = ecr_client.describe_repositories()
        resources['ecr_repositories'] = repos.get('repositories', [])
        print(f"\n[ECR Repositories] {len(resources['ecr_repositories'])}개")
        for repo in resources['ecr_repositories']:
            print(f"  - {repo['repositoryName']} ({repo['repositoryUri']})")
    except Exception as e:
        print(f"[ECR Repositories] Error: {e}")

    # DynamoDB Tables
    try:
        tables = dynamodb_client.list_tables()
        resources['dynamodb_tables'] = tables.get('TableNames', [])
        print(f"\n[DynamoDB Tables] {len(resources['dynamodb_tables'])}개")
        for table in resources['dynamodb_tables']:
            print(f"  - {table}")
    except Exception as e:
        print(f"[DynamoDB Tables] Error: {e}")

    # Lambda Functions
    try:
        functions = lambda_client.list_functions()
        resources['lambda_functions'] = functions.get('Functions', [])
        print(f"\n[Lambda Functions] {len(resources['lambda_functions'])}개")
        for func in resources['lambda_functions']:
            print(f"  - {func['FunctionName']} ({func['Runtime']})")
    except Exception as e:
        print(f"[Lambda Functions] Error: {e}")

    # S3 Buckets
    try:
        buckets = s3_client.list_buckets()
        resources['s3_buckets'] = buckets.get('Buckets', [])
        print(f"\n[S3 Buckets] {len(resources['s3_buckets'])}개")
        for bucket in resources['s3_buckets']:
            print(f"  - {bucket['Name']}")
    except Exception as e:
        print(f"[S3 Buckets] Error: {e}")

    # Load Balancers
    try:
        lbs = elbv2_client.describe_load_balancers()
        resources['load_balancers'] = lbs.get('LoadBalancers', [])
        print(f"\n[Load Balancers] {len(resources['load_balancers'])}개")
        for lb in resources['load_balancers']:
            print(f"  - {lb['LoadBalancerName']} ({lb['DNSName']})")
    except Exception as e:
        print(f"[Load Balancers] Error: {e}")

    # Target Groups
    try:
        tgs = elbv2_client.describe_target_groups()
        resources['target_groups'] = tgs.get('TargetGroups', [])
        print(f"\n[Target Groups] {len(resources['target_groups'])}개")
        for tg in resources['target_groups']:
            print(f"  - {tg['TargetGroupName']}")
    except Exception as e:
        print(f"[Target Groups] Error: {e}")

    # CloudFormation Stacks
    try:
        stacks = cloudformation_client.list_stacks(
            StackStatusFilter=['CREATE_COMPLETE', 'UPDATE_COMPLETE', 'ROLLBACK_COMPLETE']
        )
        resources['cloudformation_stacks'] = stacks.get('StackSummaries', [])
        print(f"\n[CloudFormation Stacks] {len(resources['cloudformation_stacks'])}개")
        for stack in resources['cloudformation_stacks']:
            print(f"  - {stack['StackName']} ({stack['StackStatus']})")
    except Exception as e:
        print(f"[CloudFormation Stacks] Error: {e}")

    print("\n" + "=" * 80)
    return resources

def cleanup_resources(resources, dry_run=True):
    """리소스 삭제 (dry_run=False일 때만 실제 삭제)"""
    if dry_run:
        print("\n[DRY RUN] 실제로 삭제하지 않고 확인만 합니다.")
        print("실제 삭제를 원하면 dry_run=False로 설정하세요.\n")
        return

    print("\n" + "=" * 80)
    print("리소스 삭제 시작")
    print("=" * 80)

    # 1. ECS Services 삭제
    print("\n[1/8] ECS Services 삭제...")
    for cluster, service in resources['ecs_services']:
        try:
            print(f"  Deleting service: {service}")
            ecs_client.update_service(
                cluster=cluster,
                service=service,
                desiredCount=0
            )
            ecs_client.delete_service(cluster=cluster, service=service, force=True)
            print(f"  ✓ Deleted: {service}")
        except Exception as e:
            print(f"  ✗ Error deleting {service}: {e}")

    # 2. ECS Clusters 삭제
    print("\n[2/8] ECS Clusters 삭제...")
    for cluster in resources['ecs_clusters']:
        try:
            print(f"  Deleting cluster: {cluster}")
            ecs_client.delete_cluster(cluster=cluster)
            print(f"  ✓ Deleted: {cluster}")
        except Exception as e:
            print(f"  ✗ Error deleting {cluster}: {e}")

    # 3. ECR Repositories 삭제
    print("\n[3/8] ECR Repositories 삭제...")
    for repo in resources['ecr_repositories']:
        try:
            repo_name = repo['repositoryName']
            print(f"  Deleting repository: {repo_name}")
            ecr_client.delete_repository(repositoryName=repo_name, force=True)
            print(f"  ✓ Deleted: {repo_name}")
        except Exception as e:
            print(f"  ✗ Error deleting {repo_name}: {e}")

    # 4. Lambda Functions 삭제
    print("\n[4/8] Lambda Functions 삭제...")
    for func in resources['lambda_functions']:
        try:
            func_name = func['FunctionName']
            print(f"  Deleting function: {func_name}")
            lambda_client.delete_function(FunctionName=func_name)
            print(f"  ✓ Deleted: {func_name}")
        except Exception as e:
            print(f"  ✗ Error deleting {func_name}: {e}")

    # 5. DynamoDB Tables 삭제
    print("\n[5/8] DynamoDB Tables 삭제...")
    for table in resources['dynamodb_tables']:
        try:
            print(f"  Deleting table: {table}")
            dynamodb_client.delete_table(TableName=table)
            print(f"  ✓ Deleted: {table}")
        except Exception as e:
            print(f"  ✗ Error deleting {table}: {e}")

    # 6. S3 Buckets 삭제
    print("\n[6/8] S3 Buckets 삭제...")
    for bucket in resources['s3_buckets']:
        try:
            bucket_name = bucket['Name']
            print(f"  Deleting bucket: {bucket_name}")
            # 먼저 버킷 내용물 삭제
            objects = s3_client.list_objects_v2(Bucket=bucket_name)
            if 'Contents' in objects:
                for obj in objects['Contents']:
                    s3_client.delete_object(Bucket=bucket_name, Key=obj['Key'])
            s3_client.delete_bucket(Bucket=bucket_name)
            print(f"  ✓ Deleted: {bucket_name}")
        except Exception as e:
            print(f"  ✗ Error deleting {bucket_name}: {e}")

    # 7. Target Groups 삭제
    print("\n[7/8] Target Groups 삭제...")
    for tg in resources['target_groups']:
        try:
            tg_arn = tg['TargetGroupArn']
            print(f"  Deleting target group: {tg['TargetGroupName']}")
            elbv2_client.delete_target_group(TargetGroupArn=tg_arn)
            print(f"  ✓ Deleted: {tg['TargetGroupName']}")
        except Exception as e:
            print(f"  ✗ Error deleting {tg['TargetGroupName']}: {e}")

    # 8. Load Balancers 삭제
    print("\n[8/8] Load Balancers 삭제...")
    for lb in resources['load_balancers']:
        try:
            lb_arn = lb['LoadBalancerArn']
            print(f"  Deleting load balancer: {lb['LoadBalancerName']}")
            elbv2_client.delete_load_balancer(LoadBalancerArn=lb_arn)
            print(f"  ✓ Deleted: {lb['LoadBalancerName']}")
        except Exception as e:
            print(f"  ✗ Error deleting {lb['LoadBalancerName']}: {e}")

    print("\n" + "=" * 80)
    print("리소스 삭제 완료")
    print("=" * 80)

if __name__ == "__main__":
    import sys

    # 먼저 리소스 목록 확인
    resources = list_resources()

    # 명령줄 인자 확인
    if len(sys.argv) > 1 and sys.argv[1] == '--delete':
        print("\n⚠️  WARNING: 모든 리소스가 삭제됩니다!")
        print("계속하려면 'yes'를 입력하세요: ", end='')
        confirmation = input()
        if confirmation.lower() == 'yes':
            cleanup_resources(resources, dry_run=False)
        else:
            print("취소되었습니다.")
    else:
        # DRY RUN (실제 삭제 안 함)
        cleanup_resources(resources, dry_run=True)

        print("\n" + "=" * 80)
        print("실제 삭제를 원하면 다음 명령어를 실행하세요:")
        print("python3 cleanup_aws_resources.py --delete")
        print("=" * 80)
