"""
Replicate를 사용한 FLUX LoRA 학습 및 추론 통합 스크립트
"""

import replicate
import requests
import zipfile
import os
from PIL import Image
import time

class FluxLoRATrainer:
    def __init__(self, api_token):
        os.environ["REPLICATE_API_TOKEN"] = api_token
        
    def prepare_dataset(self, image_folder, output_zip="dataset.zip", 
                       trigger_word="TOK", captions=None):
        """
        이미지 폴더를 학습용 ZIP 파일로 변환
        
        Args:
            image_folder: 이미지가 있는 폴더 경로
            output_zip: 출력 ZIP 파일명
            trigger_word: LoRA 트리거 워드
            captions: 이미지별 캡션 딕셔너리 (선택사항)
        """
        with zipfile.ZipFile(output_zip, 'w') as zf:
            for filename in os.listdir(image_folder):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img_path = os.path.join(image_folder, filename)
                    
                    # 이미지 검증 및 변환
                    img = Image.open(img_path)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # ZIP에 이미지 추가
                    zf.write(img_path, f"{filename}")
                    
                    # 캡션 추가
                    base_name = os.path.splitext(filename)[0]
                    if captions and filename in captions:
                        caption = captions[filename]
                    else:
                        caption = f"a photo of {trigger_word}"
                    
                    zf.writestr(f"{base_name}.txt", caption)
        
        print(f"✅ 데이터셋 준비 완료: {output_zip}")
        return output_zip
    
    def train_lora(self, dataset_zip, model_name, trigger_word="TOK", 
                   steps=1000, learning_rate=4e-4):
        """
        LoRA 학습 시작
        
        Args:
            dataset_zip: 학습 데이터 ZIP 파일 경로
            model_name: 저장할 모델 이름
            trigger_word: 트리거 워드
            steps: 학습 스텝 수
            learning_rate: 학습률
        
        Returns:
            학습 ID
        """
        # ZIP 파일을 URL로 업로드 (GitHub, Google Drive, 또는 임시 호스팅)
        # 여기서는 예시로 file.io 사용
        print("📤 데이터셋 업로드 중...")
        
        with open(dataset_zip, 'rb') as f:
            response = requests.post('https://file.io', files={'file': f})
            dataset_url = response.json()['link']
        
        print(f"📦 데이터셋 URL: {dataset_url}")
        
        # 학습 시작
        print("🚀 LoRA 학습 시작...")
        
        training = replicate.trainings.create(
            version="ostris/flux-dev-lora-trainer:4ffd32160efd92e956d39c5338a9b8fbafca58e03f791f6d8011f3e20e8ea6fa",
            input={
                "input_images": dataset_url,
                "trigger_word": trigger_word,
                "steps": steps,
                "learning_rate": learning_rate,
                "rank": 32,
                "optimizer": "adamw8bit",
                "batch_size": 1,
                "resolution": "512,768,1024",
                "autocaption": True,  # 자동 캡션 생성
                "autocaption_prefix": trigger_word,
            },
            destination=f"{os.environ.get('REPLICATE_USERNAME', 'user')}/{model_name}"
        )
        
        print(f"📊 학습 ID: {training.id}")
        print(f"📍 상태: {training.status}")
        print(f"💰 예상 비용: $2-3")
        print(f"⏱️ 예상 시간: 20-30분")
        
        return training
    
    def wait_for_training(self, training):
        """학습 완료 대기"""
        print("\n⏳ 학습 진행 중...")
        
        while training.status not in ["succeeded", "failed", "canceled"]:
            time.sleep(30)
            training.reload()
            print(f"   상태: {training.status} - {time.strftime('%H:%M:%S')}")
        
        if training.status == "succeeded":
            print(f"\n✅ 학습 완료!")
            print(f"🎉 모델: {training.output['version']}")
            return training.output['version']
        else:
            print(f"\n❌ 학습 실패: {training.status}")
            if training.error:
                print(f"   에러: {training.error}")
            return None
    
    def generate_image(self, model_version, prompt, num_images=1):
        """학습된 LoRA로 이미지 생성"""
        output = replicate.run(
            model_version,
            input={
                "prompt": prompt,
                "num_outputs": num_images,
                "aspect_ratio": "1:1",
                "output_format": "png",
                "guidance": 3.5,
                "num_inference_steps": 28,
            }
        )
        
        return output

# 사용 예시
if __name__ == "__main__":
    # 1. 초기화
    trainer = FluxLoRATrainer(api_token="r8_YOUR_TOKEN")
    
    # 2. 데이터셋 준비
    # 이미지 폴더 구조:
    # my_images/
    #   ├── img1.jpg
    #   ├── img2.jpg
    #   └── img3.jpg
    
    dataset = trainer.prepare_dataset(
        image_folder="my_images",
        trigger_word="MYCHAR",
        captions={
            "img1.jpg": "MYCHAR smiling, portrait photo",
            "img2.jpg": "MYCHAR wearing suit, professional photo",
            "img3.jpg": "MYCHAR in casual clothes, outdoor photo"
        }
    )
    
    # 3. 학습 시작
    training = trainer.train_lora(
        dataset_zip=dataset,
        model_name="my-character-flux-lora",
        trigger_word="MYCHAR",
        steps=1000
    )
    
    # 4. 학습 완료 대기
    model_version = trainer.wait_for_training(training)
    
    if model_version:
        # 5. 이미지 생성 테스트
        print("\n🎨 테스트 이미지 생성 중...")
        
        test_prompts = [
            "MYCHAR as a wizard, fantasy art, magical",
            "MYCHAR in cyberpunk style, neon lights",
            "MYCHAR portrait, oil painting style",
            "MYCHAR wearing kimono in japanese garden"
        ]
        
        for i, prompt in enumerate(test_prompts):
            print(f"\n생성 중: {prompt}")
            output = trainer.generate_image(model_version, prompt)
            
            # 이미지 저장
            for j, image_url in enumerate(output):
                img_data = requests.get(image_url).content
                with open(f"output_{i}_{j}.png", "wb") as f:
                    f.write(img_data)
                print(f"   ✅ 저장: output_{i}_{j}.png")
    
    print("\n🎉 완료!")
    print(f"💡 다음에 사용하려면: replicate.run('{model_version}', input={{...}})")