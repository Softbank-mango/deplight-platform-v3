#!/usr/bin/env python3
"""남은 AWS 리소스 강제 정리"""
import boto3
import time

AWS_ACCESS_KEY = "AKIAXPBPUMIXA5RFKXUR"
AWS_SECRET_KEY = "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"
AWS_REGION = "ap-northeast-2"

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

ecs_client = session.client('ecs')
s3_client = session.client('s3')
elbv2_client = session.client('elbv2')

print("=" * 80)
print("남은 리소스 강제 정리")
print("=" * 80)

# 1. ECS 태스크 강제 중지
print("\n[1/4] ECS 태스크 강제 중지...")
cluster_name = "delightful-deploy-cluster"
try:
    tasks = ecs_client.list_tasks(cluster=cluster_name)
    task_arns = tasks.get('taskArns', [])
    if task_arns:
        print(f"  {len(task_arns)}개 태스크 발견, 강제 중지 중...")
        for task_arn in task_arns:
            try:
                ecs_client.stop_task(cluster=cluster_name, task=task_arn, reason='Cleanup')
                print(f"  ✓ 태스크 중지: {task_arn}")
            except Exception as e:
                print(f"  ✗ 태스크 중지 실패: {e}")
        print("  태스크 종료 대기 중 (30초)...")
        time.sleep(30)
    else:
        print("  활성 태스크 없음")
except Exception as e:
    print(f"  ✗ Error: {e}")

# 2. ECS 클러스터 삭제 재시도
print("\n[2/4] ECS 클러스터 삭제 재시도...")
try:
    ecs_client.delete_cluster(cluster=cluster_name)
    print(f"  ✓ 클러스터 삭제 성공: {cluster_name}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# 3. S3 버킷 비우기 및 삭제
print("\n[3/4] S3 버킷 강제 삭제...")
bucket_name = "delightful-deploy-artifacts-1762083190"
try:
    print(f"  버킷 비우는 중: {bucket_name}")

    # 모든 객체 버전 삭제
    paginator = s3_client.get_paginator('list_object_versions')
    pages = paginator.paginate(Bucket=bucket_name)

    delete_count = 0
    for page in pages:
        # 일반 객체 삭제
        if 'Versions' in page:
            for version in page['Versions']:
                s3_client.delete_object(
                    Bucket=bucket_name,
                    Key=version['Key'],
                    VersionId=version['VersionId']
                )
                delete_count += 1

        # 삭제 마커 삭제
        if 'DeleteMarkers' in page:
            for marker in page['DeleteMarkers']:
                s3_client.delete_object(
                    Bucket=bucket_name,
                    Key=marker['Key'],
                    VersionId=marker['VersionId']
                )
                delete_count += 1

    print(f"  ✓ {delete_count}개 객체 삭제 완료")

    # 버킷 삭제
    s3_client.delete_bucket(Bucket=bucket_name)
    print(f"  ✓ 버킷 삭제 성공: {bucket_name}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# 4. Target Groups 삭제 재시도
print("\n[4/4] Target Groups 삭제 재시도...")
print("  ALB 삭제 완료 대기 중 (30초)...")
time.sleep(30)

target_groups = ['delightful-deploy-blue-tg', 'delightful-deploy-green-tg']
for tg_name in target_groups:
    try:
        # TG ARN 찾기
        tgs = elbv2_client.describe_target_groups(Names=[tg_name])
        if tgs['TargetGroups']:
            tg_arn = tgs['TargetGroups'][0]['TargetGroupArn']
            elbv2_client.delete_target_group(TargetGroupArn=tg_arn)
            print(f"  ✓ 삭제 성공: {tg_name}")
    except Exception as e:
        print(f"  ✗ Error deleting {tg_name}: {e}")

print("\n" + "=" * 80)
print("정리 완료")
print("=" * 80)
