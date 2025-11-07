#!/usr/bin/env python3
"""
Delightful Deploy Dashboard API
FastAPI backend for the service dashboard
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import boto3
from datetime import datetime
from typing import List, Dict, Optional
import os
import threading
import json
import requests
from pathlib import Path

app = FastAPI(
    title="Delightful Deploy Dashboard",
    description="서비스 대시보드 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static 파일 경로 설정
STATIC_DIR = Path(__file__).parent.parent / "static"

# AWS 설정
AWS_REGION = os.getenv('AWS_REGION', 'ap-northeast-2')
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
deployment_table = dynamodb.Table('delightful-deploy-deployment-history')
ai_analysis_table = dynamodb.Table('delightful-deploy-ai-analysis')
garden_state_table = dynamodb.Table('delightful-deploy-garden-state')
deployment_logs_table = dynamodb.Table('delightful-deploy-deployment-logs')

# ALB DNS (환경변수에서 가져오기 - Terraform이 설정)
ALB_DNS = os.getenv('ALB_DNS', 'delightful-deploy-alb-1219635926.ap-northeast-2.elb.amazonaws.com')

# GitHub Configuration for triggering workflows
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # Personal Access Token
GITHUB_API_URL = "https://api.github.com"
MANGO_REPO = os.getenv('MANGO_REPO', 'Softbank-mango/deplight-platform-v3')


@app.get("/")
async def root():
    """루트 경로 - index.html 제공"""
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail=f"index.html not found at {index_path}")
    return FileResponse(str(index_path))


@app.get("/dashboard")
async def dashboard_root():
    """대시보드 경로 - index.html 제공(/dashboard 라우팅 호환)"""
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail=f"index.html not found at {index_path}")
    return FileResponse(str(index_path))


@app.get("/deploy.html")
async def deploy_page():
    """배포 페이지 제공"""
    deploy_path = STATIC_DIR / "deploy.html"
    if not deploy_path.exists():
        raise HTTPException(status_code=404, detail=f"deploy.html not found at {deploy_path}")
    return FileResponse(str(deploy_path))


@app.get("/api/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "dashboard-api"
    }


@app.get("/api/services")
async def get_services():
    """배포된 서비스 목록 조회"""
    try:
        # 배포 히스토리 테이블에서 모든 배포 조회
        response = deployment_table.scan()
        items = response.get('Items', [])

        # AI 분석 테이블에서 프로젝트 정보 가져오기
        ai_analyses = {}
        try:
            ai_response = ai_analysis_table.scan()
            for item in ai_response.get('Items', []):
                analysis_id = item.get('analysis_id')
                if analysis_id:
                    ai_analyses[analysis_id] = item
        except Exception as e:
            print(f"Warning: Could not fetch AI analysis data: {e}")

        # 서비스 정보 구성
        services = []
        for item in items:
            analysis_id = item.get('analysis_id')
            project_info = {}

            # AI 분석 결과에서 프로젝트 정보 가져오기
            if analysis_id and analysis_id in ai_analyses:
                ai_item = ai_analyses[analysis_id]
                project_info_raw = ai_item.get('project_info', {})

                # project_info가 JSON 문자열인 경우 파싱
                if isinstance(project_info_raw, str):
                    try:
                        import json
                        project_info = json.loads(project_info_raw)
                    except Exception as parse_err:
                        print(f"Warning: Could not parse project_info JSON: {parse_err}")
                        project_info = {}
                elif isinstance(project_info_raw, dict):
                    project_info = project_info_raw
                else:
                    # 다른 타입인 경우 빈 dict로 초기화
                    project_info = {}

            # 기본 정보 구성
            repository = item.get('repository', 'unknown')
            service_name = repository.split('/')[-1] if '/' in repository else repository

            # URL 설정: FastAPI의 경우 Swagger UI로 이동
            base_url = f"http://{ALB_DNS}"
            framework = project_info.get('framework', 'N/A')

            if 'FastAPI' in framework or 'fastapi' in framework.lower():
                service_url = f"{base_url}/docs"
            else:
                service_url = base_url

            service = {
                "id": item.get('deployment_id', analysis_id),
                "name": service_name,
                "description": project_info.get('description', f"{project_info.get('framework', 'Unknown')} Application"),
                "framework": framework,
                "language": project_info.get('language', 'N/A'),
                "runtime": project_info.get('runtime', 'N/A'),
                "port": project_info.get('port', 8000),
                "status": _get_service_status(item.get('status', 'unknown')),
                "deployedAt": item.get('timestamp', item.get('created_at', datetime.now().isoformat())),
                "commitSha": item.get('commit_sha', 'unknown'),
                "branch": item.get('branch', 'main'),
                "url": service_url,
                "repository": repository
            }

            services.append(service)

        # 최신 배포 순으로 정렬
        services.sort(key=lambda x: x['deployedAt'], reverse=True)

        return {
            "success": True,
            "count": len(services),
            "services": services
        }

    except Exception as e:
        print(f"Error fetching services: {e}")
        # 에러 발생 시 테스트 데이터 반환
        return {
            "success": False,
            "error": str(e),
            "count": 1,
            "services": [
                {
                    "id": "test-1",
                    "name": "test-fastapi-app",
                    "description": "FastAPI Test Application",
                    "framework": "FastAPI",
                    "language": "Python",
                    "runtime": "Python 3.11",
                    "port": 8000,
                    "status": "healthy",
                    "deployedAt": datetime.now().isoformat(),
                    "commitSha": "bcd6c2f4",
                    "branch": "main",
                    "url": f"http://{ALB_DNS}",
                    "repository": "test/scenario1"
                }
            ]
        }


@app.get("/api/services/{service_id}")
async def get_service_detail(service_id: str):
    """특정 서비스의 상세 정보 조회"""
    try:
        # 배포 히스토리에서 조회
        response = deployment_table.get_item(
            Key={'deployment_id': service_id}
        )

        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="Service not found")

        item = response['Item']

        # AI 분석 결과 조회
        analysis_id = item.get('analysis_id')
        project_info = {}
        if analysis_id:
            try:
                ai_response = ai_analysis_table.get_item(
                    Key={'analysis_id': analysis_id}
                )
                if 'Item' in ai_response:
                    project_info = ai_response['Item'].get('project_info', {})
            except:
                pass

        return {
            "success": True,
            "service": {
                "id": item.get('deployment_id'),
                "name": item.get('repository', 'unknown').split('/')[-1],
                "repository": item.get('repository'),
                "commitSha": item.get('commit_sha'),
                "branch": item.get('branch'),
                "status": item.get('status'),
                "deployedAt": item.get('timestamp'),
                "projectInfo": project_info,
                "deploymentDetails": item
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/garden")
async def get_garden_state():
    """Garden 상태 조회 (Deploygotchi)"""
    try:
        response = garden_state_table.scan()
        items = response.get('Items', [])

        return {
            "success": True,
            "count": len(items),
            "garden": items
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "garden": []
        }


@app.post("/api/services/{service_id}/restart")
async def restart_service(service_id: str):
    """서비스 재시작 (ECS 태스크 재시작)"""
    # TODO: ECS 태스크 재시작 로직 구현
    return {
        "success": False,
        "message": "Not implemented yet"
    }


@app.delete("/api/services/{service_id}")
async def delete_service(service_id: str):
    """서비스 삭제"""
    # TODO: 서비스 삭제 로직 구현 (ECS, DynamoDB 등)
    return {
        "success": False,
        "message": "Not implemented yet"
    }


@app.post("/api/deploy")
async def start_deployment(deployment: dict):
    """새 배포 시작 - GitHub Actions Workflow Dispatch 트리거"""
    try:
        repository = deployment.get('repository')
        branch = deployment.get('branch', 'main')

        if not repository:
            raise HTTPException(status_code=400, detail="Repository is required")

        # Repository URL에서 owner/repo 추출
        # 예: https://github.com/sabill123/sb_test_2 -> sabill123/sb_test_2
        if repository.startswith('http'):
            repo_parts = repository.rstrip('.git').split('/')
            owner = repo_parts[-2]
            repo_name = repo_parts[-1]
            repo_full_name = f"{owner}/{repo_name}"
        else:
            repo_full_name = repository

        # 배포 ID 생성
        import uuid
        deployment_id = str(uuid.uuid4())

        # DynamoDB에 초기 상태 저장
        deployment_table.put_item(Item={
            'id': deployment_id,
            'deployment_id': deployment_id,
            'repository': repository,
            'branch': branch,
            'status': 'triggered',
            'timestamp': datetime.now().isoformat(),
            'pusher': 'dashboard-user',
            'current_step': 0,
            'total_steps': 8
        })

        # GitHub Actions Workflow Dispatch 트리거
        # 중요: Mango의 workflow를 트리거 (사용자 repo가 아님!)
        if GITHUB_TOKEN:
            # Mango의 GitHub repo (환경변수로 재정의 가능)
            mango_repo = MANGO_REPO
            workflow_file = "deploy.yml"
            dispatch_url = f"{GITHUB_API_URL}/repos/{mango_repo}/actions/workflows/{workflow_file}/dispatches"

            headers = {
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            }

            payload = {
                "ref": "main",  # Mango repo의 main 브랜치
                "inputs": {
                    "environment": "dev",
                    "deployment_id": deployment_id,
                    "target_repository": repository,  # 사용자 repo URL
                    "target_branch": branch  # 사용자 repo 브랜치
                }
            }

            try:
                response = requests.post(dispatch_url, headers=headers, json=payload, timeout=10)

                if response.status_code == 204:
                    print(f"✅ Mango workflow triggered for user repo: {repository} ({branch})")

                    # 로그 기록
                    deployment_logs_table.put_item(Item={
                        'deployment_id': deployment_id,
                        'timestamp': datetime.now().isoformat(),
                        'message': f'Mango deployment pipeline started for {repository}',
                        'log_type': 'info',
                        'step': 1
                    })

                    return {
                        "success": True,
                        "deployment_id": deployment_id,
                        "repository": repository,
                        "branch": branch,
                        "status": "triggered",
                        "message": f"Deployment started successfully. Repository: {repository}, Branch: {branch}"
                    }
                else:
                    error_msg = f"GitHub API returned {response.status_code}: {response.text}"
                    print(f"❌ {error_msg}")

                    # 실패 상태 업데이트
                    deployment_table.update_item(
                        Key={'id': deployment_id},
                        UpdateExpression='SET #status = :status, error_message = :error',
                        ExpressionAttributeNames={'#status': 'status'},
                        ExpressionAttributeValues={
                            ':status': 'failed',
                            ':error': error_msg
                        }
                    )

                    raise HTTPException(status_code=500, detail=error_msg)

            except requests.RequestException as e:
                error_msg = f"Failed to trigger GitHub Actions: {str(e)}"
                print(f"❌ {error_msg}")

                deployment_table.update_item(
                    Key={'id': deployment_id},
                    UpdateExpression='SET #status = :status, error_message = :error',
                    ExpressionAttributeNames={'#status': 'status'},
                    ExpressionAttributeValues={
                        ':status': 'failed',
                        ':error': error_msg
                    }
                )

                raise HTTPException(status_code=500, detail=error_msg)
        else:
            # GitHub Token이 없는 경우 - 수동 배포 안내
            print("⚠️ GITHUB_TOKEN not set. Please push to GitHub to trigger deployment.")

            deployment_logs_table.put_item(Item={
                'deployment_id': deployment_id,
                'timestamp': datetime.now().isoformat(),
                'message': 'Manual deployment not available. Please push code to GitHub to trigger CI/CD pipeline.',
                'log_type': 'warning',
                'step': 0
            })

            return {
                "success": True,
                "deployment_id": deployment_id,
                "repository": repository,
                "branch": branch,
                "status": "pending",
                "message": "GITHUB_TOKEN not configured. Please push code to GitHub to trigger automatic deployment via CI/CD pipeline."
            }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Deployment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/deploy/{deployment_id}/status")
async def get_deployment_status(deployment_id: str):
    """배포 상태 조회 - DynamoDB에서 실제 로그 읽기"""
    try:
        # 배포 메타데이터 가져오기
        deployment_response = deployment_table.get_item(Key={'id': deployment_id})

        if 'Item' not in deployment_response:
            raise HTTPException(status_code=404, detail="Deployment not found")

        deployment_item = deployment_response['Item']
        status = deployment_item.get('status', 'unknown')

        # 로그 가져오기 (DynamoDB Query)
        logs_response = deployment_logs_table.query(
            KeyConditionExpression='deployment_id = :deployment_id',
            ExpressionAttributeValues={':deployment_id': deployment_id},
            ScanIndexForward=True,  # 시간순 정렬
            Limit=1000
        )

        logs = []
        current_step = 0

        for item in logs_response.get('Items', []):
            logs.append({
                'timestamp': item.get('timestamp', ''),
                'message': item.get('message', ''),
                'type': item.get('log_type', 'info')
            })

            # 현재 단계 추적
            step = int(item.get('step', 0))  # Decimal을 int로 변환
            if step > current_step:
                current_step = step

        # 진행률 계산
        progress = (float(current_step) / 8.0) * 100 if current_step > 0 else 0

        # 완료된 경우
        if status == 'success':
            progress = 100
            current_step = 8
        elif status == 'failed':
            # 실패한 경우에도 현재 단계 유지
            pass

        return {
            "success": True,
            "deployment_id": deployment_id,
            "status": status,
            "current_step": current_step,
            "total_steps": 8,
            "progress": progress,
            "logs": logs,
            "repository": deployment_item.get('repository', ''),
            "branch": deployment_item.get('branch', 'main')
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting deployment status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/deploy/complete")
async def complete_deployment(deployment_data: dict):
    """배포 완료 후 DynamoDB에 저장"""
    try:
        import uuid
        import json

        repository = deployment_data.get('repository')
        branch = deployment_data.get('branch', 'main')
        framework = deployment_data.get('framework', 'Unknown')

        if not repository:
            raise HTTPException(status_code=400, detail="Repository is required")

        # ID 생성
        service_id = str(uuid.uuid4())
        analysis_id = str(uuid.uuid4())[:16]
        timestamp = datetime.now().isoformat()

        # Repository에서 이름 추출 (owner/repo 형태)
        repo_name = repository.split('/')[-1].replace('.git', '')

        # AI 분석 결과 저장
        ai_analysis = {
            'analysis_id': analysis_id,
            'timestamp': timestamp,
            'repository': repository,
            'commit_sha': 'latest',
            'created_at': timestamp,
            'project_info': json.dumps({
                'framework': framework,
                'language': 'Python' if framework == 'FastAPI' else 'JavaScript',
                'runtime': 'Python 3.11' if framework == 'FastAPI' else 'Node.js 18',
                'port': 8000 if framework == 'FastAPI' else 3000,
                'description': f'{framework} Application'
            }),
            'confidence': '0.95',
            'recommendation': 'deploy'
        }

        # 배포 기록 저장
        deployment_record = {
            'id': service_id,
            'deployment_id': service_id,
            'repository': repository,
            'commit_sha': 'latest',
            'branch': branch,
            'status': 'success',
            'timestamp': timestamp,
            'analysis_id': analysis_id,
            'pusher': 'user',
            'deployment_url': f'http://{ALB_DNS}'
        }

        # DynamoDB에 저장
        ai_analysis_table.put_item(Item=ai_analysis)
        deployment_table.put_item(Item=deployment_record)

        return {
            "success": True,
            "service_id": service_id,
            "analysis_id": analysis_id,
            "message": "Deployment saved successfully"
        }

    except Exception as e:
        print(f"Error saving deployment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _get_service_status(status: str) -> str:
    """DynamoDB 상태를 UI 상태로 변환"""
    status_map = {
        'success': 'healthy',
        'completed': 'healthy',
        'in_progress': 'deploying',
        'deploying': 'deploying',
        'failed': 'error',
        'error': 'error'
    }
    return status_map.get(status.lower(), 'unknown')


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=3000,
        log_level='info'
    )
