# Deplight Platform - v3

> **🚀 Ultra-fast Serverless Deployment Platform**
> Deploy any GitHub repository to AWS in 7-120 seconds with AI-powered optimization

[![GitHub](https://img.shields.io/badge/GitHub-v3-blue)](https://github.com/Softbank-mango/deplight-platform-v3)
[![AWS](https://img.shields.io/badge/AWS-ECS%20Fargate-orange)](https://aws.amazon.com/fargate/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## What's New in v3

### 🎨 Modern Dashboard
- **Glassmorphism UI**: Sleek dark theme with backdrop blur effects
- **Real-time Tracking**: 8-stage deployment progress visualization
- **Local Development**: Run on http://localhost:3000

### ⚡ Performance Breakthrough
- **7-second redeployments** (with cache hit)
- **1,700% faster** than 10-minute target goal
- **UV Package Manager**: 5-10x faster than pip
- **DynamoDB Cache**: AI analysis from 60s to 0.5s

### 🏗️ Infrastructure Improvements
- **Circuit Breaker**: Fast, safe deployments
- **Auto Rollback**: 30-second automatic recovery
- **Terraform Local/Remote**: Flexible state management

## Quick Start

### Dashboard (Local)
```bash
# Clone repository
git clone https://github.com/Softbank-mango/deplight-platform-v3
cd deplight-platform/mango/dashboard

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run dashboard
uvicorn api.main:app --host 0.0.0.0 --port 3000 --reload

# Access
open http://localhost:3000
```

### Deploy an App
1. Open Dashboard: http://localhost:3000
2. Click "새 배포" (New Deployment)
3. Enter GitHub URL: `https://github.com/your-org/your-app`
4. Wait 7-120 seconds
5. Done! Access at: `http://delightful-deploy-alb-796875577.ap-northeast-2.elb.amazonaws.com/`

## Deployment System Overview

### Architecture Flow
```
Developer (GitHub URL)
    ↓
Dashboard (Glassmorphism UI)
    ↓
GitHub Actions (OIDC Auth)
    ↓
Lambda AI Analyzer (Framework Detection + Dockerfile Generation)
    ↓
Docker Build (UV + BuildKit)
    ↓
ECR (Image Storage)
    ↓
ECS Fargate (Circuit Breaker Deployment)
    ↓
ALB (Load Balancer)
    ↓
Live Application!
```

### Key Technologies
- **Frontend**: React 18, Tailwind CSS, Glassmorphism design
- **Backend**: FastAPI, Python 3.11+
- **AI**: GPT-5 for code analysis, DynamoDB caching
- **Container**: Docker with UV package manager
- **Cloud**: AWS ECS Fargate, ALB, Lambda
- **IaC**: Terraform with Circuit Breaker
- **CI/CD**: GitHub Actions with OIDC

## Repository Layout (v3)
```text
deplight-platform/
├─ mango/
│  ├─ dashboard/                    # Dashboard UI/API
│  │  ├─ api/                       # FastAPI backend
│  │  │  ├─ main.py                 # API routes
│  │  │  └─ models.py               # Data models
│  │  ├─ static/
│  │  │  └─ index.html              # Glassmorphism UI
│  │  ├─ requirements.txt           # Python dependencies
│  │  ├─ Dockerfile                 # UV-optimized
│  │  └─ venv/                      # Python virtual env
│  ├─ lambda/
│  │  └─ ai_code_analyzer/          # AI analysis Lambda
│  │     ├─ handler.py              # Main handler
│  │     ├─ generators/             # Dockerfile generators
│  │     └─ templates/              # Framework templates
│  ├─ infrastructure/
│  │  └─ terraform/                 # IaC
│  │     ├─ main.tf
│  │     ├─ ecs.tf                  # Circuit Breaker config
│  │     ├─ lambda.tf
│  │     └─ variables.tf
│  └─ scripts/
│     ├─ deploy_dashboard.sh        # Full deployment
│     └─ deploy_dashboard_simple.py # Quick redeploy
├─ docs/
│  ├─ deployment_system.md          # Architecture (v3)
│  ├─ README_DEPLOYMENT_GUIDE.md    # User guide (v3)
│  ├─ GITHUB_REPOSITORY_SCENARIOS.md # Repo scenarios
│  └─ DASHBOARD_DEPLOYMENT.md       # Dashboard deploy guide
├─ test/
│  └─ demo_app/                     # Test applications
│     ├─ fastapi-ecommerce/
│     ├─ express-todo/
│     └─ streamlit-dashboard/
└─ .github/
   └─ workflows/
      ├─ deploy.yml                 # Main deployment
      └─ deploy-dashboard.yml       # Dashboard deployment
```

## Performance Metrics

| Metric | First Deploy | Redeploy (Cache) | Improvement |
|--------|-------------|------------------|-------------|
| AI Analysis | 60s | 0.5s | 120x faster |
| Docker Build | 30s | 0.8s | 37x faster |
| ECS Update | 30s | 2.8s | 10x faster |
| **Total** | **~120s** | **~7s** | **17x faster** |

## Cost Analysis

| Resource | Cost/Deploy | Monthly (100 deploys) |
|----------|-------------|----------------------|
| Lambda AI | $0.001 | $0.10 |
| ECR Storage | $0.001 | $0.10 |
| ECS Fargate | $0.004/hr | $3.00 (720hrs) |
| ALB | $0.025/hr | $18.00 (720hrs) |
| **Total** | **$0.004** | **~$21/month** |

## Supported Frameworks

### Backend
- ✅ FastAPI (Python)
- ✅ Express.js (Node.js)
- ✅ Django (Python)
- ✅ Flask (Python)
- ✅ NestJS (Node.js)

### Frontend
- ✅ React
- ✅ Next.js
- ✅ Streamlit
- ✅ Vue.js
- ✅ Static HTML

### Auto-Detection
The AI analyzer automatically detects:
- Framework and language
- Port configuration
- CPU/Memory requirements
- Dependencies
- Health check endpoints

## Documentation

### Essential Guides
1. **[Deployment Guide](README_DEPLOYMENT_GUIDE.md)**: Complete deployment walkthrough
2. **[Architecture](deployment_system.md)**: System design and v3 improvements
3. **[GitHub Scenarios](docs/GITHUB_REPOSITORY_SCENARIOS.md)**: Organization vs personal repos
4. **[Dashboard Deployment](docs/DASHBOARD_DEPLOYMENT.md)**: Dashboard-specific deployment

### Quick Links
- **Dashboard**: http://localhost:3000
- **Production ALB**: http://delightful-deploy-alb-796875577.ap-northeast-2.elb.amazonaws.com/
- **GitHub v3**: https://github.com/Softbank-mango/deplight-platform-v3
- **AWS Region**: ap-northeast-2 (Seoul)

## Getting Started

### Prerequisites
- Python 3.11+
- AWS CLI configured
- Docker (for local testing)
- GitHub account

### Local Development
```bash
# 1. Setup Dashboard
cd mango/dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --host 0.0.0.0 --port 3000 --reload

# 2. Access Dashboard
open http://localhost:3000

# 3. Deploy an app
# Enter GitHub URL in dashboard UI
# Watch real-time progress tracking
# Access deployed app via ALB URL
```

### Production Deployment
See [DASHBOARD_DEPLOYMENT.md](docs/DASHBOARD_DEPLOYMENT.md) for:
- GitHub Actions deployment
- AWS infrastructure setup
- Terraform configuration
- Troubleshooting

## Features

### Dashboard Features
- 🎨 **Modern UI**: Glassmorphism dark theme
- 📊 **Real-time Tracking**: 8-stage deployment visualization
- 🚀 **Quick Actions**: URL copy, health check, app launch
- 📋 **Service Cards**: Detailed deployment information
- 🔄 **Auto-refresh**: Live status updates

### Deployment Features
- ⚡ **Ultra-fast**: 7-second redeployments
- 🧠 **AI-powered**: Automatic framework detection
- 🔒 **Zero-downtime**: Circuit breaker deployment
- 🔄 **Auto-rollback**: 30-second recovery
- 📦 **Smart caching**: DynamoDB + Docker layers
- 🏗️ **Auto-scaling**: 2-4 tasks based on load

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- **Issues**: https://github.com/Softbank-mango/deplight-platform-v3/issues
- **Documentation**: See `/docs` directory
- **Email**: support@deplight.com

---

**Built with ❤️ by the Softbank Mango Team**

*v3 - Making deployment delightful, one commit at a time* 🚀
