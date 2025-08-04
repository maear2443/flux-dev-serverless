# 서버리스 LoRA 학습 완벽 가이드

## 🚀 Replicate로 LoRA 학습 (가장 쉬움)

### 1. Replicate의 학습 API 사용

```python
import replicate

# FLUX LoRA 학습
training = replicate.trainings.create(
    version="ostris/flux-dev-lora-trainer:4ffd32160efd92e956d39c5338a9b8fbafca58e03f791f6d8011f3e20e8ea6fa",
    input={
        "input_images": "https://my-dataset.zip",  # 학습 이미지 ZIP
        "trigger_word": "TOK",  # 트리거 단어
        "steps": 1000,
        "learning_rate": 0.0004,
    },
    destination="username/my-flux-lora"  # 학습된 모델 저장 위치
)

print(f"학습 시작: {training.status}")
print(f"예상 시간: 20-30분")
print(f"예상 비용: $2-3")
```

### 2. 학습 데이터 준비

```python
# prepare_dataset.py
import os
import zipfile
from PIL import Image

def prepare_training_data(image_folder, output_zip):
    """
    이미지 폴더를 Replicate 학습용 ZIP으로 변환
    """
    with zipfile.ZipFile(output_zip, 'w') as zf:
        for img_file in os.listdir(image_folder):
            if img_file.endswith(('.png', '.jpg', '.jpeg')):
                # 이미지 리사이즈 (512x512 또는 1024x1024)
                img = Image.open(os.path.join(image_folder, img_file))
                img = img.resize((512, 512), Image.LANCZOS)
                
                # 캡션 파일 생성
                caption = f"a photo of TOK person"  # 또는 커스텀 캡션
                
                # ZIP에 추가
                img_path = f"images/{img_file}"
                zf.writestr(img_path, img.tobytes())
                zf.writestr(f"images/{img_file.split('.')[0]}.txt", caption)

# 사용
prepare_training_data("my_images/", "training_data.zip")
```

### 3. 비용 및 시간

| 모델 | 학습 시간 | 비용 | GPU |
|------|-----------|------|------|
| FLUX LoRA | 20-30분 | $2-3 | A100 80GB |
| SDXL LoRA | 10-15분 | $1-2 | A40 |
| SD 1.5 LoRA | 5-10분 | $0.5-1 | T4 |

## 🔧 RunPod으로 LoRA 학습

### 1. 서버리스 학습 워커 만들기

```python
# train_handler.py
import runpod
import torch
from diffusers import DiffusionPipeline
import kohya_ss  # LoRA 학습 라이브러리

def handler(job):
    job_input = job["input"]
    
    # 학습 파라미터
    dataset_url = job_input["dataset_url"]
    model_name = job_input.get("model_name", "FLUX.1-dev")
    trigger_word = job_input.get("trigger_word", "TOK")
    steps = job_input.get("steps", 1000)
    learning_rate = job_input.get("learning_rate", 5e-5)
    
    # 데이터셋 다운로드
    download_dataset(dataset_url)
    
    # 학습 설정
    config = {
        "pretrained_model_name_or_path": model_name,
        "instance_data_dir": "./dataset",
        "output_dir": "./output",
        "instance_prompt": f"a photo of {trigger_word}",
        "resolution": 1024,
        "train_batch_size": 1,
        "gradient_accumulation_steps": 4,
        "learning_rate": learning_rate,
        "max_train_steps": steps,
        "lora_rank": 32,
    }
    
    # 학습 실행
    trainer = LoRATrainer(config)
    trainer.train()
    
    # 결과 업로드
    lora_url = upload_to_huggingface(
        "./output/pytorch_lora_weights.safetensors",
        repo_name=f"{trigger_word}-lora"
    )
    
    return {
        "lora_url": lora_url,
        "trigger_word": trigger_word,
        "training_time": trainer.get_training_time()
    }

runpod.serverless.start({"handler": handler})
```

