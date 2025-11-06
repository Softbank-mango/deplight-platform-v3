"""ECR Pusher Module - ECR 이미지 푸시"""
import boto3
import subprocess
import base64
import os

class ECRPusher:
    def __init__(self, logger):
        self.logger = logger
        self.ecr_client = boto3.client('ecr', region_name='ap-northeast-2')
        self.ecr_registry = os.getenv('ECR_REGISTRY', '513348493870.dkr.ecr.ap-northeast-2.amazonaws.com')
        self.ecr_repository = os.getenv('ECR_REPOSITORY', 'delightful-deploy')

    def push(self, image_tag: str):
        """ECR에 이미지 푸시"""
        self.logger.log("ECR 로그인 중...", 'info', step=6)
        self._ecr_login()

        self.logger.log("이미지 푸시 중...", 'info', step=6)
        self._ecr_push(image_tag)

    def _ecr_login(self):
        """ECR 로그인"""
        try:
            # ECR 로그인 토큰 획득
            response = self.ecr_client.get_authorization_token()
            token = response['authorizationData'][0]['authorizationToken']
            endpoint = response['authorizationData'][0]['proxyEndpoint']

            username, password = base64.b64decode(token).decode('utf-8').split(':')

            # Docker 로그인
            result = subprocess.run(
                ['docker', 'login', '--username', username, '--password-stdin', endpoint],
                input=password,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                raise Exception(f"ECR login failed: {result.stderr}")

            self.logger.log("✓ ECR 인증 성공", 'success', step=6)

        except Exception as e:
            raise Exception(f"ECR login error: {str(e)}")

    def _ecr_push(self, image_tag: str):
        """ECR에 이미지 푸시"""
        image_name = f"{self.ecr_registry}/{self.ecr_repository}:{image_tag}"

        try:
            result = subprocess.run(
                ['docker', 'push', image_name],
                capture_output=True,
                text=True,
                timeout=600  # 10분
            )

            if result.returncode != 0:
                raise Exception(f"ECR push failed: {result.stderr}")

            self.logger.log("✓ ECR 푸시 완료", 'success', step=6)

        except subprocess.TimeoutExpired:
            raise Exception("ECR push timeout (10 minutes)")
        except Exception as e:
            raise Exception(f"ECR push error: {str(e)}")
