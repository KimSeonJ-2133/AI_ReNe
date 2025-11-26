# test_backend.py
import requests

# 1. 테스트할 API 주소
url = "http://localhost:8000/api/voice-chat"

# 2. 테스트할 오디오 파일 경로 (본인 파일명으로 수정하세요!)
file_path = "test_audio.mp3" 

try:
    # 3. 파일 열어서 전송 (바이너리 모드 'rb')
    with open(file_path, "rb") as f:
        files = {"file": (file_path, f, "audio/mpeg")}
        
        print("서버로 전송 중...")
        response = requests.post(url, files=files)
    
    # 4. 결과 출력
    if response.status_code == 200:
        result = response.json()
        print("\n성공!")
        print(f"사용자: {result['user_text']}")
        print(f"AI응답: {result['ai_response']}")
    else:
        print(f"\n실패 (Status: {response.status_code})")
        print(response.text)

except FileNotFoundError:
    print(f"오류: '{file_path}' 파일을 찾을 수 없습니다.")
except Exception as e:
    print(f"오류 발생: {e}")