### 2. Docker 파일 (학습용)

```dockerfile
FROM runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel

# 학습 라이브러리 설치
RUN pip install \
    diffusers[training] \
    accelerate \
    transformers \
    bitsandbytes \
    kohya-ss \
    wandb

# 학습 스크립트
COPY train_handler.py /

CMD ["python", "train_handler.py"]
```

## 💰 비용 비교: 학습

| 플랫폼 | 설정 난이도 | 비용 (LoRA 1개) | 속도 | 특징 |
|--------|------------|----------------|------|------|
| **Replicate** | ⭐ 매우 쉬움 | $2-3 | 20-30분 | 완전 관리형 |
| **RunPod** | ⭐⭐⭐ 보통 | $0.5-1 | 30-40분 | 커스터마이징 가능 |
| **Modal** | ⭐⭐ 쉬움 | $1-2 | 20-30분 | Python 네이티브 |
| **Vast.ai** | ⭐⭐⭐⭐ 어려움 | $0.3-0.8 | 40-60분 | 가장 저렴 |

## 🎨 Replicate 학습 + 추론 통합 예시

```python
# 1. 학습
training = replicate.trainings.create(
    version="ostris/flux-dev-lora-trainer:latest",
    input={
        "input_images": "https://my-images.zip",
        "trigger_word": "MYCHAR",
        "steps": 1000,
    },
    destination="myusername/my-character-lora"
)

# 2. 학습 완료 대기
training.wait()

# 3. 바로 사용!
output = replicate.run(
    "myusername/my-character-lora:latest",
    input={
        "prompt": "MYCHAR wearing a kimono in tokyo",
        "num_outputs": 4
    }
)
```

## 🔥 AutoTrain 방식 (Hugging Face)

```python
# Hugging Face AutoTrain 사용
from autotrain import AutoTrain

# 초간단 학습
at = AutoTrain()
at.train_lora(
    model="black-forest-labs/FLUX.1-dev",
    dataset="my_dataset",
    output="my-lora",
    hardware="A100",  # 서버리스 GPU
    time_limit=30  # 30분 제한
)

# 비용: $3-5
# 완전 자동화
```

## 📊 추천 워크플로우

### 초보자/빠른 프로토타이핑:
```
1. Replicate로 학습 ($3)
2. Replicate로 테스트
3. 만족하면 RunPod으로 대량 생성
```

### 중급자/비용 최적화:
```
1. RunPod 학습 워커 구축
2. 학습 ($1)
3. ComfyUI Worker로 추론
```

### 고급자/완전 제어:
```
1. Vast.ai에서 저렴한 GPU 찾기
2. Kohya 스크립트로 직접 학습
3. 커스텀 서버리스 배포
```

## 🎯 Quick Start: Replicate 학습

```bash
# 1. Replicate CLI 설치
pip install replicate

# 2. 데이터셋 준비 (10-20장 이미지)
mkdir my_dataset
# 이미지 넣기

# 3. ZIP 만들기
zip -r dataset.zip my_dataset/

# 4. 업로드 & 학습
replicate train \
  --destination myusername/my-lora \
  --version ostris/flux-dev-lora-trainer \
  --input input_images=@dataset.zip \
  --input trigger_word=MYTOK \
  --input steps=500

# 5. 완료! 20분 후 사용 가능
```

## 💡 Pro Tips

1. **데이터셋 품질 > 수량**
   - 10장의 좋은 이미지 > 100장의 나쁜 이미지
   - 다양한 각도/조명 포함

2. **트리거 워드 선택**
   - 독특한 단어 사용 (TOK, MYCHAR 등)
   - 일반 단어 피하기

3. **학습률 조정**
   - FLUX: 1e-4 ~ 5e-4
   - SDXL: 1e-5 ~ 1e-4
   - 과적합 주의

4. **비용 절약**
   - 짧은 학습 (500-1000 steps)
   - 작은 LoRA rank (16-32)
   - 오프피크 시간 활용