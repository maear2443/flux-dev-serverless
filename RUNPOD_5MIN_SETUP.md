# RunPod ComfyUI Worker 5분 세팅 가이드

## 1단계: RunPod에서 배포 (2분)

1. https://www.runpod.io/console/serverless 접속
2. "Quick Deploy" 클릭
3. "runpod-workers/worker-comfyui" 검색
4. 다음 설정:
   - Container Image: `runpod/worker-comfyui:latest`
   - GPU: RTX 4090 (24GB)
   - Max Workers: 1
   - Idle Timeout: 60초
5. "Deploy" 클릭

## 2단계: Network Volume 생성 (1분)

1. RunPod Console → Storage → Network Volumes
2. "New Network Volume" 클릭
3. 설정:
   - Name: `comfyui-models`
   - Size: 20GB
   - Region: 같은 지역 선택
4. "Create" 클릭

## 3단계: Volume 연결 (1분)

1. Serverless Endpoint 설정으로 이동
2. "Edit Endpoint" 클릭
3. "Persistent Storage" 섹션에서:
   - Volume: `comfyui-models` 선택
   - Mount Path: `/workspace/models`
4. "Update" 클릭

## 4단계: LoRA 업로드 (1분)

### 옵션 A: RunPod File Browser 사용
1. Pod 생성 (임시):
   - GPU Pod → Deploy
   - 같은 Network Volume 연결
   - Jupyter Lab 템플릿 선택
2. Jupyter에서 파일 업로드:
   - `/workspace/models/Lora/` 폴더로 이동
   - Upload 버튼으로 LoRA 파일 업로드
3. Pod 종료

### 옵션 B: Direct Upload API 사용
```python
import requests

# LoRA 파일을 URL에 업로드 (HuggingFace, Google Drive 등)
lora_url = "https://huggingface.co/your-lora/resolve/main/anime.safetensors"

# ComfyUI 워크플로우에서 URL 다운로드
workflow = {
    "download_lora": {
        "class_type": "DownloadAndLoadLora",
        "inputs": {
            "url": lora_url,
            "name": "my_custom_lora.safetensors"
        }
    }
}
```

## 5단계: 테스트 (바로 사용!)

```python
import requests
import json

# API 정보
API_KEY = "your-runpod-api-key"
ENDPOINT_ID = "your-endpoint-id"

# 간단한 테스트
response = requests.post(
    f"https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "input": {
            "prompt": "anime character",
            "lora": "my_custom_lora.safetensors",
            "lora_strength": 0.8
        }
    }
)

print(response.json())
```

## 🎉 완료!

이제 사용 가능합니다:
- FLUX + 커스텀 LoRA
- ComfyUI의 모든 기능
- API로 자동화 가능
- 시간당 $0.44만 지불

## 💡 Pro Tips

1. **여러 LoRA 사용**:
   ```python
   "loras": [
       {"name": "style_lora.safetensors", "strength": 0.7},
       {"name": "character_lora.safetensors", "strength": 0.9}
   ]
   ```

2. **ComfyUI Web UI 접근**:
   - GPU Pod 생성 시 ComfyUI 템플릿 선택
   - 웹에서 워크플로우 만들고 JSON 추출
   - Serverless API에서 사용

3. **비용 절약**:
   - Idle Timeout을 60초로 설정
   - 배치 처리로 여러 이미지 한번에
   - 낮은 Steps (20-30)로도 충분