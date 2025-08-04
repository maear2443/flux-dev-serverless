import runpod
import torch
import base64
from io import BytesIO
from PIL import Image
from diffusers import StableDiffusion3Pipeline, DPMSolverMultistepScheduler
import os

# GPU 메모리 최적화
torch.cuda.empty_cache()

print("🔧 Stable Diffusion 3 모델 로드 중...")

# SD3는 더 작고 효율적 (약 4-6GB)
pipe = StableDiffusion3Pipeline.from_pretrained(
    "stabilityai/stable-diffusion-3-medium-diffusers",
    torch_dtype=torch.float16,
    variant="fp16",
    use_auth_token=os.environ.get("HF_TOKEN", "")
).to("cuda")

# 메모리 최적화
pipe.enable_vae_slicing()
pipe.enable_vae_tiling()
pipe.enable_sequential_cpu_offload()

def handler(job):
    """RUNPOD 핸들러 함수"""
    try:
        job_input = job["input"]
        
        # 파라미터 추출
        prompt = job_input.get("prompt", "beautiful landscape")
        negative_prompt = job_input.get("negative_prompt", "")
        width = job_input.get("width", 1024)
        height = job_input.get("height", 1024)
        num_inference_steps = job_input.get("steps", 30)
        guidance_scale = job_input.get("guidance_scale", 7.0)
        seed = job_input.get("seed", -1)
        
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