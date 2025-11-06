"""
Deployment Engine - 모든 모듈을 orchestrate
"""
from .logger import DeploymentLogger
from .modules import (
    GitCloner,
    AIAnalyzer,
    DockerBuilder,
    ECRPusher,
    TerraformRunner,
    CodeDeployManager,
    HealthChecker
)


class DeploymentEngine:
    """메인 배포 엔진 - 모든 배포 단계를 orchestrate"""

    def __init__(self, deployment_id: str, repository: str, branch: str = 'main'):
        self.deployment_id = deployment_id
        self.repository = repository
        self.branch = branch
        self.logger = DeploymentLogger(deployment_id)

        # 모듈 초기화
        self.git_cloner = GitCloner(self.logger)
        self.ai_analyzer = AIAnalyzer(self.logger)
        self.docker_builder = DockerBuilder(self.logger)
        self.ecr_pusher = ECRPusher(self.logger)
        self.terraform_runner = TerraformRunner(self.logger)
        self.codedeploy_manager = CodeDeployManager(self.logger)
        self.health_checker = HealthChecker(self.logger)

        self.repo_path = None
        self.analysis_result = None
        self.image_tag = None

    def deploy(self) -> dict:
        """전체 배포 파이프라인 실행"""
        try:
            self.logger.log(f"[{self.repository}] 배포 시작", 'info', step=1)
            self.logger.log(f"Branch: {self.branch}", 'info', step=1)

            # Step 1: Git Clone
            self.repo_path = self.git_cloner.clone(self.repository, self.branch)

            # Step 2 & 3: AI Analysis
            self.analysis_result = self.ai_analyzer.analyze(
                self.repo_path, self.repository, self.branch
            )

            # Step 4: Dockerfile 다운로드/생성
            self.ai_analyzer.download_dockerfile(self.repo_path)

            # Step 5: Docker Build
            self.image_tag = f"deploy-{self.deployment_id[:8]}"
            self.docker_builder.build(self.repo_path, self.image_tag)

            # Step 6: ECR Push
            self.ecr_pusher.push(self.image_tag)

            # Step 7: Terraform Apply + CodeDeploy
            self.terraform_runner.apply(self.image_tag)
            # self.codedeploy_manager.deploy()  # Terraform이 CodeDeploy 트리거

            # Step 8: Health Check
            alb_dns = "delightful-deploy-alb-796875577.ap-northeast-2.elb.amazonaws.com"
            self.health_checker.check(f"http://{alb_dns}/health")

            self.logger.log("", 'info', step=8)
            self.logger.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", 'success', step=8)
            self.logger.log("🎉 배포가 성공적으로 완료되었습니다!", 'success', step=8)
            self.logger.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", 'success', step=8)

            return {
                'status': 'success',
                'deployment_id': self.deployment_id,
                'analysis_id': self.analysis_result.get('analysis_id'),
                'image_tag': self.image_tag,
                'logs': self.logger.get_logs()
            }

        except Exception as e:
            self.logger.log(f"✗ 배포 실패: {str(e)}", 'error')
            raise
        finally:
            self.git_cloner.cleanup()


def deploy(deployment_id: str, repository: str, branch: str = 'main') -> dict:
    """배포 실행 (엔트리 포인트)"""
    engine = DeploymentEngine(deployment_id, repository, branch)
    return engine.deploy()
