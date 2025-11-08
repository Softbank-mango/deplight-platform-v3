#!/usr/bin/env python3
"""
DynamoDB deployment-logs 테이블 생성
"""
import boto3

dynamodb = boto3.client('dynamodb', region_name='ap-northeast-2')

def create_deployment_logs_table():
    """배포 로그 테이블 생성"""
    table_name = 'delightful-deploy-deployment-logs'

    try:
        # 기존 테이블 확인
        existing_tables = dynamodb.list_tables()['TableNames']
        if table_name in existing_tables:
            print(f"✅ 테이블이 이미 존재합니다: {table_name}")
            return

        # 테이블 생성
        response = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'deployment_id',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'timestamp',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'deployment_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'timestamp',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST',  # On-demand billing
            Tags=[
                {
                    'Key': 'Application',
                    'Value': 'delightful-deploy'
                },
                {
                    'Key': 'Purpose',
                    'Value': 'deployment-logs'
                }
            ]
        )

        print(f"✅ 테이블 생성 시작: {table_name}")
        print(f"   Status: {response['TableDescription']['TableStatus']}")

        # 테이블 활성화 대기
        print("   테이블 활성화 대기 중...")
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=table_name)

        print(f"✅ 테이블 생성 완료: {table_name}")

    except Exception as e:
        print(f"❌ 테이블 생성 실패: {e}")
        raise

if __name__ == '__main__':
    create_deployment_logs_table()
