# RUNPOD Serverless Endpoint 생성 가이드

## 1. RUNPOD 계정 준비
- https://www.runpod.io/ 에서 계정 생성
- 크레딧 충전 (최소 $10 권장)

## 2. Serverless 엔드포인트 생성

1. RUNPOD 대시보드 → "Serverless" 탭
2. "New Endpoint" 클릭
3. 다음 설정 입력:

### 기본 설정
- **Endpoint Name**: `flux-dev-serverless`
- **Select Template**: "Custom" 선택

### Container Configuration
- **Container Image**: `maear2444/flux-dev-serverless:latest`
- **Container Registry Credentials**: 필요 없음 (Public 이미지)
- **Container Disk**: `50 GB`
- **Volume Disk**: 필요 없음

### GPU Configuration
- **GPU Type**: 다음 중 선택
  - RTX 4090 (24GB) - 가장 저렴, 권장
  - RTX A5000 (24GB)
  - A40 (48GB) - 과도한 스펙
  - A100 (40GB/80GB) - 매우 비쌈

### Worker Configuration
- **Max Workers**: `3` (필요에 따라 조정)
- **Idle Timeout**: `60` 초
- **Execution Timeout**: `300` 초 (5분)
- **Flashboot**: 활성화 (빠른 시작)

### Environment Variables (선택사항)
```
HF_HUB_ENABLE_HF_TRANSFER=1
```

### Advanced Settings
- **Scaling Type**: "Queue Delay"
- **Target Queue Delay**: 1-3초

## 3. 엔드포인트 생성 완료 후

1. **Endpoint ID** 복사 (예: `abc123xyz`)
2. **API Key** 생성:
   - Settings → API Keys
   - "Create API Key" 클릭
   - 생성된 키 안전하게 보관

## 4. 요금 정보
- **RTX 4090**: ~$0.44/시간
- **콜드 스타트**: 첫 요청 시 20-30초
- **웜 상태**: 2-5초 내 응답
- **유휴 시**: 자동 종료로 비용 절감

## 5. 테스트
생성된 Endpoint ID와 API Key를 사용하여 test_api.py 실행