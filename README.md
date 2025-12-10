# ReNe Project (Next Recruit) - AI Career Platform

## 1. Project Overview
**ReNe(Next Recruit)**는 언리얼 엔진 5(UE5) 기반의 메타버스 환경과 LLM/RAG 기반의 AI 에이전트를 결합한 차세대 채용 플랫폼입니다.

기존의 텍스트 중심 채용 방식에서 벗어나, **3D 가상 면접(AI Interview)**과 **P2P 실전 면접**을 통해 구직자의 역량을 '데이터(Avatar Stats)'로 증명하고, 기업에게는 검증된 인재를 매칭합니다.

### Key Features
* **AI Profile Generation (시작의 레네)**
    * 사용자와의 대화를 통해 핵심 역량 키워드와 요약 프로필을 자동 생성합니다.
    * 문서 업로드 과정을 거쳤다면, 프로필을 검증 & 갱신하는 역할을 수행합니다.
* **Training Simulation (성장의 레네)**
    * 직무별 모의 면접을 통해, 구직자의 구체적인 기술적 Depth 를 검증합니다.
* **Company Simulation (시련의 레네)**
    * 특정 기업의 RAG 데이터(인재상, JD)를 기반으로 한 고난도 압박 면접을 연습합니다.
* **Real Interview (실전/P2P)**
    * **Company AI:** 실제 채용 공고에 지원하는 AI 면접입니다.
    * **P2P:** 기업 담당자와 구직자 간의 1:1 화상/음성 면접 (녹음 후 AI 분석 리포트 제공).
* **Dashboard (UMG)**
    * AI가 분석한 정량적 데이터(스탯, 리포트)를 시각화하여 제공합니다.

---

## 2. Directory Structure & Naming Convention
본 프로젝트는 **FastAPI**를 기반으로 하며, AI Agent 로직과 API 서버가 통합된 구조입니다.

### Naming Convention
* **Directory:** `snake_case` (e.g., `src`, `tech_npc_agent`)
* **File:** `snake_case` (e.g., `my_agent_logic.py`)

