#!/bin/bash
# Docker 이미지 로컬 테스트 스크립트

echo "🔍 Docker 이미지 확인 중..."
docker images | grep flux-dev-serverless

echo ""
echo "🧪 Docker 컨테이너 테스트 실행..."
echo "다음 명령어로 로컬 테스트 가능:"
echo ""
echo "docker run --rm maear/flux-dev-serverless:latest python3 -c 'import torch; print(f\"PyTorch version: {torch.__version__}\"); print(f\"CUDA available: {torch.cuda.is_available()}\")''"
echo ""
echo "또는 전체 핸들러 테스트:"
echo "docker run --rm maear/flux-dev-serverless:latest python3 -c 'import handler; print(\"Handler loaded successfully!\")'"