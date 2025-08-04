import requests
import json
import base64
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv

# .env 파일 로드 (있는 경우)
load_dotenv()

# API 설정 (환경 변수에서 읽기)
ENDPOINT_ID = os.getenv("RUNPOD_ENDPOINT_ID", "your-endpoint-id")
API_KEY = os.getenv("RUNPOD_API_KEY", "your-runpod-api-key")

if ENDPOINT_ID == "your-endpoint-id" or API_KEY == "your-runpod-api-key":
    print("⚠️ 경고: RUNPOD 설정이 필요합니다!")
    print("1. .env 파일을 만들고 RUNPOD_ENDPOINT_ID와 RUNPOD_API_KEY를 설정하거나")
    print("2. 이 파일에서 직접 값을 수정하세요.")
    exit(1)

url = f"https://api.runpod.io/v2/{ENDPOINT_ID}/runsync"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 요청 데이터
data = {
    "input": {
        "prompt": "a majestic mountain landscape at sunset, highly detailed, professional photography",
        "negative_prompt": "low quality, blurry, oversaturated",
        "width": 1024,
        "height": 1024,
        "steps": 28,
        "guidance_scale": 3.5,
        "upscale": True,
        "upscale_factor": 2
    }
}

# API 호출
print("🚀 이미지 생성 요청 중...")
response = requests.post(url, headers=headers, json=data)
result = response.json()

# 응답 처리
if response.status_code == 200 and "output" in result:
    output = result["output"]
    
    if "image" in output:
        # 이미지 디코딩 및 저장
        img_data = base64.b64decode(output["image"])
        img = Image.open(BytesIO(img_data))
        img.save("output.png")
        
        print(f"✅ 이미지 저장 완료!")
        print(f"📐 크기: {output.get('width', 'Unknown')} x {output.get('height', 'Unknown')}")
        print(f"🎲 시드: {output.get('seed', 'Unknown')}")
    else:
        print("❌ 응답에 이미지가 없습니다:", output)
else:
    print(f"❌ 에러 발생!")
    print(f"상태 코드: {response.status_code}")
    print(f"응답: {result}")