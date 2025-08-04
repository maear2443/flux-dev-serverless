@echo off
REM Docker 빌드 및 푸시 스크립트 (Windows)

REM .env 파일에서 환경 변수 읽기 (있는 경우)
if exist .env (
    for /f "tokens=1,2 delims==" %%a in (.env) do (
        set %%a=%%b
    )
)

REM Docker Hub 사용자명 확인
if "%DOCKER_USERNAME%"=="" (
    set /p DOCKER_USERNAME=Docker Hub 사용자명을 입력하세요: 
)

REM HF 토큰 확인
if "%HF_TOKEN%"=="" (
    set /p HF_TOKEN=HuggingFace 토큰을 입력하세요: 
)

set IMAGE_NAME=flux-dev-serverless
set TAG=latest

echo 🔨 Docker 이미지 빌드 중...
docker build --build-arg HF_TOKEN=%HF_TOKEN% -t %DOCKER_USERNAME%/%IMAGE_NAME%:%TAG% .

if %errorlevel% equ 0 (
    echo ✅ 빌드 성공!
    
    echo 📤 Docker Hub에 푸시 중...
    docker push %DOCKER_USERNAME%/%IMAGE_NAME%:%TAG%
    
    if %errorlevel% equ 0 (
        echo ✅ 푸시 완료!
        echo 🎉 이미지: %DOCKER_USERNAME%/%IMAGE_NAME%:%TAG%
    ) else (
        echo ❌ 푸시 실패!
    )
) else (
    echo ❌ 빌드 실패!
)

pause