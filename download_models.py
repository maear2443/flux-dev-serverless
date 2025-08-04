import os
from huggingface_hub import snapshot_download, hf_hub_download

# HF 토큰 설정 (환경 변수에서 읽기)
HF_TOKEN = os.environ.get("HF_TOKEN")
if not HF_TOKEN:
    print("⚠️ 경고: HF_TOKEN 환경 변수가 설정되지 않았습니다!")
    print("Docker 빌드 시 --build-arg HF_TOKEN=your-token 을 사용하세요.")
    exit(1)

# 모델 저장 경로
MODEL_DIR = "/app/models"
os.makedirs(MODEL_DIR, exist_ok=True)

print("📥 FLUX.1-dev 모델 다운로드 중...")
# FLUX.1-dev 전체 다운로드
snapshot_download(
    "black-forest-labs/FLUX.1-dev",
    local_dir=f"{MODEL_DIR}/flux-dev",
    token=HF_TOKEN
)

print("📥 텍스트 인코더 다운로드 중...")
# CLIP 인코더
hf_hub_download(
    "comfyanonymous/flux_text_encoders",
    "clip_l.safetensors",
    local_dir=f"{MODEL_DIR}/encoders"
)
hf_hub_download(
    "comfyanonymous/flux_text_encoders", 
    "t5xxl_fp8_e4m3fn.safetensors",
    local_dir=f"{MODEL_DIR}/encoders"
)

print("✅ 모든 모델 다운로드 완료!")