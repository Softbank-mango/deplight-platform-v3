#!/usr/bin/env python3
"""
GitHub 리포지토리 생성 및 Push 자동화 스크립트
"""
import os
import sys
import subprocess
import requests

def run_command(cmd, cwd=None):
    """Run shell command and return output"""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        cwd=cwd
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None
    return result.stdout.strip()

def create_github_repo(token, repo_name, description, is_private=False):
    """Create GitHub repository using API"""
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": repo_name,
        "description": description,
        "private": is_private,
        "auto_init": False
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        repo_data = response.json()
        print(f"✅ Repository created: {repo_data['html_url']}")
        return repo_data['clone_url'], repo_data['html_url']
    elif response.status_code == 422:
        print(f"⚠️  Repository '{repo_name}' already exists")
        # Get existing repo info
        user_response = requests.get("https://api.github.com/user", headers=headers)
        username = user_response.json()['login']
        return f"https://github.com/{username}/{repo_name}.git", f"https://github.com/{username}/{repo_name}"
    else:
        print(f"❌ Failed to create repository: {response.status_code}")
        print(response.json())
        return None, None

def main():
    # GitHub Personal Access Token
    # 환경 변수나 직접 입력
    token = os.getenv('GITHUB_TOKEN')

    if not token:
        print("❌ GITHUB_TOKEN 환경 변수가 설정되지 않았습니다.")
        print("\n다음 중 하나를 선택하세요:")
        print("1. 환경 변수 설정: export GITHUB_TOKEN='your_token_here'")
        print("2. 토큰을 직접 입력하세요:")
        token = input("GitHub Token: ").strip()

        if not token:
            print("❌ 토큰이 필요합니다. 종료합니다.")
            sys.exit(1)

    # Repository configuration
    repo_name = "delightful-deploy-demo"
    description = "🚀 Delightful Deploy - AI-powered deployment automation demo app"

    print(f"\n📦 Creating repository: {repo_name}")
    clone_url, html_url = create_github_repo(token, repo_name, description, is_private=False)

    if not clone_url:
        sys.exit(1)

    # Setup git remote
    print("\n🔗 Setting up git remote...")

    # Remove existing remote if any
    run_command("git remote remove origin 2>/dev/null")

    # Add new remote
    # Use HTTPS with token authentication
    username_response = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"token {token}"}
    )
    username = username_response.json()['login']
    auth_url = clone_url.replace("https://", f"https://{username}:{token}@")

    result = run_command(f"git remote add origin {auth_url}")
    if result is not None:
        print("✅ Remote added")

    # Push to GitHub
    print("\n⬆️  Pushing to GitHub...")
    result = run_command("git push -u origin main")

    if result is not None:
        print("✅ Successfully pushed to GitHub!")
        print(f"\n🎉 Repository URL: {html_url}")
        print(f"\n🤖 GitHub Actions workflows will start automatically:")
        print(f"   - AI Analyzer: {html_url}/actions")
        print(f"   - CI/CD Pipeline: {html_url}/actions")
    else:
        print("❌ Failed to push to GitHub")
        sys.exit(1)

if __name__ == "__main__":
    main()
