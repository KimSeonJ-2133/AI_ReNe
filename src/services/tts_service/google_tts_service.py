#모듈 정의 : Google TTS(gTTS) 기반 기본 TTS 기능 제공 - Service Class
#연결 모듈 : src/services/interview_service/interview_service.py (Service)
from gtts import gTTS
import io

class GoogleTTSService:
    def __init__(self):
        pass
    
    def speak(self, text: str) -> bytes:
        """
        텍스트를 입력받아서 오디오 바이트(bytes)로 변환합니다.
        """

        if not text:
            print("TTS를 진행할 텍스트가 없습니다.")
            return None

        try: 
            tts = gTTS(text=text, lang='ko')

            # 파일을 디스크에 저장하지 않고
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)

            # 포인터를 처음으로 되돌리고 바이트 값을 가져옴
            audio_fp.seek(0)
            return audio_fp.getvalue()
        
        except Exception as e:
            print(f"TTS 변환 중 오류: {e}")
            return None

try:
    tts_service = GoogleTTSService()
except Exception as e:
    print(f"Google TTS 로딩 실패: {e}")