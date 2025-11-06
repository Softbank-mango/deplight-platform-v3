#!/usr/bin/env python3
"""
GitHub Secrets 설정 스크립트
"""
import subprocess
import sys

def run_command(cmd):
    """Run shell command"""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout)
    return True

def main():
    print("🔐 Setting up GitHub Secrets...\n")

    # AWS Credentials
    aws_access_key = "AKIAXPBPUMIXHV66ZPRD"
    aws_secret_key = input("Enter AWS_SECRET_ACCESS_KEY: ").strip()

    if not aws_secret_key:
        print("❌ AWS Secret Access Key is required")
        sys.exit(1)

    # Repository
    repo = "Softbank-mango/arc_test"

    print(f"\n📦 Repository: {repo}\n")

    # Set secrets
    secrets = {
        "AWS_ACCESS_KEY_ID": aws_access_key,
        "AWS_SECRET_ACCESS_KEY": aws_secret_key,
    }

    for secret_name, secret_value in secrets.items():
        print(f"Setting {secret_name}...")
        cmd = f'gh secret set {secret_name} -b "{secret_value}" -R {repo}'
        if run_command(cmd):
            print(f"✅ {secret_name} set successfully\n")
        else:
            print(f"❌ Failed to set {secret_name}\n")

    print("✅ All secrets configured!")
    print("\n🚀 GitHub Actions workflows are ready to run:")
    print(f"   https://github.com/{repo}/actions")

if __name__ == "__main__":
    main()
