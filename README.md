# FLUX Dev Serverless on RUNPOD

FLUX.1-dev 모델을 RUNPOD 서버리스에서 실행하기 위한 프로젝트입니다.

## 📁 프로젝트 구조

```
flux-dev-serverless/
├── Dockerfile          # Docker 이미지 빌드 파일
├── download_models.py  # 모델 다운로드 스크립트
├── handler.py         # RUNPOD 핸들러 메인 코드
├── test_api.py        # API 테스트 스크립트
├── build_and_push.sh  # Linux/Mac 빌드 스크립트
├── build_and_push.bat # Windows 빌드 스크립트
└── README.md          # 이 파일
```

## 🚀 시작하기

### 1. 사전 요구사항

- Docker 설치
- Docker Hub 계정
- RUNPOD 계정 및 크레딧
- HuggingFace 토큰 (FLUX.1-dev 접근용)

### 2. 환경 설정

1. `.env.example`을 `.env`로 복사:
   ```bash
   cp .env.example .env
   ```

2. `.env` 파일을 열어 실제 값 입력:
   ```
   HF_TOKEN=your-actual-hf-token
   RUNPOD_API_KEY=your-actual-runpod-key
   DOCKER_USERNAME=your-dockerhub-username
   ```

2. `build_and_push.bat` (Windows) 또는 `build_and_push.sh` (Linux/Mac)에서 Docker Hub 사용자명 변경:
   ```
   DOCKER_USERNAME=your-dockerhub-username
   ```

### 3. Docker 이미지 빌드 및 푸시

Windows:
```bash
build_and_push.bat
```

Linux/Mac:
```bash
chmod +x build_and_push.sh
./build_and_push.sh
```

### 4. RUNPOD 서버리스 엔드포인트 생성

1. RUNPOD 콘솔 접속
2. "Serverless" → "New Endpoint" 클릭
3. 다음 설정 입력:
   - **Container Image**: `your-dockerhub-username/flux-dev-serverless:latest`
   - **GPU**: RTX 4090 또는 A40 (24GB VRAM 필수)
   - **Container Disk**: 50GB
   - **Max Workers**: 필요에 따라 설정
   - **Idle Timeout**: 60초
   - **Environment Variables**: 없음

### 5. API 테스트

1. `test_api.py` 파일 수정:
   ```python
   ENDPOINT_ID = "your-endpoint-id"  # RUNPOD에서 받은 ID
   API_KEY = "your-runpod-api-key"   # RUNPOD API 키
   ```

2. 테스트 실행:
   ```bash
   python test_api.py
   ```

## 📝 API 사용법

### 요청 형식

```python
{
    "input": {
        "prompt": "이미지 설명",
        "negative_prompt": "제외할 요소",
        "width": 1024,
        "height": 1024,
        "steps": 28,
        "guidance_scale": 3.5,
        "seed": -1,  # -1은 랜덤
        "upscale": false,
        "upscale_factor": 2
    }
}
```

### 응답 형식

```python
{
    "output": {
        "image": "base64_encoded_image_string",
        "seed": 12345,
        "width": 1024,
        "height": 1024
    }
}
```

## 💰 비용 최적화

1. **Idle Timeout 설정**: 사용하지 않을 때 자동 종료
2. **GPU 선택**: RTX 4090이 A40보다 저렴
3. **배치 처리**: 여러 요청을 한 번에 처리
4. **이미지 크기**: 필요한 최소 크기 사용

## 🔧 문제 해결

### "Out of Memory" 에러
- GPU 메모리가 부족할 때 발생
- 이미지 크기를 줄이거나 steps를 감소

### 느린 Cold Start
- 첫 요청 시 모델 로드로 인해 발생
- 자주 사용하는 시간대에 웜업 요청 전송

### 이미지 품질 문제
- `steps` 증가 (기본 28 → 40~50)
- `guidance_scale` 조정 (2.5~5.0 범위)

## 📚 참고 자료

- [RUNPOD 문서](https://docs.runpod.io/)
- [FLUX 모델 정보](https://huggingface.co/black-forest-labs/FLUX.1-dev)
- [Diffusers 라이브러리](https://huggingface.co/docs/diffusers)

## 📄 라이선스

FLUX.1-dev 모델의 라이선스를 확인하세요.

## 🐙 GitHub Actions 자동 빌드

이 프로젝트는 GitHub Actions를 통한 자동 빌드를 지원합니다.

### 설정 방법

1. GitHub 저장소의 Settings → Secrets and variables → Actions
2. 다음 시크릿 추가:
   - `DOCKER_USERNAME`: Docker Hub 사용자명
   - `DOCKER_PASSWORD`: Docker Hub 비밀번호 또는 액세스 토큰
   - `HF_TOKEN`: HuggingFace 토큰

### 자동 빌드 트리거

- `main` 브랜치에 push할 때마다 자동 빌드
- Pull Request 생성 시 테스트 빌드
- Actions 탭에서 수동 실행 가능

## 💾 저장 공간 최적화

이 프로젝트는 Docker 이미지 크기를 최소화하기 위해 런타임 모델 다운로드 방식을 사용합니다:

- **Docker 이미지 크기**: ~5GB (모델 제외)
- **첫 실행 시**: FLUX.1-dev 모델 자동 다운로드 (24GB, 20-30분 소요)
- **이후 실행**: 캐시된 모델 사용 (빠른 시작)

### RUNPOD 볼륨 설정
RUNPOD에서 모델을 영구 저장하려면:
1. Volume 생성 (50GB 이상)
2. `/workspace/models`에 마운트
3. 모델이 한 번만 다운로드되도록 보장