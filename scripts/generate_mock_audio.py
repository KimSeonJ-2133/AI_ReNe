
import os
import sys
from pathlib import Path
from openai import OpenAI

# 프로젝트 루트 경로 설정
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# config 모듈에서 설정 로드
from src.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# 저장 경로 설정
OUTPUT_DIR = project_root / "data" / "mock_interview_audio"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 면접 시나리오 (JD: 스타트업 풀스택 개발자 - React/Node.js)
# role: 'interviewer' (면접관) 또는 'candidate' (지원자)
# text: 대사 내용
scenario = [
    {
        "role": "interviewer",
        "text": "안녕하세요. 저희 스타트업 풀스택 개발자 포지션에 지원해 주셔서 감사합니다. 먼저 간단하게 자기소개 부탁드립니다."
    },
    {
        "role": "candidate",
        "text": "안녕하세요. 저는 사용자 경험을 중요하게 생각하는 3년 차 풀스택 개발자입니다. 이전 직장에서는 React와 Node.js를 활용하여 이커머스 플랫폼의 백오피스 시스템을 구축한 경험이 있습니다. 프론트엔드와 백엔드를 아우르며 주도적으로 서비스를 만들어가고 싶어 지원하게 되었습니다."
    },
    {
        "role": "interviewer",
        "text": "반갑습니다. Node.js를 사용하셨다고 했는데, Node.js의 이벤트 루프(Event Loop)가 어떻게 동작하는지, 그리고 싱글 스레드 환경에서 어떻게 비동기 작업을 처리하는지 설명해 주실 수 있나요?"
    },
    {
        "role": "candidate",
        "text": "네, Node.js는 싱글 스레드 기반이지만 libuv 라이브러리를 통해 비동기 I/O를 지원합니다. 이벤트 루프는 Call Stack이 비어있을 때 Task Queue에 있는 콜백 함수들을 가져와 실행하는 방식으로 동작합니다. 무거운 작업은 워커 스레드 풀에 위임하여 메인 스레드가 차단되지 않도록 처리합니다."
    },
    {
        "role": "interviewer",
        "text": "정확하게 이해하고 계시네요. 그럼 프론트엔드 쪽 질문도 드릴게요. React를 사용하시면서 상태 관리는 주로 어떤 라이브러리를 사용하셨고, 그 이유는 무엇인가요?"
    },
    {
        "role": "candidate",
        "text": "초기에는 Redux를 사용했지만, 보일러플레이트 코드가 많아 최근 프로젝트에서는 Recoil과 React Query를 도입했습니다. 서버 상태는 React Query로 캐싱 및 동기화를 처리하고, 클라이언트의 전역 상태는 Recoil로 가볍게 관리하는 방식이 개발 생산성 측면에서 훨씬 효율적이었습니다."
    },
    {
        "role": "interviewer",
        "text": "좋은 접근이네요. 저희는 AWS Lambda를 활용한 서버리스 아키텍처도 일부 도입하고 있는데, 혹시 서버리스 환경에서의 개발 경험이 있으신가요?"
    },
    {
        "role": "candidate",
        "text": "실무에서 대규모로 운영해 본 경험은 없지만, 개인 프로젝트에서 이미지 리사이징 기능을 AWS Lambda와 S3 트리거를 이용해 구현해 본 적이 있습니다. 서버 관리에 대한 부담 없이 비즈니스 로직에만 집중할 수 있다는 점이 인상 깊었습니다."
    },
    {
        "role": "interviewer",
        "text": "솔직한 답변 감사합니다. 마지막으로 협업 방식에 대해 여쭤보고 싶은데요. 동료 개발자와 기술적인 의견 충돌이 발생했을 때 어떻게 해결하시는 편인가요?"
    },
    {
        "role": "candidate",
        "text": "저는 '왜' 그렇게 생각하는지 근거를 공유하는 것을 중요하게 생각합니다. 단순히 제 주장을 고집하기보다, 각 방식의 장단점을 정리하여 팀원들과 논의하고, 프로젝트의 상황과 목표에 가장 부합하는 결정을 내리려고 노력합니다. 코드 리뷰를 통해 서로 배우는 문화도 지향합니다."
    }
]

def generate_audio():
    print(f"Generating audio files in {OUTPUT_DIR}...")
    
    for i, turn in enumerate(scenario):
        role = turn["role"]
        text = turn["text"]
        
        # 역할에 따른 목소리 설정
        # alloy, echo, fable, onyx, nova, shimmer
        voice = "onyx" if role == "interviewer" else "echo"
        
        filename = f"{i+1:02d}_{role}.mp3"
        filepath = OUTPUT_DIR / filename
        
        print(f"[{i+1}/{len(scenario)}] Generating {role} audio: {text[:30]}...")
        
        try:
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            
            response.stream_to_file(filepath)
            print(f" -> Saved to {filename}")
            
        except Exception as e:
            print(f" -> Error: {e}")

    print("\nAll audio files generated successfully!")

if __name__ == "__main__":
    generate_audio()
