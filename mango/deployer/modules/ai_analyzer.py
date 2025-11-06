"""AI Analyzer Module - Lambda 함수 호출"""
import boto3
import json
import os
from datetime import datetime

class AIAnalyzer:
    def __init__(self, logger):
        self.logger = logger
        self.lambda_client = boto3.client('lambda', region_name='ap-northeast-2')
        self.s3_client = boto3.client('s3', region_name='ap-northeast-2')
        self.lambda_function_name = os.getenv('AI_ANALYZER_LAMBDA', 'delightful-deploy-ai-analyzer')
        self.s3_bucket = os.getenv('S3_BUCKET', 'delightful-deploy-artifacts-1762083190')
        self.analysis_id = None
        self.project_info = None

    def analyze(self, repo_path: str, repository: str, branch: str) -> dict:
        """Lambda 함수로 AI 분석 실행"""
        # 파일 목록 가져오기
        file_list = []
        for root, dirs, files in os.walk(repo_path):
            # .git 디렉토리 제외
            dirs[:] = [d for d in dirs if d != '.git']
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), repo_path)
                file_list.append(rel_path)

        # README 읽기
        readme_content = ""
        readme_files = ['README.md', 'readme.md', 'README', 'README.txt']
        for readme_file in readme_files:
            readme_path = os.path.join(repo_path, readme_file)
            if os.path.exists(readme_path):
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        readme_content = f.read()
                    break
                except:
                    pass

        # Lambda 페이로드
        payload = {
            'repository': repository,
            'commit_sha': 'latest',
            'branch': branch,
            'pusher': 'dashboard-user',
            'timestamp': datetime.now().isoformat(),
            'file_list': file_list[:100],  # 최대 100개
            'readme_content': readme_content[:3000] if readme_content else ""
        }

        self.logger.log("Lambda 함수 호출 중...", 'info', step=2)

        try:
            response = self.lambda_client.invoke(
                FunctionName=self.lambda_function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )

            response_payload = json.loads(response['Payload'].read())

            if response['StatusCode'] != 200:
                raise Exception(f"Lambda invocation failed: {response_payload}")

            body = json.loads(response_payload['body'])
            self.analysis_id = body['analysis_id']
            self.project_info = body['project_info']

            self.logger.log(f"✓ AI 분석 완료 (ID: {self.analysis_id})", 'success', step=2)

            # Step 3: 프로젝트 정보 출력
            self._log_project_info()

            return {
                'analysis_id': self.analysis_id,
                'project_info': self.project_info
            }

        except Exception as e:
            raise Exception(f"Lambda invocation error: {str(e)}")

    def _log_project_info(self):
        """프로젝트 정보 출력"""
        if not self.project_info:
            return

        framework = self.project_info.get('primary_framework',
                                          self.project_info.get('primary_language', 'Unknown'))
        language = self.project_info.get('primary_language', 'Unknown')
        runtime = self.project_info.get('runtime', 'Unknown')
        port = self.project_info.get('app_port', 8000)

        self.logger.log("프로젝트 타입 감지 중...", 'info', step=3)
        self.logger.log(f"감지됨: {framework} ({language})", 'success', step=3)
        self.logger.log(f"Runtime: {runtime}", 'info', step=3)
        self.logger.log(f"Port: {port}", 'info', step=3)

    def download_dockerfile(self, repo_path: str) -> str:
        """S3에서 생성된 Dockerfile 다운로드"""
        if not self.analysis_id:
            raise Exception("Analysis ID not available")

        s3_key = f"analysis/{self.analysis_id}/dockerfile"
        dockerfile_path = os.path.join(repo_path, 'Dockerfile')

        try:
            self.s3_client.download_file(self.s3_bucket, s3_key, dockerfile_path)
            self.logger.log("✓ Dockerfile 다운로드 완료", 'success', step=4)
            self.logger.log("✓ 배포 설정 준비 완료", 'success', step=4)
            return dockerfile_path
        except Exception as e:
            # Fallback: 기본 Dockerfile 생성
            self.logger.log(f"⚠ S3에서 Dockerfile 다운로드 실패, 기본 Dockerfile 생성", 'warning', step=4)
            return self._create_fallback_dockerfile(repo_path)

    def _create_fallback_dockerfile(self, repo_path: str) -> str:
        """기본 Dockerfile 생성"""
        port = self.project_info.get('app_port', 8000) if self.project_info else 8000

        dockerfile_content = f"""FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt* ./
RUN pip install --no-cache-dir -r requirements.txt || echo "No requirements.txt"

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE {port}

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \\
    CMD curl -f http://localhost:{port}/health || exit 1

CMD ["python", "main.py"]
"""

        dockerfile_path = os.path.join(repo_path, 'Dockerfile')
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)

        self.logger.log("✓ Fallback Dockerfile 생성 완료", 'success', step=4)
        return dockerfile_path
