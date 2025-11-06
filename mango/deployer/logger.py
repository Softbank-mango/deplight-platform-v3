"""
Deployment Logger - DynamoDB에 실시간 로그 저장
"""
import boto3
from datetime import datetime
from typing import List, Dict


class DeploymentLogger:
    """배포 로그를 DynamoDB에 실시간으로 저장"""

    def __init__(self, deployment_id: str, table_name: str = 'delightful-deploy-deployment-logs'):
        self.deployment_id = deployment_id
        self.table = boto3.resource('dynamodb', region_name='ap-northeast-2').Table(table_name)
        self.logs = []

    def log(self, message: str, log_type: str = 'info', step: int = None):
        """로그 메시지 추가 및 DynamoDB 저장"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'message': message,
            'type': log_type
        }

        if step:
            log_entry['step'] = step

        self.logs.append(log_entry)

        # DynamoDB에 저장
        try:
            self.table.put_item(Item={
                'deployment_id': self.deployment_id,
                'timestamp': timestamp,
                'log_type': log_type,
                'message': message,
                'step': step or 0
            })
        except Exception as e:
            print(f"Failed to save log to DynamoDB: {e}")

        print(f"[{timestamp}] [{log_type.upper()}] {message}")

    def get_logs(self) -> List[Dict]:
        """모든 로그 반환"""
        return self.logs
