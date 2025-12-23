#모듈 정의 : 기업 채용 공고(JD) 파일 업로드 및 파싱 처리 - Service Module
#연결 모듈 : src/api/endpoints/main.py (API),
#  src/agents/company_jd_parser_agent.py (Agent)

import os
from datetime import datetime
from typing import Dict, Any, Optional, Union
from fastapi import UploadFile
from sqlalchemy.orm import Session

from src.utils.file_storage_utils import save_uploaded_file, validate_file_extension
from src.agents.tools.file_text_extractor import extract_text_from_file
from src.agents.company_jd_parser_agent import parse_jd_with_llm, classify_company_doc
from src.schemas.company_schemas.company_file_upload_schemas import JDUploadResponse, CompanyIntroUploadResponse
from services.rag_service import company_rag_service
# from src.models.recruitment import RecruitmentNotice  # [가상 모델] 추후 구현 필요


async def process_company_file_upload(
    session_id: str,
    file_type: str,
    file: UploadFile,
    user_id: int,
    db: Session = None
) -> Union[JDUploadResponse, CompanyIntroUploadResponse]:
    """
    기업 문서 업로드 통합 처리 (기업 소개서 또는 채용 공고 자동 분류)
    """
    # 1. 파일 검증
    allowed_extensions = [".pdf", ".docx", ".txt"]
    if not validate_file_extension(file.filename, allowed_extensions):
        raise ValueError(f"지원하지 않는 파일 형식입니다: {file.filename}")
    
    # 2. 파일 저장 (임시로 company_docs에 저장)
    user_folder = str(user_id)
    file_path = await save_uploaded_file(
        file = file,
        user_id = user_folder,
        file_type = "company_docs"
    )
    
    # 3. 텍스트 추출
    try:
        text_content = extract_text_from_file(file_path)
        print(f"[INFO] 텍스트 추출 완료: {len(text_content)} 글자")
    except Exception as e:
        raise RuntimeError(f"텍스트 추출 실패: {str(e)}")
        
    # 4. 문서 분류
    print(f"[INFO] 문서 분류 시작...")
    classification = classify_company_doc(text_content)
    doc_type = classification["doc_type"]
    job_group_name = classification.get("job_group")
    print(f"[INFO] 문서 분류 결과: {doc_type} (Job Group: {job_group_name})")
    
    if doc_type == "COMPANY_INTRO":
        return await _handle_company_intro(user_id, text_content, file_path, db)
    else:
        # RECRUITMENT_NOTICE
        return await _handle_recruitment_notice(user_id, job_group_name, text_content, file_path, file.filename, db)


async def _handle_company_intro(company_id: int, text_content: str, file_path: str, db: Session) -> CompanyIntroUploadResponse:
    from src.models.user import Company
    from src.models.document import CompanyIntroduction
    from fastapi import HTTPException
    
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail=f"기업을 찾을 수 없습니다. (ID: {company_id})")
        
    # 기존 소개서가 있으면 업데이트, 없으면 생성
    intro = db.query(CompanyIntroduction).filter(CompanyIntroduction.company_id == company_id).first()
    if intro:
        intro.markdown_content = text_content
    else:
        intro = CompanyIntroduction(
            company_id=company_id,
            markdown_content=text_content
        )
        db.add(intro)
        
    db.commit()
    db.refresh(intro)
    
    file_id = f"comp_intro_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return CompanyIntroUploadResponse(
        file_id=file_id,
        markdown_content=text_content,
        created_at=intro.created_at.isoformat() if intro.created_at else datetime.now().isoformat()
    )


async def _handle_recruitment_notice(company_id: int, job_group_name: str, text_content: str, file_path: str, filename: str, db: Session) -> JDUploadResponse:
    # 1. LLM 파싱 (JRS)
    try:
        parsing_result = parse_jd_with_llm(
            text_content = text_content,
            file_type = os.path.splitext(filename)[1][1:]
        )
        print(f"[INFO] JRS 파싱 완료 - Min: {parsing_result['min_rcs_level']}, Target: {parsing_result['target_rcs_level']}")
    except Exception as e:
        raise RuntimeError(f"JRS 파싱 실패: {str(e)}")
    
    file_id = f"comp_jd_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # 2. DB 저장
    if db:
        from src.models.user import Company, JobGroup
        from src.models.document import RecruitmentNotice
        from fastapi import HTTPException
        
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail=f"기업 정보를 찾을 수 없습니다. (ID: {company_id})")
            
        # JobGroup 확인 및 생성
        target_jg_name = job_group_name if job_group_name else "기본 직군"
        job_group = db.query(JobGroup).filter(
            JobGroup.company_id == company.id,
            JobGroup.name == target_jg_name
        ).first()
        
        if not job_group:
            print(f"[Service] JobGroup '{target_jg_name}' 생성 중...")
            job_group = JobGroup(
                company_id=company.id,
                name=target_jg_name
            )
            db.add(job_group)
            db.flush()
            print(f"[Service] JobGroup 생성 완료 - ID: {job_group.id}")
            
        # RecruitmentNotice 저장
        new_notice = RecruitmentNotice(
            job_group_id=job_group.id,
            markdown_content=parsing_result["jrs_markdown"]
        )
        db.add(new_notice)
        db.commit()
        db.refresh(new_notice)
        print(f"[Service] RecruitmentNotice 저장 완료 - ID: {new_notice.id}")
        
        # 3. RAG Vector DB 인덱싱
        print(f"[Service] RAG Vector DB 인덱싱 시작...")
        try:
            metadata = {
                "user_id": company_id,
                "file_type": "company_jd",
                "source": file_path,
                "db_record_id": new_notice.id,
                "job_group": target_jg_name
            }
            company_rag_service.index_document(text_content, metadata)
            print(f"[Service] RAG Vector DB 인덱싱 완료")
        except Exception as rag_error:
            print(f"[Service Warning] RAG 인덱싱 실패 (계속 진행): {rag_error}")
            
    return JDUploadResponse(
        file_id=file_id,
        min_rcs_level=parsing_result["min_rcs_level"],
        target_rcs_level=parsing_result["target_rcs_level"],
        jrs_markdown=parsing_result["jrs_markdown"],
        created_at=datetime.now().isoformat()
    )


def get_parsed_jd(file_id: str) -> Optional[Dict[str, Any]]:
    """
    저장된 JRS 데이터 조회 (DB 연동 후 구현)
    
    Args:
        file_id: 파일 ID
        
    Returns:
        파싱된 JRS 데이터 또는 None
    """
    # TODO: DB에서 조회
    # from src.repositories.company_jd_repository import get_jd_by_file_id
    # return get_jd_by_file_id(file_id)
    
    return None
