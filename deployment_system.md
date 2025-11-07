# Deployment System - v3

> **Latest Version**: v3 - GitHub Repository: https://github.com/Softbank-mango/deplight-platform-v3

## What's New in v3

### 🎨 Dashboard Improvements
- **Modern Glassmorphism UI**: Dark theme with backdrop blur effects
- **Real-time Deployment Tracking**: 8-stage progress visualization
- **Enhanced Service Cards**: Detailed deployment information with quick actions
- **Local Development**: Dashboard runs on http://localhost:3000 for development

### ⚡ Performance Optimizations
- **UV Package Manager**: 5-10x faster than pip for Python dependencies
- **BuildKit Caching**: Optimized Docker layer caching
- **AI Analysis Cache**: DynamoDB-backed cache reduces analysis time from 60s to 0.5s on cache hits
- **Deployment Times**:
  - First deployment (with AI analysis): ~60-120 seconds
  - Subsequent deployments (cache hit): ~7-10 seconds
  - 1,700% faster than target 10-minute goal

### 🏗️ Infrastructure Updates
- **Circuit Breaker Deployment**: Fast, safe deployments without CodeDeploy complexity
- **Terraform Local Mode**: Simplified infrastructure management
- **Dynamic Deployment Configuration**: Flexible blue-green or circuit breaker modes

## Core Design Points

- **GitHub → AWS Authentication**: Use GitHub OIDC with an AWS IAM role (web identity) to mint short-lived credentials. In workflows, use `aws-actions/configure-aws-credentials`. Keep long-lived secrets to a minimum.
- **Image Tag Propagation**: GitHub Actions pushes the image to ECR tagged with `<commit_sha>`. The Terraform CLI deploy step passes this value via `-var="image_tag=<commit_sha>"`, updating the ECS Task Definition.
- **Infrastructure as Source**: Place Terraform modules under the repo's `infrastructure/` directory. Use **Terraform CLI with local state or remote backend (S3 state + DynamoDB locking)** from GitHub Actions. Keep environment-specific settings (subnets, DB size, etc.) separated by variable files or workspace directories.
- **AI Analyzer Integration**: A Lambda "AI Code Analyzer" scans the codebase to infer **framework, language, port, CPU/Memory requirements, dependencies**, etc., then:
    1. Generates optimized Dockerfile automatically
    2. Caches analysis results in DynamoDB for instant redeployments
    3. Provides deployment recommendations via GitHub Actions logs
- **Rollback Strategy**:
    - With Circuit Breaker: automatic rollback on health check failure (30 seconds)
    - Manual rollback: from GitHub Actions, re-apply the previous known-good tag by running `terraform apply -var=image_tag=<previous>`
- **Observability**: CloudWatch Logs, ECS task monitoring, and ALB health checks provide comprehensive visibility. Dashboard displays real-time deployment status and service health.

## Architecture Diagram (ASCII)

```
┌───────────────────────────────────────────────────────────────────────────┐
│                              Developer                                    │
│                           (write code & push)                             │
└───────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                   ┌────────────────────────────────────┐
                   │         GitHub Repository          │
                   │     (includes .delightful.yaml)    │
                   └────────────────────────────────────┘
                                      │
                                      ▼
             ┌──────────────────────────────────────────────────────┐
             │                   GitHub Actions                     │
             │------------------------------------------------------│
             │ 1) Analyzer Workflow                                 │
             │    - Invoke Lambda (AI Code Analyzer)                │
             │    - Analyze lang/deps/traffic                       │
             │    - PR comments & tfvars suggestions                │
             │                                                      │
             │ 2) CI/CD Workflow                                    │
             │    - Build / Test / SCA                              │
             │    - Push image to ECR                               │
             │    - Terraform Apply (CLI, passes image_tag)         │
             │    - Trigger CodeDeploy Blue/Green                   │
             │    - Smoke tests & Slack notifications               │
             └──────────────────────────────────────────────────────┘
                                      │
                                      ▼
                   ┌────────────────────────────────┐
                   │   Terraform Pipeline (CLI)     │
                   │ - Remote state (S3/Dynamo)     │
                   │ - Applies ECS / CodeDeploy     │
                   │ - Configures CloudWatch/X-Ray  │
                   └────────────────────────────────┘
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                                   AWS                                     │
│---------------------------------------------------------------------------│
│   ┌──────────────┐     ┌──────────────┐     ┌─────────────────┐           │
│   │     ECS      │◄───►│     ALB      │◄───►│    CodeDeploy   │◄──┐       │
│   │ (TaskDef: TF)│     │ (Blue/Green) │     │(deploy/rollback)│   │       │
│   └──────────────┘     └──────────────┘     └─────────────────┘   │       │
│          ▲                                           │            │       │
│          │                                           │            │       │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐      │       │
│   │     RDS      │     │  ElastiCache │     │  CloudWatch  │  ◄───┘       │
│   │     (DB)     │     │    (Redis)   │     │    + X-Ray   │              │
│   └──────────────┘     └──────────────┘     └──────────────┘              │
└───────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                     ┌───────────────────────────┐
                     │  Slack / Dashboard Links  │
                     │ (deploy results & metrics)│
                     └───────────────────────────┘

```

