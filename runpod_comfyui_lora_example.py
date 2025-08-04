import json
import requests
import base64
from io import BytesIO
from PIL import Image

# RunPod ComfyUI API 설정
RUNPOD_API_KEY = "your-runpod-api-key"
ENDPOINT_ID = "your-endpoint-id"

# FLUX + LoRA 워크플로우
workflow = {
    "3": {
        "class_type": "KSampler",
        "inputs": {
            "seed": 12345,
            "steps": 20,
            "cfg": 7,
            "sampler_name": "dpmpp_2m",
            "scheduler": "karras",
            "denoise": 1,
            "model": ["4", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "latent_image": ["5", 0]
        }
    },
    "4": {
        "class_type": "CheckpointLoaderSimple",
        "inputs": {
            "ckpt_name": "flux1-dev.safetensors"
        }
    },
    "5": {
        "class_type": "EmptyLatentImage",
        "inputs": {
            "width": 1024,
            "height": 1024,
            "batch_size": 1
        }
    },
    "6": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "text": "masterpiece, anime style character WITH_LORA",
            "clip": ["4", 1]
        }
    },
    "7": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "text": "bad quality, blurry",
            "clip": ["4", 1]
        }
    },
    "8": {
        "class_type": "VAEDecode",
        "inputs": {
            "samples": ["3", 0],
            "vae": ["4", 2]
        }
    },
    "9": {
        "class_type": "SaveImage",
        "inputs": {
            "images": ["8", 0],
            "filename_prefix": "flux_lora"
        }
    },
    "10": {
        "class_type": "LoraLoader",
        "inputs": {
            "lora_name": "my_anime_lora.safetensors",
            "strength_model": 0.8,
            "strength_clip": 0.8,
            "model": ["4", 0],
            "clip": ["4", 1]
        }
    }
}

# 요청 보내기
def generate_image(prompt, lora_name=None, lora_strength=0.8):
    # 워크플로우 수정
    workflow_copy = workflow.copy()
    workflow_copy["6"]["inputs"]["text"] = prompt
    
    if lora_name:
        workflow_copy["10"]["inputs"]["lora_name"] = lora_name
        workflow_copy["10"]["inputs"]["strength_model"] = lora_strength
        workflow_copy["10"]["inputs"]["strength_clip"] = lora_strength
        # LoRA 적용된 모델로 연결
        workflow_copy["3"]["inputs"]["model"] = ["10", 0]
    
    # API 요청
    response = requests.post(
        f"https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync",
        headers={
            "Authorization": f"Bearer {RUNPOD_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "input": {
                "workflow": workflow_copy
            }
        }
    )
    
    result = response.json()
    
    # 이미지 추출
    if "output" in result and "images" in result["output"]:
        img_data = base64.b64decode(result["output"]["images"][0])
        img = Image.open(BytesIO(img_data))
        img.save("output.png")
        print("✅ 이미지 생성 완료!")
    else:
        print("❌ 에러:", result)

# 사용 예시
if __name__ == "__main__":
    # 기본 FLUX
    generate_image("beautiful anime character")
    
    # LoRA 적용
    generate_image(
        "beautiful anime character in kimono",
        lora_name="anime_style_v2.safetensors",
        lora_strength=0.9
    )