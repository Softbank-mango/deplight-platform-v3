"""
Git Cloner Module - GitHub 저장소 클론
"""
import subprocess
import tempfile
import os
from typing import Optional


class GitCloner:
    """GitHub 저장소 클론"""

    def __init__(self, logger):
        self.logger = logger
        self.temp_dir = None

    def clone(self, repository: str, branch: str = 'main') -> str:
        """
        저장소 클론
        Returns: 클론된 디렉토리 경로
        """
        self.temp_dir = tempfile.mkdtemp(prefix='delightful-deploy-')

        # GitHub URL 정규화
        if not repository.startswith('http'):
            repo_url = f"https://github.com/{repository}.git"
        else:
            repo_url = repository

        try:
            result = subprocess.run(
                ['git', 'clone', '--depth', '1', '--branch', branch, repo_url, self.temp_dir],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                raise Exception(f"Git clone failed: {result.stderr}")

            self.logger.log(f"✓ Repository cloned to {self.temp_dir}", 'success', step=1)
            return self.temp_dir

        except subprocess.TimeoutExpired:
            raise Exception("Git clone timeout (120s)")
        except Exception as e:
            raise Exception(f"Git clone error: {str(e)}")

    def cleanup(self):
        """임시 디렉토리 정리"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            try:
                shutil.rmtree(self.temp_dir)
                self.logger.log("✓ Cleaned up temporary files", 'info')
            except Exception as e:
                self.logger.log(f"⚠ Cleanup failed: {e}", 'warning')
