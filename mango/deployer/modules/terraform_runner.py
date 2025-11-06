"""Terraform Runner Module - ECS 서비스 업데이트"""
import boto3
import os
import time

class TerraformRunner:
    def __init__(self, logger):
        self.logger = logger
        self.ecs_client = boto3.client('ecs', region_name='ap-northeast-2')
        self.ecs_cluster = os.getenv('ECS_CLUSTER', 'delightful-deploy-cluster')
        self.ecs_service = os.getenv('ECS_SERVICE', 'delightful-deploy-service')
        self.ecr_registry = os.getenv('ECR_REGISTRY', '513348493870.dkr.ecr.ap-northeast-2.amazonaws.com')
        self.ecr_repository = os.getenv('ECR_REPOSITORY', 'delightful-deploy')

    def apply(self, image_tag: str):
        """ECS 서비스 업데이트"""
        try:
            # 새 태스크 정의 생성
            self.logger.log("새 태스크 정의 등록...", 'info', step=7)

            # 기존 태스크 정의 가져오기
            response = self.ecs_client.describe_services(
                cluster=self.ecs_cluster,
                services=[self.ecs_service]
            )

            if not response['services']:
                raise Exception(f"ECS service not found: {self.ecs_service}")

            current_task_def_arn = response['services'][0]['taskDefinition']

            # 태스크 정의 읽기
            task_def_response = self.ecs_client.describe_task_definition(
                taskDefinition=current_task_def_arn
            )

            task_def = task_def_response['taskDefinition']

            # 새 이미지로 업데이트
            new_containers = []
            for container in task_def['containerDefinitions']:
                container['image'] = f"{self.ecr_registry}/{self.ecr_repository}:{image_tag}"
                new_containers.append(container)

            # 새 태스크 정의 등록
            new_task_def = self.ecs_client.register_task_definition(
                family=task_def['family'],
                taskRoleArn=task_def.get('taskRoleArn', ''),
                executionRoleArn=task_def.get('executionRoleArn', ''),
                networkMode=task_def['networkMode'],
                containerDefinitions=new_containers,
                requiresCompatibilities=task_def['requiresCompatibilities'],
                cpu=task_def['cpu'],
                memory=task_def['memory']
            )

            new_task_def_arn = new_task_def['taskDefinition']['taskDefinitionArn']

            self.logger.log(f"✓ 새 태스크 정의 등록 완료", 'success', step=7)
            self.logger.log("서비스 업데이트 중...", 'info', step=7)

            # 서비스 업데이트
            self.ecs_client.update_service(
                cluster=self.ecs_cluster,
                service=self.ecs_service,
                taskDefinition=new_task_def_arn,
                forceNewDeployment=True
            )

            self.logger.log("✓ ECS 서비스 업데이트 시작", 'success', step=7)

            # 배포 완료 대기
            for i in range(30):  # 최대 5분
                time.sleep(10)
                response = self.ecs_client.describe_services(
                    cluster=self.ecs_cluster,
                    services=[self.ecs_service]
                )

                service = response['services'][0]
                running_count = service['runningCount']
                desired_count = service['desiredCount']

                if running_count == desired_count and running_count > 0:
                    self.logger.log(f"✓ 새 태스크 실행 중 ({running_count}/{desired_count})", 'success', step=7)
                    break

                if i % 3 == 0:
                    self.logger.log(f"배포 진행 중... ({running_count}/{desired_count})", 'info', step=7)

        except Exception as e:
            raise Exception(f"ECS update error: {str(e)}")
