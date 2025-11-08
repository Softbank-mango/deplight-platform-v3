# Deplight Dashboard - Optimized Dockerfile with UV
FROM python:3.11-slim

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    AWS_REGION=ap-northeast-2

# 작업 디렉토리 설정
WORKDIR /app

# UV 설치 (5-10x faster than pip)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    update-ca-certificates && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# PATH에 UV 추가 (새 설치 스크립트는 ~/.local/bin 사용)
ENV PATH="/root/.local/bin:/root/.cargo/bin:$PATH"

# 의존성 파일 복사
COPY requirements.txt .

# UV로 의존성 설치 (빠른 설치)
RUN uv pip install --system -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:8000/api/health')" || exit 1

# 포트 노출
EXPOSE 8000

# FastAPI 서버 실행
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
