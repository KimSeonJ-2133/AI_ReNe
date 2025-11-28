# uv pip install torch torchvision torchaudio --torch-backend=cu126
import torch
from transformers import pipeline
import librosa
import os, sys
import tempfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from core.config import settings

class WhisperKoreanSTTService:
    """
    OpenAI Whisper Large V3 한국어 파인튜닝 모델 전용 STT Service
    Singleton 패턴 적용
    최초 한 번 STT 모델 로딩(API 요청이 올 떼마다 계속 메모리에 올렸다 지웠다 하지 않도록 합니다.)
    """
    _instance = None # Singleton - 처음 한 번만 객체 생성

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WhisperKoreanSTTService, cls).__new__(cls) # STTService 객체 생성
            cls._instance.initialize_model() # 모델 로딩 함수 실행
        return cls._instance

    # STT 모델 로딩 함수
    def initialize_model(self):
        print("STT 모델 로딩 중...")
        device = 'cuda' if torch.cuda.is_available() else 'cpu'

        # huggingface의 복잡한 모델 사용 과정을 pipeline으로 자동화 (전처리(tensor로 변환) - 모델 추론 - 후처리(decoding))
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=settings.WHISPER_KOREAN_MODEL_PATH,
            device=device
        )

        print("Whisper Korean 모델 로딩 완료")

    def transcribe(self, audio_bytes: bytes) -> str:
        """
        바이너리 데이터를 임시 파일로 저장 후 librosa로 로드하여 STT 수행
        """
        temp_path = None
        try:
            # 안전하게 임시 파일 생성 (확장자 webm 명시)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name

            print(f"임시 파일 생성됨: {temp_path}")
            print(f"파일 크기: {os.path.getsize(temp_path)} bytes")

            # librosa로 직접 파일 경로를 읽어서 numpy 배열로 변환
            audio, sr = librosa.load(temp_path, sr=16000) 
            print(f"오디오 길이: {len(audio)}, 샘플레이트: {sr}")

            # STT 모델로 한국어로 변환
            result = self.pipe(
                audio,
                chunk_length_s=30,
                batch_size=8,
                return_timestamps=False
            )

            # 결과 서빙
            return result["text"]
        
        except Exception as e:
            print(f"STT 변환 중 에러 발생: {e}")
            import traceback
            traceback.print_exc()  # 상세한 에러 로그 출력
            return ""

        finally:
            # 임시 파일 삭제
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception as e:
                    print(f"임시 파일 삭제 실패: {e}")

# global STTService instance 생성 (import 용)
try:
    stt_service = WhisperKoreanSTTService()
except Exception as e:
    print(f"Whisper Korean 모델 로딩 실패: {e}")



    