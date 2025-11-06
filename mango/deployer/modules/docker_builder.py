"""Docker Builder Module - Docker 이미지 빌드"""
import subprocess
import os

class DockerBuilder:
    def __init__(self, logger):
        self.logger = logger
        self.ecr_registry = os.getenv('ECR_REGISTRY', '513348493870.dkr.ecr.ap-northeast-2.amazonaws.com')
        self.ecr_repository = os.getenv('ECR_REPOSITORY', 'delightful-deploy')

    def build(self, repo_path: str, image_tag: str) -> str:
        """Docker 이미지 빌드"""
        image_name = f"{self.ecr_registry}/{self.ecr_repository}:{image_tag}"

        self.logger.log("Docker 이미지 빌드 시작...", 'info', step=5)
        self.logger.log(f"이미지 태그: {image_tag}", 'info', step=5)

        try:
            # Docker 빌드
            result = subprocess.run(
                ['docker', 'build', '-t', image_name, '.'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=600  # 10분
            )

            if result.returncode != 0:
                raise Exception(f"Docker build failed: {result.stderr}")

            self.logger.log("✓ 이미지 빌드 완료", 'success', step=5)
            return image_tag

        except subprocess.TimeoutExpired:
            raise Exception("Docker build timeout (10 minutes)")
        except Exception as e:
            raise Exception(f"Docker build error: {str(e)}")
