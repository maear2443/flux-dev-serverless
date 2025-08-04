# GitHub에 업로드하기

이 프로젝트를 GitHub에 업로드하는 방법입니다.

## 1. GitHub에서 새 저장소 만들기

1. [GitHub.com](https://github.com)에 로그인
2. 우측 상단 '+' 버튼 → "New repository" 클릭
3. 저장소 이름: `flux-dev-serverless` (또는 원하는 이름)
4. 설명: "FLUX.1-dev model on RUNPOD Serverless"
5. Public/Private 선택
6. **중요**: "Initialize this repository with:" 옵션들은 모두 체크 해제
7. "Create repository" 클릭

## 2. 로컬 저장소를 GitHub에 연결

GitHub에서 저장소를 만든 후 나오는 명령어를 사용하거나, 아래 명령어를 실행:

```bash
cd C:\Users\maear\Downloads\flux-dev-serverless

# GitHub 원격 저장소 추가 (YOUR_USERNAME을 본인 GitHub 사용자명으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/flux-dev-serverless.git

# 브랜치 이름을 main으로 변경 (GitHub 기본값)
git branch -M main

# GitHub에 푸시
git push -u origin main
```

## 3. 민감한 정보 확인

업로드 전에 다음 사항을 확인하세요:

- [ ] HuggingFace 토큰이 코드에 하드코딩되어 있지 않은지
- [ ] RUNPOD API 키가 노출되지 않았는지
- [ ] Docker Hub 비밀번호가 포함되지 않았는지

## 4. 환경 변수 사용 권장

민감한 정보는 환경 변수로 관리하세요:

1. `.env.example` 파일 생성:
```
HF_TOKEN=your-hf-token-here
RUNPOD_API_KEY=your-runpod-api-key-here
DOCKER_USERNAME=your-dockerhub-username
```

2. 실제 사용 시 `.env` 파일로 복사하여 실제 값 입력

## 5. GitHub Actions (선택사항)

자동 빌드를 원한다면 `.github/workflows/build.yml` 파일 추가:

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{ secrets.DOCKER_USERNAME }}/flux-dev-serverless:latest
```

이 경우 GitHub 저장소 Settings → Secrets에서 다음 시크릿 추가 필요:
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`