@echo off
echo 📌 GitHub 업로드 가이드
echo.
echo 1. GitHub.com에서 새 저장소 만들기:
echo    - 저장소 이름: flux-dev-serverless
echo    - Public 또는 Private 선택
echo    - README, .gitignore, License 추가하지 않기
echo.
echo 2. 저장소를 만든 후, 아래 명령어 실행:
echo.
echo    git remote add origin https://github.com/YOUR_USERNAME/flux-dev-serverless.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo 3. GitHub Secrets 설정 (자동 빌드용):
echo    - DOCKER_USERNAME
echo    - DOCKER_PASSWORD
echo    - HF_TOKEN
echo.
pause