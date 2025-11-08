#!/usr/bin/env python3
"""
Check ECR repository for Docker images
"""
import boto3

def check_ecr_images():
    """Check if Docker images exist in ECR"""

    ecr = boto3.client('ecr', region_name='ap-northeast-2')

    print("=" * 80)
    print("ECR REPOSITORY CHECK")
    print("=" * 80)
    print()

    try:
        # List images in repository
        images = ecr.describe_images(
            repositoryName='delightful-deploy'
        )

        if images.get('imageDetails'):
            print(f"✅ Found {len(images['imageDetails'])} images in ECR")
            print()

            for img in images['imageDetails']:
                tags = img.get('imageTags', ['<untagged>'])
                size_mb = img.get('imageSizeInBytes', 0) / (1024 * 1024)
                pushed_at = img.get('imagePushedAt', 'Unknown')

                print(f"   Image:")
                print(f"      Tags: {', '.join(tags)}")
                print(f"      Size: {size_mb:.2f} MB")
                print(f"      Pushed: {pushed_at}")
                print(f"      Digest: {img.get('imageDigest', 'N/A')[:20]}...")
                print()

        else:
            print("❌ No images found in ECR repository!")
            print()
            print("This is why ECS tasks are failing to start.")
            print()
            print("To fix this, you need to:")
            print("1. Build a Docker image for your application")
            print("2. Push it to ECR: 513348493870.dkr.ecr.ap-northeast-2.amazonaws.com/delightful-deploy:latest")
            print()
            print("Example commands:")
            print("  docker build -t delightful-deploy .")
            print("  aws ecr get-login-password --region ap-northeast-2 | \\")
            print("    docker login --username AWS --password-stdin 513348493870.dkr.ecr.ap-northeast-2.amazonaws.com")
            print("  docker tag delightful-deploy:latest 513348493870.dkr.ecr.ap-northeast-2.amazonaws.com/delightful-deploy:latest")
            print("  docker push 513348493870.dkr.ecr.ap-northeast-2.amazonaws.com/delightful-deploy:latest")
            print()

    except ecr.exceptions.RepositoryNotFoundException:
        print("❌ ECR repository 'delightful-deploy' not found!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    check_ecr_images()
