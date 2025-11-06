"""Health Checker Module - 서비스 Health Check"""
import requests
import time
import os

class HealthChecker:
    def __init__(self, logger):
        self.logger = logger

    def check(self, url: str = None, retries: int = 10):
        """Health check 수행"""
        # ALB DNS 가져오기
        if not url:
            alb_dns = os.getenv('ALB_DNS', 'delightful-deploy-alb-796875577.ap-northeast-2.elb.amazonaws.com')
            url = f"http://{alb_dns}/health"

        self.logger.log("Health Check 시작...", 'info', step=8)
        self.logger.log(f"Health check URL: {url}", 'info', step=8)

        # 10번 시도 (30초)
        for i in range(retries):
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    self.logger.log(f"✓ Health check 성공 ({response.status_code})", 'success', step=8)
                    return True
            except Exception as e:
                pass

            if i < retries - 1:
                self.logger.log(f"Health check 재시도 중... ({i+1}/{retries})", 'info', step=8)
                time.sleep(3)

        # 실패해도 경고만 (이미 배포는 완료됨)
        self.logger.log("⚠ Health check timeout (서비스는 배포되었으나 health check 실패)", 'warning', step=8)
        return False
