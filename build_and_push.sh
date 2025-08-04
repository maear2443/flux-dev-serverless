#!/bin/bash
# Docker 빌드 및 푸시 스크립트

# Docker Hub 사용자명 설정 (본인의 것으로 변경)
DOCKER_USERNAME="your-dockerhub-username"
IMAGE_NAME="flux-dev-serverless"
TAG="latest"

echo "🔨 Docker 이미지 빌드 중..."
docker build -t ${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG} .

if [ $? -eq 0 ]; then
    echo "✅ 빌드 성공!"
    
    echo "📤 Docker Hub에 푸시 중..."
    docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG}
    
    if [ $? -eq 0 ]; then
        echo "✅ 푸시 완료!"
        echo "🎉 이미지: ${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG}"
    else
        echo "❌ 푸시 실패!"
    fi
else
    echo "❌ 빌드 실패!"
fi