## v3 Architecture Flow

```
Developer submits GitHub URL via Dashboard
              ↓
┌─────────────────────────────────────────┐
│       Dashboard (FastAPI + React)       │
│  - Glassmorphism UI                     │
│  - Real-time progress tracking          │
│  - Service management                   │
│  Running on: http://localhost:3000      │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│        GitHub Actions Triggered         │
│  1. Checkout code                       │
│  2. Invoke Lambda AI Analyzer           │
│  3. Build Docker (UV + BuildKit)        │
│  4. Push to ECR                         │
│  5. Update ECS (Circuit Breaker)        │
│  6. Health check & verify               │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│      AWS Lambda - AI Analyzer           │
│  - Framework detection                  │
│  - Dockerfile generation                │
│  - DynamoDB cache (0.5s redeployment)   │
│  - Resource recommendations             │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│            AWS ECS Fargate              │
│  Cluster: delightful-deploy-cluster     │
│  Service: delightful-deploy-service     │
│  Tasks: 2-4 (auto-scaling)              │
│  Region: ap-northeast-2 (Seoul)         │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│     Application Load Balancer           │
│  DNS: delightful-deploy-alb-            │
│       796875577.ap-northeast-2.         │
│       elb.amazonaws.com                 │
│  Health Check: /health every 10s        │
└─────────────────────────────────────────┘
              ↓
         Live Application!
```

## Summary Matrix

| Layer | Components | Role | v3 Enhancements |
| --- | --- | --- | --- |
| **UI Layer** | Dashboard (React + FastAPI) | Modern UI for deployment management | Glassmorphism design, real-time progress, local dev mode |
| **Developer Layer** | GitHub Repo | Submit code via dashboard | Supports both organization and personal repos |
| **Automation Layer** | GitHub Actions | Build/test/deploy automation | UV package manager, BuildKit optimization |
| **Infrastructure Layer** | Terraform (Local/Remote) | Manages ECS, ALB, Circuit Breaker | Dynamic deployment modes, simplified config |
| **AWS Execution Layer** | ECS + ALB + CloudWatch | Runs services with auto-scaling | Circuit Breaker for fast deployments (7-10s) |
| **Analysis Layer** | AI Code Analyzer (Lambda) | Framework detection & Dockerfile generation | DynamoDB cache for instant redeployments |

## Performance Metrics (v3)

| Metric | First Deployment | Redeployment (Cache Hit) | Improvement |
| --- | --- | --- | --- |
| AI Analysis | 60s | 0.5s | 120x faster |
| Docker Build | 30s | 0.8s | 37x faster |
| ECS Update | 30s | 2.8s | 10x faster |
| **Total Time** | **~120s** | **~7s** | **17x faster** |
| **vs 10-min goal** | 5x faster | **85x faster** | **1,700% improvement** |

## Cost Analysis (v3)

| Resource | Cost per Deployment | Monthly (100 deployments) |
| --- | --- | --- |
| Lambda AI Analyzer | $0.001 | $0.10 |
| ECR Storage | $0.001 | $0.10 |
| ECS Fargate (per hour) | $0.004 | $3.00 (720 hours) |
| ALB (per hour) | $0.025 | $18.00 (720 hours) |
| **Total** | **$0.004/deployment** | **~$21/month** |
