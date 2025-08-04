FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# 기본 패키지 설치
RUN apt-get update && apt-get install -y \
    python3 python3-pip git wget \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
RUN pip3 install --no-cache-dir \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 \
    diffusers transformers accelerate \
    sentencepiece einops einops_exts \
    opencv-python-headless pillow \
    hf-transfer runpod

# HF Transfer 활성화
ENV HF_HUB_ENABLE_HF_TRANSFER=1

# 빌드 시 HF 토큰 받기 (빌드 후 삭제됨)
ARG HF_TOKEN
ENV HF_TOKEN=$HF_TOKEN

# 작업 디렉토리
WORKDIR /app

# 모델 다운로드 스크립트
COPY download_models.py .
RUN python3 download_models.py && rm download_models.py

# HF 토큰 환경 변수 제거 (보안)
ENV HF_TOKEN=""

# Handler 스크립트
COPY handler.py .

CMD ["python3", "handler.py"]