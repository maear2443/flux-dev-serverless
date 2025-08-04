# Replicate 작동 방식 상세 설명

## 🎯 Replicate란?

모델을 Docker 컨테이너로 패키징하고 서버리스로 실행하는 플랫폼입니다.

## 📦 Replicate 구조

### 1. Cog 파일 (cog.yaml)
```yaml
build:
  gpu: true
  cuda: "11.8"
  python_version: "3.10"
  python_packages:
    - "torch==2.0.1"
    - "diffusers==0.24.0"
    - "transformers==4.35.0"

predict: "predict.py:Predictor"
```

### 2. Predict.py (핵심 코드)
```python
from cog import BasePredictor, Input, Path
import torch
from diffusers import FluxPipeline

class Predictor(BasePredictor):
    def setup(self):
        """모델 로드 (한 번만 실행)"""
        self.pipe = FluxPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-dev",
            torch_dtype=torch.float16
        ).to("cuda")
    
    def predict(
        self,
        prompt: str = Input(description="Image prompt"),
        num_steps: int = Input(default=28, ge=1, le=100),
        seed: int = Input(default=-1)
    ) -> Path:
        """각 요청마다 실행"""
        if seed == -1:
            seed = int.from_bytes(os.urandom(2), "big")
        
        generator = torch.Generator("cuda").manual_seed(seed)
        image = self.pipe(
            prompt=prompt,
            num_inference_steps=num_steps,
            generator=generator
        ).images[0]
        
        output_path = "/tmp/output.png"
        image.save(output_path)
        return Path(output_path)
```

## 💰 Replicate 가격 정책

### 공개 모델 사용
- **CPU**: $0.0002/초
- **Nvidia T4**: $0.00055/초
- **Nvidia A40**: $0.0023/초
- **Nvidia A100**: $0.0115/초

### 커스텀 모델 배포
- **Private 모델**: 위 가격 + 20%
- **Cold Start**: 첫 요청 시 10-30초 (무료)
- **Warm Pool**: 월 $10부터 (항상 대기)

## 🚀 LoRA를 Replicate에 배포하는 방법

### 1. 프로젝트 구조
```
my-flux-lora/
├── cog.yaml
├── predict.py
├── models/
│   └── my_lora.safetensors
└── requirements.txt
```

### 2. predict.py (LoRA 포함)
```python
class Predictor(BasePredictor):
    def setup(self):
        self.pipe = FluxPipeline.from_pretrained(...)
        
        # LoRA 로드
        self.pipe.load_lora_weights(
            "./models/my_lora.safetensors",
            adapter_name="my_style"
        )
    
    def predict(
        self,
        prompt: str = Input(...),
        lora_scale: float = Input(default=0.8, ge=0, le=1)
    ) -> Path:
        # LoRA 강도 조절
        self.pipe.set_adapters(["my_style"], [lora_scale])
        
        image = self.pipe(prompt=prompt).images[0]
        ...
```

### 3. 배포 명령어
```bash
# Cog 설치
pip install cog

# 로컬 테스트
cog predict -i prompt="anime character"

# Replicate에 푸시
cog push r8.im/username/my-flux-lora
```

## 🆚 RunPod vs Replicate 비교

| 특징 | RunPod ComfyUI | Replicate |
|------|----------------|-----------|
| **셋업 난이도** | 중간 (Docker 필요) | 쉬움 (Cog 사용) |
| **유연성** | 매우 높음 (ComfyUI) | 중간 (코드 기반) |
| **가격** | $0.44/시간 (RTX 4090) | $0.0032/초 사용량 |
| **Cold Start** | 20-30초 | 10-20초 |
| **LoRA 지원** | 네이티브 지원 | 코드로 구현 |
| **UI** | ComfyUI 웹 | API만 |
| **커뮤니티** | 큰 ComfyUI 생태계 | Replicate 모델들 |

## 📊 비용 예시 (월 1000장 생성)

### RunPod ComfyUI
- 이미지당 30초 = 8.3시간
- 비용: 8.3 × $0.44 = **$3.65/월**
- Volume: $3/월 추가

### Replicate
- 이미지당 15초 = 4.2시간
- 비용: 15,000초 × $0.0032 = **$48/월**

## 🎯 추천

### RunPod ComfyUI가 좋은 경우:
- 많은 이미지 생성 (100장/일 이상)
- ComfyUI 워크플로우 활용
- 여러 LoRA 실험
- 비용 최적화 중요

### Replicate가 좋은 경우:
- 적은 이미지 생성 (10장/일 이하)
- API 통합 필요
- 관리 최소화 원함
- 빠른 프로토타이핑