# 🏗️ Deployment Architecture - 배포된 서비스는 어디에?

## 📍 **배포된 서비스의 실제 위치**

사용자가 GitHub 저장소를 배포하면, 다음과 같은 AWS 인프라에 배포됩니다:

```
[User's GitHub Repo]
        ↓
   [Deplight Platform]
        ↓
   ╔═══════════════════════════════════════════╗
   ║  AWS 인프라 (ap-northeast-2, Seoul)       ║
   ╠═══════════════════════════════════════════╣
   ║                                           ║
   ║  ┌─────────────────────────────────────┐  ║
   ║  │  Application Load Balancer (ALB)    │  ║
   ║  │  Public DNS:                        │  ║
   ║  │  delightful-deploy-alb-796875577     │  ║
   ║  │  .ap-northeast-2.elb.amazonaws.com  │  ║
   ║  └─────────────────────────────────────┘  ║
   ║              ↓                            ║
   ║  ┌─────────────────────────────────────┐  ║
   ║  │  ECS Fargate Cluster                │  ║
   ║  │  • Cluster: delightful-deploy-      │  ║
   ║  │             cluster                 │  ║
   ║  │  • Service: delightful-deploy-      │  ║
   ║  │             service                 │  ║
   ║  │  • Tasks: 2-4 running containers    │  ║
   ║  └─────────────────────────────────────┘  ║
   ║              ↓                            ║
   ║  ┌─────────────────────────────────────┐  ║
   ║  │  Docker Container (Your App)        │  ║
   ║  │  • Image from ECR                   │  ║
   ║  │  • Port: 8000 (or AI-detected)      │  ║
   ║  │  • Auto-scaling: 2-4 tasks          │  ║
   ║  └─────────────────────────────────────┘  ║
   ║                                           ║
   ╚═══════════════════════════════════════════╝
```

---

## 🌐 **사용자가 접속하는 URL**

### **1. 메인 ALB URL** (공통 엔트리포인트)
```
http://delightful-deploy-alb-796875577.ap-northeast-2.elb.amazonaws.com
```

### **2. 배포된 서비스별 접근**

현재 아키텍처에서는 **하나의 ALB가 하나의 ECS 서비스를 가리킵니다**.

#### **문제점**:
- 모든 사용자 앱이 **같은 ECS 서비스**에 배포됨
- 새로운 배포가 이전 배포를 **덮어씀**
- 여러 앱을 동시에 호스팅할 수 없음

#### **해결 방안 (Multi-Service 지원)**:

##### **Option 1: Path-Based Routing** (권장)
```
ALB Listener Rules:
- /app1/*  →  ECS Service: app1
- /app2/*  →  ECS Service: app2
- /app3/*  →  ECS Service: app3
```

**URL 예시**:
```
http://delightful-deploy-alb.../app1/
http://delightful-deploy-alb.../app2/health
http://delightful-deploy-alb.../app3/docs
```

##### **Option 2: Host-Based Routing**
```
ALB Listener Rules:
- app1.deplight.com  →  ECS Service: app1
- app2.deplight.com  →  ECS Service: app2
```

**URL 예시**:
```
http://app1.deplight.com/
http://app2.deplight.com/docs
```

##### **Option 3: Per-Service ALB** (비용 증가)
```
각 배포마다 독립 ALB 생성:
- app1-alb-xxx.amazonaws.com
- app2-alb-xxx.amazonaws.com
```

---

## 🎯 **현재 구현 상태**

### **Single-Service Architecture** ❌
```
현재:
- 1 ALB
- 1 ECS Service
- 1 Target Group

문제:
- 새 배포 시 이전 앱 교체됨
- 여러 앱 동시 호스팅 불가
```

### **Multi-Service Architecture 필요** ✅
```
개선:
- 1 ALB (공통)
- N ECS Services (앱마다)
- N Target Groups
- Path/Host 기반 라우팅
```

---

## 🔧 **Multi-Service 지원 구현 계획**

### **Step 1: Terraform 수정**

```hcl
# 앱마다 독립 ECS Service 생성
resource "aws_ecs_service" "app" {
  for_each = var.deployed_apps

  name    = "${var.app_name}-${each.key}"
  cluster = aws_ecs_cluster.main.id
  # ...
}

# 앱마다 Target Group 생성
resource "aws_ecs_target_group" "app" {
  for_each = var.deployed_apps

  name = "${var.app_name}-${each.key}-tg"
  # ...
}

# Path 기반 라우팅 규칙
resource "aws_lb_listener_rule" "app" {
  for_each = var.deployed_apps

  listener_arn = aws_lb_listener.http.arn
  priority     = each.value.priority

  condition {
    path_pattern {
      values = ["/${each.key}/*"]
    }
  }

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app[each.key].arn
  }
}
```

### **Step 2: Dashboard URL 매핑**

```javascript
// 앱 이름 → URL 매핑
function getServiceUrl(appName) {
    const ALB_DNS = 'delightful-deploy-alb-796875577.ap-northeast-2.elb.amazonaws.com';
    return `http://${ALB_DNS}/${appName}/`;
}

// 예시:
getServiceUrl('fastapi-demo')
// → http://delightful-deploy-alb.../fastapi-demo/
```

---

## 📊 **현재 vs 개선 후**

### **현재 (Single-Service)**
```
User deploys "app1"
  → Replaces everything
  → URL: http://ALB/

User deploys "app2"
  → Replaces "app1" ❌
  → URL: http://ALB/  (now shows app2)
```

### **개선 후 (Multi-Service)**
```
User deploys "app1"
  → Creates ECS Service: app1
  → URL: http://ALB/app1/

User deploys "app2"
  → Creates ECS Service: app2 (parallel)
  → URL: http://ALB/app2/

Both apps running simultaneously! ✅
```

---

## 🎯 **Dashboard에서 보여줄 정보**

```javascript
{
  "services": [
    {
      "name": "fastapi-demo",
      "url": "http://delightful-deploy-alb.../fastapi-demo/",
      "status": "healthy",
      "endpoints": {
        "root": "http://ALB/fastapi-demo/",
        "health": "http://ALB/fastapi-demo/health",
        "docs": "http://ALB/fastapi-demo/docs"
      },
      "container": {
        "cluster": "delightful-deploy-cluster",
        "service": "delightful-deploy-fastapi-demo",
        "tasks": 2,
        "cpu": 256,
        "memory": 512
      },
      "deployedAt": "2025-11-07T12:34:56Z",
      "cost": "$0.004/deploy"
    }
  ]
}
```

---

## 🚀 **추천 구현 순서**

1. ✅ **현재**: Single-service (이미 구현됨)
2. ⏳ **다음**: Path-based routing 추가
3. 🔜 **향후**: Custom domain 지원

---

## 💡 **임시 해결책 (현재 테스트용)**

현재는 **단일 서비스**만 지원하므로:

```
배포된 앱 접속 URL:
http://delightful-deploy-alb-796875577.ap-northeast-2.elb.amazonaws.com/

주의사항:
- 새 배포 시 이전 앱 교체됨
- 테스트/데모 용도로만 사용
- 프로덕션은 Multi-Service 구현 후
```

---

## 📝 **요약**

**Q: 배포된 서비스는 어디에?**
A: AWS ECS Fargate (ap-northeast-2)

**Q: URL은?**
A: http://delightful-deploy-alb-796875577.ap-northeast-2.elb.amazonaws.com/

**Q: 여러 앱 동시 배포 가능?**
A: 현재는 불가, Path-based routing 구현 필요

**Q: Dashboard에서 관리 가능?**
A: 지금 구현 예정! 🚀
