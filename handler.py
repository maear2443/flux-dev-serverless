import runpod
import torch
import base64
from io import BytesIO
from PIL import Image
from diffusers import FluxPipeline, DPMSolverMultistepScheduler
import cv2
import numpy as np
import os
from huggingface_hub import snapshot_download

# GPU 메모리 최적화
torch.cuda.empty_cache()

# 모델 캐시 디렉토리
MODEL_CACHE_DIR = "/workspace/models"
os.makedirs(MODEL_CACHE_DIR, exist_ok=True)

# 환경 변수에서 HF 토큰 가져오기
HF_TOKEN = os.environ.get("HF_TOKEN", "")

print("🔧 모델 로드 중...")

# 모델이 이미 다운로드되었는지 확인
model_path = os.path.join(MODEL_CACHE_DIR, "flux-dev")
if not os.path.exists(model_path) or len(os.listdir(model_path)) == 0:
    print("📥 FLUX.1-dev 모델 다운로드 중... (첫 실행 시 20-30분 소요)")
    try:
        snapshot_download(
            "black-forest-labs/FLUX.1-dev",
            local_dir=model_path,
            token=HF_TOKEN if HF_TOKEN else None,
            local_dir_use_symlinks=False
        )
        print("✅ 모델 다운로드 완료!")
    except Exception as e:
        print(f"❌ 모델 다운로드 실패: {e}")
        print("HF_TOKEN 환경 변수를 확인하세요.")
        raise

# 모델 로드 (전역 변수로 한 번만 로드)
try:
    pipe = FluxPipeline.from_pretrained(
        model_path,
        torch_dtype=torch.float16,
        variant="fp16",
        local_files_only=True
    ).to("cuda")
    
    # 스케줄러 최적화
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    
    # VAE 최적화
    pipe.enable_vae_slicing()
    pipe.enable_vae_tiling()
    
    print("✅ 모델 로드 완료!")
except Exception as e:
    print(f"❌ 모델 로드 실패: {e}")
    raise

def upscale_image(image, scale=2):
    """간단한 업스케일링 함수"""
    # PIL Image를 numpy array로 변환
    img_array = np.array(image)
    
    # OpenCV로 업스케일
    height, width = img_array.shape[:2]
    new_dimensions = (width * scale, height * scale)
    
    # INTER_CUBIC 보간법 사용
    upscaled = cv2.resize(img_array, new_dimensions, interpolation=cv2.INTER_CUBIC)
    
    # 다시 PIL Image로 변환
    return Image.fromarray(upscaled)

def handler(job):
    """RUNPOD 핸들러 함수"""
    try:
        job_input = job["input"]
        
        # 파라미터 추출
        prompt = job_input.get("prompt", "beautiful landscape")
        negative_prompt = job_input.get("negative_prompt", "")
        width = job_input.get("width", 1024)
        height = job_input.get("height", 1024)
        num_inference_steps = job_input.get("steps", 28)
        guidance_scale = job_input.get("guidance_scale", 3.5)
        seed = job_input.get("seed", -1)
        upscale = job_input.get("upscale", False)
        upscale_factor = job_input.get("upscale_factor", 2)        
        # 시드 설정
        if seed == -1:
            seed = torch.randint(0, 2**32, (1,)).item()
        
        generator = torch.Generator(device="cuda").manual_seed(seed)
        
        # 이미지 생성
        with torch.cuda.amp.autocast():
            image = pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator
            ).images[0]
        
        # 업스케일링 (요청 시)
        if upscale:
            image = upscale_image(image, upscale_factor)
        
        # Base64 인코딩
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "image": img_str,
            "seed": seed,
            "width": image.width,
            "height": image.height
        }
        
    except Exception as e:
        return {"error": str(e)}

# RUNPOD 서버리스 시작
runpod.serverless.start({"handler": handler})