### Folder Structure
```plaintext
/ai_agent_project
├── .env                  # 환경 변수 (API Key, DB Credential) - 절대 Commit 금지
├── .gitignore            # Git 무시 목록 (.env, .venv, data/logs 등)
├── README.md             # 프로젝트 명세 및 실행 가이드
├── requirements.txt      # Python 의존성 패키지 목록
├── .venv/                # 가상 환경
├── data/                 # [External Data] 소스 코드 외 리소스
│   ├── models/           # 학습된 AI 모델 (.pth, .onnx)
│   ├── datasets/         # RAG용 기업 데이터, 학습 데이터셋
│   └── logs/             # 서버 실행 로그
├── notebooks/            # (Optional) 데이터 탐색 및 실험용 Jupyter Notebook
├── scripts/              # (Optional) 전처리, 마이그레이션 스크립트
├── tests/                # 테스트 코드 (Pytest)
└── src/                  # [Application Source Code]
    ├── main.py           # FastAPI Entry Point (App 실행)
    ├── api/              # API Router Definitions
    │   ├── endpoints/    # 개별 도메인별 라우터
    │   │   └── session_api.py
    │   ├── deps.py       # 의존성 주입 (Auth, DB Session)
    │   └── static/       # 정적 파일 (HTML/JS 등 필요 시)
    ├── prompts/          # LLM System Prompts & Templates 관리
    ├── agents/           # [Core AI Logic] 에이전트 로직
    │   ├── base_agent.py # 에이전트 추상 클래스
    │   ├── tools/        # RAG 검색, 외부 API 호출 도구
    │   └── main_agent.py # LLM 호출 및 응답 생성 오케스트레이터
    ├── services/         # 비즈니스 로직 (DB 트랜잭션, 복잡한 연산)
    ├── models/           # DB Entity (SQLAlchemy/Tortoise Model)
    ├── repositories/     # DB CRUD 접근 계층
    ├── core/             # 전역 설정
    │   ├── config.py     # .env 로드 및 App Config
    │   └── database.py   # DB 연결 설정
    ├── schemas/          # Pydantic Schemas (Request/Response DTO)
    └── utils/            # 공통 유틸리티 (Logger, File I/O)
```
ReNe
├─ .python-version
├─ data
│  ├─ chroma_data
│  │  ├─ 1d940ec5-aece-44bf-8dbf-78fc88364fee
│  │  │  ├─ data_level0.bin
│  │  │  ├─ header.bin
│  │  │  ├─ length.bin
│  │  │  └─ link_lists.bin
│  │  ├─ 8555218d-d0d6-42ab-ab47-b3d43aaf8f34
│  │  │  ├─ data_level0.bin
│  │  │  ├─ header.bin
│  │  │  ├─ length.bin
│  │  │  └─ link_lists.bin
│  │  └─ chroma.sqlite3
│  ├─ datasets
│  ├─ fonts
│  │  ├─ MALGUN.TTF
│  │  └─ NanumGothic.ttf
│  ├─ logs
│  ├─ p2p_sessions
│  │  ├─ 검증 결과 요약.pdf
│  │  └─ 면접 결과 요약.png
│  ├─ reports
│  │  └─ report_single_session_v1.pdf
│  ├─ samples
│  │  ├─ hongbeom_portfolio.txt
│  │  ├─ hongbeom_resume.txt
│  │  ├─ shiftup_company_introduction.txt
│  │  └─ shiftup_technical_artist.txt
│  └─ temp
├─ main.py
├─ notebooks
│  └─ trials_rene_graph_test.ipynb
├─ pyproject.toml
├─ README.md
├─ scripts
│  ├─ generate_sample_audio.py
│  ├─ init_data.py
│  └─ test_p2p_realtime.py
├─ src
│  ├─ agents
│  │  ├─ chat_agent.py
│  │  ├─ company_jd_parser_agent.py
│  │  ├─ interview_agent.py
│  │  ├─ p2p_auditor_agent.py
│  │  ├─ seeker_file_upload_agent.py
│  │  ├─ tools
│  │  │  ├─ file_text_extractor.py
│  │  │  └─ __init__.py
│  │  ├─ trials_rene_graph.py
│  │  └─ __init__.py
│  ├─ api
│  │  ├─ deps.py
│  │  ├─ endpoints
│  │  │  ├─ auth.py
│  │  │  ├─ main.py
│  │  │  ├─ meeting_tool
│  │  │  │  └─ meeting_tool_app.py
│  │  │  ├─ p2p_interview_api.py
│  │  │  ├─ rene_interview.py
│  │  │  ├─ temp.py
│  │  │  ├─ trials_rene_api.py
│  │  │  └─ __init__.py
│  │  ├─ static
│  │  │  ├─ index.html
│  │  │  └─ meeting_tool_index.html
│  │  └─ __init__.py
│  ├─ core
│  │  ├─ config.py
│  │  ├─ database.py
│  │  └─ __init__.py
│  ├─ main.py
│  ├─ models
│  │  ├─ document.py
│  │  ├─ interview.py
│  │  ├─ user.py
│  │  ├─ vector_mapping.py
│  │  └─ __init__.py
│  ├─ prompts
│  │  ├─ company_jd_parser_prompts.py
│  │  ├─ Corperate_Recruiter.md
│  │  ├─ Job_Seeker_Avatar.md
│  │  ├─ meeting_tool_prompts.py
│  │  ├─ p2p_auditor_prompts.py
│  │  ├─ ReNe_of_Growth.md
│  │  ├─ ReNe_of_the_Beginning.md
│  │  ├─ seeker_file_upload_tool_prompts.py
│  │  ├─ The_Analyst.md
│  │  ├─ Universal_Evaluator.md
│  │  ├─ ver1.0
│  │  │  ├─ Analyst.md
│  │  │  ├─ Beginning_ReNe.md
│  │  │  ├─ Company_Recruiter.md
│  │  │  ├─ Evaluator.md
│  │  │  ├─ Growth_ReNe.md
│  │  │  ├─ High_Level_Interviewer.md
│  │  │  ├─ Job_Seeker.md
│  │  │  ├─ Low_Level_Interviewer.md
│  │  │  └─ Mid_Level_Interviewer.md
│  │  └─ __init__.py
│  ├─ repositories
│  │  ├─ company_introduction_repository
│  │  │  └─ company_introduction_repository.py
│  │  ├─ company_repository
│  │  │  └─ company_repository.py
│  │  ├─ interview_session_repository
│  │  │  └─ interview_session_repository.py
│  │  ├─ jobseeker_repository
│  │  │  └─ jobseeker_repository.py
│  │  ├─ portfolio_repository
│  │  │  └─ portfolio_repository.py
│  │  ├─ recruitment_notice_repository
│  │  │  └─ recruitment_notice_repository.py
│  │  ├─ rene_interview_repository
│  │  │  └─ rene_interview_repository.py
│  │  ├─ resume_repository
│  │  │  └─ resume_repository.py
│  │  ├─ trials_rene_detail_repository
│  │  │  └─ trials_rene_detail_repository.py
│  │  └─ __init__.py
│  ├─ schemas
│  │  ├─ beginning_rene_schemas
│  │  │  └─ beginning_rene_response_dto.py
│  │  ├─ company_schemas
│  │  │  ├─ company_file_upload_schemas.py
│  │  │  ├─ company_request_dto.py
│  │  │  └─ company_response_dto.py
│  │  ├─ jobseeker_schemas
│  │  │  ├─ jobseeker_request_dto.py
│  │  │  ├─ jobseeker_response_dto.py
│  │  │  └─ seeker_file_upload_schemas.py
│  │  ├─ p2p_schemas
│  │  │  └─ p2p_response_dto.py
│  │  ├─ trials_rene_schemas
│  │  │  ├─ trials_rene_request_dto.py
│  │  │  └─ trials_rene_response_dto.py
│  │  └─ __init__.py
│  ├─ services
│  │  ├─ auth_service
│  │  │  └─ auth_service.py
│  │  ├─ file_upload_service
│  │  │  ├─ company_file_upload_service.py
│  │  │  └─ seeker_file_upload_service.py
│  │  ├─ interview_service
│  │  │  └─ interview_service.py
│  │  ├─ meeting_tool_service
│  │  │  └─ meeting_tool_service.py
│  │  ├─ p2p_service
│  │  │  ├─ buffer_manager.py
│  │  │  └─ p2p_service.py
│  │  ├─ stt_service
│  │  │  ├─ faster_whisper_service.py
│  │  │  ├─ insanely_fast_whisper_service.py
│  │  │  ├─ whisper_korean_stt_service.py
│  │  │  ├─ whisper_large_stt_service.py
│  │  │  └─ __init__.py
│  │  ├─ trials_rene_service
│  │  │  └─ trials_rene_service.py
│  │  ├─ tts_service
│  │  │  ├─ elevenlabs_tts_service.py
│  │  │  ├─ google_tts_service.py
│  │  │  └─ __init__.py
│  │  └─ __init__.py
│  ├─ utils
│  │  ├─ audio_file_utils.py
│  │  ├─ file_storage_utils.py
│  │  ├─ google_utils.py
│  │  ├─ pdf_utils.py
│  │  └─ __init__.py
│  └─ __init__.py
└─ tests
   ├─ fixtures
   │  ├─ jd_backend_senior.txt
   │  ├─ jd_backend_senior_jrs_parsed.md
   │  ├─ jd_startup_fullstack.txt
   │  ├─ jd_startup_fullstack_jrs_parsed.md
   │  ├─ p2p_audit_result_sample_1.json
   │  ├─ p2p_interview_sample_1.txt
   │  ├─ sample_jd.txt
   │  ├─ sample_resume.txt
   │  └─ sample_speech_ko.mp3
   ├─ test_auth_service.py
   ├─ test_file_upload_services.py
   ├─ test_integration_services.py
   ├─ test_interview_service.py
   ├─ test_meeting_tool_service.py
   ├─ test_p2p_auditor.py
   ├─ test_p2p_flow.py
   ├─ test_stt_tts_services.py
   ├─ whisper_stt_test.py
   └─ __init__.py

```