#!/usr/bin/env python3
"""
대시보드 테스트를 위해 DynamoDB에 배포 데이터 추가
"""
import boto3
from datetime import datetime, timedelta
import uuid
import json

dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
deployment_table = dynamodb.Table('delightful-deploy-deployment-history')
ai_analysis_table = dynamodb.Table('delightful-deploy-ai-analysis')

def add_test_services():
    """테스트 서비스들을 DynamoDB에 추가"""

    print("=" * 80)
    print("대시보드 테스트 데이터 추가")
    print("=" * 80)
    print()

    # 서비스 1: FastAPI 앱 (test/scenario1)
    service1_id = str(uuid.uuid4())
    service1_analysis_id = "ef93bb2eb28852ae"  # 기존 AI 분석 결과
    service1_timestamp = datetime.now().isoformat()

    deployment1 = {
        'id': service1_id,  # Primary key
        'deployment_id': service1_id,
        'repository': 'test/scenario1',
        'commit_sha': 'bcd6c2f4',
        'branch': 'main',
        'status': 'success',
        'timestamp': service1_timestamp,
        'analysis_id': service1_analysis_id,
        'pusher': 'test-user',
        'deployment_url': 'http://delightful-deploy-alb-52260314.ap-northeast-2.elb.amazonaws.com'
    }

    # AI 분석 결과 생성/업데이트
    ai_analysis1 = {
        'analysis_id': service1_analysis_id,
        'timestamp': service1_timestamp,  # Range key
        'repository': 'test/scenario1',
        'commit_sha': 'bcd6c2f4',
        'created_at': datetime.now().isoformat(),
        'project_info': json.dumps({
            'framework': 'FastAPI',
            'language': 'Python',
            'runtime': 'Python 3.11',
            'port': 8000,
            'description': 'A simple FastAPI application for testing Delightful Deploy'
        }),
        'confidence': '0.95',
        'recommendation': 'deploy'
    }

    try:
        ai_analysis_table.put_item(Item=ai_analysis1)
        print(f"✅ AI 분석 결과 생성: {service1_analysis_id}")
    except Exception as e:
        print(f"⚠️  AI 분석 결과 생성 실패: {e}")

    deployment_table.put_item(Item=deployment1)
    print(f"✅ 서비스 1 배포 기록 추가: test-fastapi-app")
    print(f"   - ID: {service1_id}")
    print(f"   - Status: success (healthy)")
    print(f"   - Framework: FastAPI")
    print()

    # 서비스 2: Express.js 앱 (배포 중)
    service2_id = str(uuid.uuid4())
    service2_analysis_id = str(uuid.uuid4())[:16]
    service2_timestamp = (datetime.now() - timedelta(minutes=5)).isoformat()

    ai_analysis2 = {
        'analysis_id': service2_analysis_id,
        'timestamp': service2_timestamp,
        'repository': 'example/express-api',
        'commit_sha': 'a1b2c3d4',
        'created_at': (datetime.now() - timedelta(hours=2)).isoformat(),
        'project_info': json.dumps({
            'framework': 'Express.js',
            'language': 'JavaScript',
            'runtime': 'Node.js 18',
            'port': 3000,
            'description': 'Express.js REST API backend'
        }),
        'confidence': '0.92',
        'recommendation': 'deploy'
    }

    deployment2 = {
        'id': service2_id,
        'deployment_id': service2_id,
        'repository': 'example/express-api',
        'commit_sha': 'a1b2c3d4',
        'branch': 'main',
        'status': 'in_progress',
        'timestamp': service2_timestamp,
        'analysis_id': service2_analysis_id,
        'pusher': 'dev-user',
        'deployment_url': 'http://delightful-deploy-alb-52260314.ap-northeast-2.elb.amazonaws.com'
    }

    ai_analysis_table.put_item(Item=ai_analysis2)
    deployment_table.put_item(Item=deployment2)
    print(f"✅ 서비스 2 배포 기록 추가: express-api")
    print(f"   - ID: {service2_id}")
    print(f"   - Status: in_progress (deploying)")
    print(f"   - Framework: Express.js")
    print()

    # 서비스 3: React 앱 (성공)
    service3_id = str(uuid.uuid4())
    service3_analysis_id = str(uuid.uuid4())[:16]
    service3_timestamp = (datetime.now() - timedelta(hours=12)).isoformat()

    ai_analysis3 = {
        'analysis_id': service3_analysis_id,
        'timestamp': service3_timestamp,
        'repository': 'frontend/react-dashboard',
        'commit_sha': 'e5f6g7h8',
        'created_at': (datetime.now() - timedelta(days=1)).isoformat(),
        'project_info': json.dumps({
            'framework': 'React',
            'language': 'TypeScript',
            'runtime': 'Node.js 18',
            'port': 3000,
            'description': 'React Dashboard UI with TypeScript'
        }),
        'confidence': '0.98',
        'recommendation': 'deploy'
    }

    deployment3 = {
        'id': service3_id,
        'deployment_id': service3_id,
        'repository': 'frontend/react-dashboard',
        'commit_sha': 'e5f6g7h8',
        'branch': 'main',
        'status': 'success',
        'timestamp': service3_timestamp,
        'analysis_id': service3_analysis_id,
        'pusher': 'frontend-team',
        'deployment_url': 'http://delightful-deploy-alb-52260314.ap-northeast-2.elb.amazonaws.com'
    }

    ai_analysis_table.put_item(Item=ai_analysis3)
    deployment_table.put_item(Item=deployment3)
    print(f"✅ 서비스 3 배포 기록 추가: react-dashboard")
    print(f"   - ID: {service3_id}")
    print(f"   - Status: success (healthy)")
    print(f"   - Framework: React")
    print()

    # 서비스 4: Django 앱 (오류)
    service4_id = str(uuid.uuid4())
    service4_analysis_id = str(uuid.uuid4())[:16]
    service4_timestamp = (datetime.now() - timedelta(hours=2)).isoformat()

    ai_analysis4 = {
        'analysis_id': service4_analysis_id,
        'timestamp': service4_timestamp,
        'repository': 'backend/django-admin',
        'commit_sha': 'i9j0k1l2',
        'created_at': (datetime.now() - timedelta(hours=3)).isoformat(),
        'project_info': json.dumps({
            'framework': 'Django',
            'language': 'Python',
            'runtime': 'Python 3.11',
            'port': 8000,
            'description': 'Django Admin Panel'
        }),
        'confidence': '0.89',
        'recommendation': 'deploy'
    }

    deployment4 = {
        'id': service4_id,
        'deployment_id': service4_id,
        'repository': 'backend/django-admin',
        'commit_sha': 'i9j0k1l2',
        'branch': 'develop',
        'status': 'failed',
        'timestamp': service4_timestamp,
        'analysis_id': service4_analysis_id,
        'pusher': 'backend-team',
        'error': 'Database migration failed',
        'deployment_url': 'http://delightful-deploy-alb-52260314.ap-northeast-2.elb.amazonaws.com'
    }

    ai_analysis_table.put_item(Item=ai_analysis4)
    deployment_table.put_item(Item=deployment4)
    print(f"✅ 서비스 4 배포 기록 추가: django-admin")
    print(f"   - ID: {service4_id}")
    print(f"   - Status: failed (error)")
    print(f"   - Framework: Django")
    print()

    print("=" * 80)
    print("총 4개 서비스 추가 완료")
    print("=" * 80)
    print()
    print("대시보드 상태:")
    print("  🟢 2개 서비스 실행 중 (healthy)")
    print("  🟡 1개 서비스 배포 중 (deploying)")
    print("  🔴 1개 서비스 오류 (error)")
    print()
    print("대시보드 접속: http://localhost:3000")
    print("30초 후 자동 새로고침되거나, '🔄 새로고침' 버튼을 클릭하세요.")
    print()


def verify_data():
    """추가된 데이터 확인"""
    print("=" * 80)
    print("DynamoDB 데이터 확인")
    print("=" * 80)
    print()

    # deployment-history 확인
    deploy_response = deployment_table.scan()
    print(f"✅ deployment-history 테이블: {len(deploy_response['Items'])} 항목")
    for item in deploy_response['Items']:
        print(f"   - {item['repository']} ({item['status']})")
    print()

    # ai-analysis 확인
    ai_response = ai_analysis_table.scan()
    print(f"✅ ai-analysis 테이블: {len(ai_response['Items'])} 항목")
    for item in ai_response['Items']:
        print(f"   - {item.get('repository', 'N/A')}")
    print()


if __name__ == '__main__':
    try:
        add_test_services()
        verify_data()
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
