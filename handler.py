import runpod
import torch
import base64
from io import BytesIO
from PIL import Image
from diffusers import FluxPipeline, DPMSolverMultistepScheduler
import cv2
import numpy as np

# GPU 메모리 최적화
torch.cuda.empty_cache()

# 모델 로드 (전역 변수로 한 번만 로드)
print("🔧 모델 로드 중...")
pipe = FluxPipeline.from_pretrained(
    "/app/models/flux-dev",
    torch_dtype=torch.float16,
    variant="fp16"
).to("cuda")

# 스케줄러 최적화
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

# VAE 최적화
pipe.enable_vae_slicing()
pipe.enable_vae_tiling()

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
        with torch.cuda.amp.autocast():            image = pipe(
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