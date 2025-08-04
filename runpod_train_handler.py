"""
RunPod 서버리스 LoRA 학습 워커
"""

import runpod
import torch
import os
import zipfile
import requests
from pathlib import Path

# Kohya 학습 스크립트 활용
def train_lora_kohya(config):
    """Kohya 스크립트를 사용한 LoRA 학습"""
    
    # 학습 스크립트 생성
    train_script = f"""
    accelerate launch --num_cpu_threads_per_process=2 train_network.py \\
      --pretrained_model_name_or_path={config['model_path']} \\
      --dataset_config={config['dataset_config']} \\
      --output_dir={config['output_dir']} \\
      --output_name={config['output_name']} \\
      --save_model_as=safetensors \\
      --prior_loss_weight=1.0 \\
      --max_train_steps={config['max_steps']} \\
      --learning_rate={config['learning_rate']} \\
      --optimizer_type="AdamW8bit" \\
      --lr_scheduler="cosine_with_restarts" \\
      --lr_warmup_steps=100 \\
      --train_batch_size=1 \\
      --gradient_checkpointing \\
      --gradient_accumulation_steps=1 \\
      --mixed_precision="fp16" \\
      --save_precision="fp16" \\
      --network_module="networks.lora" \\
      --network_rank={config['lora_rank']} \\
      --network_alpha={config['lora_alpha']} \\
      --network_train_unet_only \\
      --cache_latents \\
      --cache_latents_to_disk \\
      --persistent_data_loader_workers
    """
    
    # 학습 실행
    os.system(train_script)
    
    # 결과 파일 찾기
    output_files = list(Path(config['output_dir']).glob("*.safetensors"))
    if output_files:
        return str(output_files[-1])  # 가장 최신 파일
    return None

def handler(job):
    """RunPod 핸들러"""
    try:
        job_input = job["input"]
        
        # 1. 입력 파라미터
        dataset_url = job_input["dataset_url"]
        model_name = job_input.get("model_name", "black-forest-labs/FLUX.1-dev")
        trigger_word = job_input.get("trigger_word", "TOK")
        max_steps = job_input.get("steps", 1000)
        learning_rate = job_input.get("learning_rate", 4e-4)
        lora_rank = job_input.get("lora_rank", 32)
        
        # 2. 데이터셋 다운로드 및 준비
        print(f"📥 데이터셋 다운로드: {dataset_url}")
        dataset_path = "/tmp/dataset.zip"
        
        response = requests.get(dataset_url)
        with open(dataset_path, 'wb') as f:
            f.write(response.content)
        
        # ZIP 압축 해제
        extract_path = "/tmp/dataset"
        os.makedirs(extract_path, exist_ok=True)
        
        with zipfile.ZipFile(dataset_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        
        # 3. 데이터셋 설정 파일 생성
        dataset_config = {
            "general": {
                "enable_bucket": True,
                "resolution": "1024,1024",
                "batch_size": 1
            },
            "datasets": [{
                "subsets": [{
                    "image_dir": extract_path,
                    "class_tokens": trigger_word,
                    "num_repeats": 10
                }]
            }]
        }
        
        # 설정 저장
        import json
        config_path = "/tmp/dataset_config.json"
        with open(config_path, 'w') as f:
            json.dump(dataset_config, f)
        
        # 4. 학습 실행
        print("🚀 LoRA 학습 시작...")
        
        train_config = {
            "model_path": model_name,
            "dataset_config": config_path,
            "output_dir": "/tmp/output",
            "output_name": f"{trigger_word}_lora",
            "max_steps": max_steps,
            "learning_rate": learning_rate,
            "lora_rank": lora_rank,
            "lora_alpha": lora_rank
        }
        
        # 실제 학습 (간단한 버전)
        # 실제로는 Kohya 스크립트나 diffusers의 train_text_to_image_lora.py 사용
        from train_simple_lora import train_flux_lora  # 커스텀 학습 함수
        
        output_path = train_flux_lora(
            model_name=model_name,
            train_data_dir=extract_path,
            output_dir="/tmp/output",
            instance_prompt=f"a photo of {trigger_word}",
            max_train_steps=max_steps,
            learning_rate=learning_rate,
            rank=lora_rank
        )
        
        # 5. 결과 업로드
        print("📤 학습된 LoRA 업로드 중...")
        
        # HuggingFace Hub에 업로드
        from huggingface_hub import HfApi
        api = HfApi()
        
        repo_id = f"{os.environ.get('HF_USERNAME', 'user')}/{trigger_word}-flux-lora"
        
        # 리포지토리 생성
        api.create_repo(repo_id, exist_ok=True)
        
        # 파일 업로드
        upload_url = api.upload_file(
            path_or_fileobj=output_path,
            path_in_repo=f"{trigger_word}_lora.safetensors",
            repo_id=repo_id,
            repo_type="model"
        )
        
        # 모델 카드 생성
        model_card = f"""
---
tags:
- flux
- lora
- diffusers
- {trigger_word}
---

# {trigger_word} FLUX LoRA

## Trigger word
`{trigger_word}`

## Usage
```python
from diffusers import FluxPipeline
import torch

pipe = FluxPipeline.from_pretrained(
    "black-forest-labs/FLUX.1-dev",
    torch_dtype=torch.float16
).to("cuda")

pipe.load_lora_weights("{repo_id}")

prompt = "a photo of {trigger_word} person"
image = pipe(prompt).images[0]
```

## Training details
- Base model: {model_name}
- Steps: {max_steps}
- Learning rate: {learning_rate}
- Rank: {lora_rank}
"""
        
        api.upload_file(
            path_or_fileobj=model_card.encode(),
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="model"
        )
        
        return {
            "status": "success",
            "lora_url": f"https://huggingface.co/{repo_id}",
            "trigger_word": trigger_word,
            "training_steps": max_steps,
            "download_url": f"https://huggingface.co/{repo_id}/resolve/main/{trigger_word}_lora.safetensors"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# RunPod 서버리스 시작
runpod.serverless.start({"handler": handler})