# Delightful Deploy - Demo App

A simple FastAPI demo application for testing the Delightful Deploy AI-powered deployment system.

## Description

This is a minimal FastAPI application used to demonstrate:
- Automated Docker image building
- ECR image push
- ECS deployment with Blue/Green strategy
- AI-powered code analysis
- CloudWatch monitoring
- X-Ray tracing

## Tech Stack

- **Framework**: FastAPI
- **Runtime**: Python 3.11
- **WSGI Server**: Uvicorn
- **Port**: 8000

## Endpoints

- `GET /` - Welcome message with version info
- `GET /health` - Health check endpoint
- `GET /api/status` - API status endpoint

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

The application will be available at http://localhost:8000

## Deployment

This app is designed to be deployed using Delightful Deploy:

1. Push to GitHub (main or develop branch)
2. GitHub Actions will automatically:
   - Invoke AI Analyzer Lambda
   - Build Docker image
   - Push to ECR
   - Deploy to ECS via Terraform
   - Perform Blue/Green deployment via CodeDeploy
   - Run smoke tests

## Configuration

Deployment configuration is in [.delightful.yaml](.delightful.yaml)

## Infrastructure

- **ECS Cluster**: delightful-deploy-cluster
- **ECS Service**: delightful-deploy-service
- **ALB**: delightful-deploy-alb
- **Target Groups**: Blue/Green for canary deployment
- **CloudWatch**: Logs, metrics, and dashboard
- **X-Ray**: Distributed tracing

## Monitoring

- CloudWatch Dashboard: [View Dashboard](https://console.aws.amazon.com/cloudwatch/home?region=ap-northeast-2#dashboards:name=delightful-deploy-dashboard)
- CloudWatch Logs: `/aws/ecs/delightful-deploy`
- X-Ray Service Map: Available in AWS X-Ray console

## Author

SoftBank Hackathon 2025 Team
