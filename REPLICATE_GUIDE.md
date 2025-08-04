# Replicate API로 FLUX 사용하기

## 장점
- 모델 다운로드 불필요 (0GB)
- 즉시 사용 가능
- 모든 FLUX 버전 지원
- 관리 불필요

## 단점
- API 비용 발생 ($0.0032/초)
- 인터넷 연결 필요

## 사용법

1. Replicate 계정 생성: https://replicate.com
2. API 토큰 발급
3. 환경 변수 설정:
   ```
   REPLICATE_API_TOKEN=your-token
   ```

4. 코드 예시:
   ```python
   import replicate
   
   output = replicate.run(
       "black-forest-labs/flux-dev",
       input={
           "prompt": "astronaut riding a horse",
           "num_outputs": 1,
           "aspect_ratio": "1:1", 
           "output_format": "webp",
           "output_quality": 80
       }
   )
   print(output)
   ```

## 비용 계산
- 평균 생성 시간: 10-15초
- 이미지당 비용: $0.032-0.048
- 월 1000장: 약 $32-48