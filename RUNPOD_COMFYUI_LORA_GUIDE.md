# RunPod ComfyUI Worker 커스터마이징 가이드

## 방법 1: 기존 Worker Fork하기

### 1단계: Worker 복제
```bash
git clone https://github.com/runpod-workers/worker-comfyui
cd worker-comfyui
```

### 2단계: LoRA 추가
1. `models/loras/` 폴더에 LoRA 파일 추가
2. `workflows/` 폴더에 커스텀 워크플로우 추가

### 3단계: Dockerfile 수정
```dockerfile
# 기존 Dockerfile에 추가
COPY models/loras/*.safetensors /comfyui/models/loras/
COPY workflows/*.json /comfyui/workflows/
```

### 4단계: 배포
```bash
docker build -t your-username/comfyui-custom .
docker push your-username/comfyui-custom
```

## 방법 2: 런타임 LoRA 로딩 (더 유연함)

### handler.py 수정
```python
def handler(job):
    job_input = job["input"]
    
    # LoRA URL에서 다운로드
    lora_url = job_input.get("lora_url", None)
    if lora_url:
        download_lora(lora_url)
    
    # ComfyUI 워크플로우 실행
    workflow = job_input.get("workflow", default_workflow)
    workflow["lora_name"] = job_input.get("lora_name", "my_lora.safetensors")
    
    return run_workflow(workflow)
```

## 방법 3: Volume Mount 사용 (추천!)

### RunPod 설정
1. Network Volume 생성 (10GB)
2. `/workspace/models` 마운트
3. LoRA 파일 업로드

### 장점
- Docker 이미지 재빌드 불필요
- 여러 LoRA 쉽게 교체
- 비용 효율적

## API 예시
```json
{
  "input": {
    "workflow": "flux_lora_workflow.json",
    "positive_prompt": "anime style character",
    "lora_name": "anime_lora_v1.safetensors",
    "lora_strength": 0.8
  }
}
```