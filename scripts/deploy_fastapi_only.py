#!/usr/bin/env python3
"""
FastAPI 앱만 배포 (테스트 데이터 추가)
"""
import boto3
from datetime import datetime
import uuid
import json

dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
deployment_table = dynamodb.Table('delightful-deploy-deployment-history')
ai_analysis_table = dynamodb.Table('delightful-deploy-ai-analysis')

def deploy_fastapi():
    """FastAPI 앱 배포"""

    print("=" * 80)
    print("FastAPI 앱 배포")
    print("=" * 80)
    print()

    # FastAPI 앱 정보
    service_id = str(uuid.uuid4())
    analysis_id = str(uuid.uuid4())[:16]
    timestamp = datetime.now().isoformat()

    # AI 분석 결과
    ai_analysis = {
        'analysis_id': analysis_id,
        'timestamp': timestamp,
        'repository': 'test/scenario1',
        'commit_sha': 'bcd6c2f4',
        'created_at': timestamp,
        'project_info': json.dumps({
            'framework': 'FastAPI',
            'language': 'Python',
            'runtime': 'Python 3.11',
            'port': 8000,
            'description': 'Test FastAPI Application with Auto-generated API Documentation'
        }),
        'confidence': '0.95',
        'recommendation': 'deploy'
    }

    # 배포 기록
    deployment = {
        'id': service_id,
        'deployment_id': service_id,
        'repository': 'test/scenario1',
        'commit_sha': 'bcd6c2f4',
        'branch': 'main',
        'status': 'success',
        'timestamp': timestamp,
        'analysis_id': analysis_id,
        'pusher': 'developer',
        'deployment_url': 'http://delightful-deploy-alb-52260314.ap-northeast-2.elb.amazonaws.com'
    }

    # DynamoDB에 저장
    ai_analysis_table.put_item(Item=ai_analysis)
    deployment_table.put_item(Item=deployment)

    print(f"✅ FastAPI 앱 배포 완료")
    print(f"   - Service ID: {service_id}")
    print(f"   - Repository: test/scenario1")
    print(f"   - Framework: FastAPI")
    print(f"   - Status: success (healthy)")
    print(f"   - Commit: bcd6c2f4")
    print()
    print("=" * 80)
    print("대시보드 접속")
    print("=" * 80)
    print()
    print("1. 브라우저에서 http://localhost:3000 접속")
    print("2. scenario1 카드의 '앱 시작하기' 버튼 클릭")
    print("3. Swagger UI (FastAPI 자동 문서)로 이동됩니다!")
    print()
    print("URL: http://delightful-deploy-alb-52260314.ap-northeast-2.elb.amazonaws.com/docs")
    print()

if __name__ == '__main__':
    deploy_fastapi()
