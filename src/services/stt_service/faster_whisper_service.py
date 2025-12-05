# uv pip install torch torchvision torchaudio --torch-backend=cu126
import torch
from transformers import pipeline
import librosa
import os, sys
import tempfile
from faster_whisper import WhisperModel

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from core.config import settings

class FasterWhisperService:
    """
    Faster Whisper 전용 STT Service
    Singleton 패턴 적용
    최초 한 번 STT 모델 로딩
    """
    _instance = None # Singleton - 처음 한 번만 객체 생성

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FasterWhisperService, cls).__new__(cls) # STTService 객체 생성
            cls._instance.initialize_model() # 모델 로딩 함수 실행
        return cls._instance

    # STT 모델 로딩 함수
    def initialize_model(self):
        print("Faster-Whisper (Large-v3) STT 모델 로딩 중...")
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        compute_type = "float16" if device == 'cuda' else "int8"
        # huggingface의 복잡한 모델 사용 과정을 pipeline으로 자동화 (전처리(tensor로 변환) - 모델 추론 - 후처리(decoding))
        self.model = WhisperModel(
            model_size_or_path="large-v3",
            device=device,
            compute_type=compute_type
        )

        print(f"Faster-Whisper 모델 로딩 완료 (Device: {device})")

    def transcribe(self, audio_bytes: bytes) -> str:
        """
        바이너리 데이터를 임시 파일로 저장 후 WhisperModel.transcribe로 로드하여 STT 수행
        """
        temp_path = None
        try:
            # 안전하게 임시 파일 생성 (확장자 wav 명시 - pcm_to_wav_bytes가 wav 포맷을 반환하므로)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name

            print(f"임시 파일 생성됨: {temp_path}")
            print(f"파일 크기: {os.path.getsize(temp_path)} bytes")

            # 추론 (librosa 불필요 - 내부적으로 ffmpeg를 사용)
            segments, info = self.model.transcribe(
                temp_path,
                language='ko',
                beam_size=1, # 속도가 최우선이면 1로 설정
                vad_filter=True, # 음성이 없는 구간을 필터링
                vad_parameters=dict(min_silence_duration_ms=500)
            )

            # STT 모델로 한국어로 변환
            text_result = "".join([segment.text for segment in segments])

            # 결과 서빙
            return text_result.strip()
        
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
    stt_service = FasterWhisperService()
except Exception as e:
    print(f"Faster-Whisper 모델 로딩 실패: {e}")



    