from gtts import gTTS
import os

text = "안녕하세요. 저는 5년차 백엔드 개발자 김철수입니다. 주로 자바와 스프링 부트를 사용하여 대용량 트래픽 처리 시스템을 개발했습니다."
tts = gTTS(text=text, lang='ko')
save_path = "c:/WorkSpace/AI_ReNe/tests/fixtures/sample_speech_ko.mp3"
tts.save(save_path)
print(f"Audio file saved to {save_path}")
