# uv pip install torch torchvision torchaudio --torch-backend=cu126
import torch
from transformers import pipeline
import numpy as np
import librosa
import os, sys, io

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from core.config import settings

class STTService:
    """
    STT Service Class - 최초 한 번 STT 모델 로딩(API 요청이 올 떼마다 계속 메모리에 올렸다 지웠다 하지 않도록 합니다.)
    """
    _instance = None # Singleton - 처음 한 번만 객체 생성

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(STTService, cls).__new__(cls) # STTService 객체 생성
            cls._instance.initialize_model() # 모델 로딩 함수 실행
        return cls._instance

    # STT 모델 로딩 함수
    def initialize_model(self):
        print("STT 모델 로딩 중...")
        device = 'cuda' if torch.cuda.is_available() else 'cpu'

        # huggingface의 복잡한 모델 사용 과정을 pipeline으로 자동화 (전처리(tensor로 변환) - 모델 추론 - 후처리(decoding))
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model = settings.WHISPER_MODEL_PATH,
            device = device
        )
        print("STT 모델 로딩 완료")

    def transcribe(self, audio_bytes: bytes) -> str:
        # 프론트로 받은 bytes 데이터를 인메모리 파일 객체로 변환
        audio_stream = io.BytesIO(audio_bytes)

        # librosa로 모델이 해석할 수 있게 numpy 배열로 변환
        audio, sr = librosa.load(audio_stream, sr=16000)

        # STT 모델로 한국어로 변환
        result = self.pipe(audio, generate_kwargs={"task": "transcribe","language": "korean"})

        # 결과 서빙
        return result["text"]

# global STTService instance 생성 (import 용)
try:
    stt_service = STTService()
except Exception as e:
    print(f"STT 모델 로딩 실패: {e}")



    