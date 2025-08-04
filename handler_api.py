import runpod
import torch
import base64
from io import BytesIO
from PIL import Image
import requests
import os

def handler(job):
    """RUNPOD 핸들러 - Replicate API 사용"""
    try:
        job_input = job["input"]
        
        # 파라미터 추출
        prompt = job_input.get("prompt", "beautiful landscape")
        width = job_input.get("width", 1024)
        height = job_input.get("height", 1024)
        num_inference_steps = job_input.get("steps", 4)  # schnell은 4단계
        seed = job_input.get("seed", -1)
        
        # Replicate API 호출 (더 간단하고 효율적)
        replicate_api_token = os.environ.get("REPLICATE_API_TOKEN", "")
        
        if not replicate_api_token:
            # 대안: Hugging Face Inference API 사용
            hf_token = os.environ.get("HF_TOKEN", "")
            api_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
            
            headers = {"Authorization": f"Bearer {hf_token}"}
            
            response = requests.post(
                api_url,
                headers=headers,
                json={
                    "inputs": prompt,
                    "parameters": {
                        "width": width,
                        "height": height,
                        "num_inference_steps": num_inference_steps,
                        "seed": seed if seed != -1 else None
                    }
                }
            )
            
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
            else:
                return {"error": f"API error: {response.status_code} - {response.text}"}
        else:
            # Replicate API 사용
            import replicate
            
            output = replicate.run(
                "black-forest-labs/flux-schnell",
                input={
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                    "num_inference_steps": num_inference_steps,
                    "seed": seed if seed != -1 else None
                }
            )
            
            # URL에서 이미지 다운로드
            response = requests.get(output[0])
            image = Image.open(BytesIO(response.content))
        
        # Base64 인코딩
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "image": img_str,
            "seed": seed,
            "width": width,
            "height": height
        }
        
    except Exception as e:
        return {"error": str(e)}

# RUNPOD 서버리스 시작
runpod.serverless.start({"handler": handler})