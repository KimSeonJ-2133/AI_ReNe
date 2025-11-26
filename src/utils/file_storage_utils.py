"""파일 저장 및 검증 유틸리티"""
import os
from pathlib import Path
from typing import List, Tuple
from datetime import datetime
from fastapi import UploadFile, HTTPException


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """
    파일 확장자 검증
    
    Args:
        filename: 검증할 파일명
        allowed_extensions: 허용된 확장자 리스트 (예: ['.pdf', '.docx', '.txt'])
    
    Returns:
        bool: 유효한 확장자인 경우 True
    """
    file_ext = Path(filename).suffix.lower()
    return file_ext in allowed_extensions


def get_file_size_mb(file_path: str) -> float:
    """
    파일 크기를 MB 단위로 반환
    
    Args:
        file_path: 파일 경로
    
    Returns:
        float: 파일 크기 (MB)
    """
    size_bytes = os.path.getsize(file_path)
    return size_bytes / (1024 * 1024)


def generate_file_path(user_id: str, file_type: str, filename: str) -> Tuple[str, str]:
    """
    파일 저장 경로 생성
    
    Args:
        user_id: 사용자 ID
        file_type: 파일 타입 ("resume" 또는 "portfolio")
        filename: 원본 파일명
    
    Returns:
        Tuple[str, str]: (전체 경로, 파일명)
            - 전체 경로: data/uploads/{user_id}/{file_type}/
            - 파일명: {timestamp}_{original_filename}
    """
    # 타임스탬프 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 파일명 생성
    new_filename = f"{timestamp}_{filename}"
    
    # 디렉토리 경로 생성
    base_dir = Path("data/uploads") / user_id / file_type
    
    return str(base_dir), new_filename


async def save_uploaded_file(
    file: UploadFile, 
    user_id: str, 
    file_type: str,
    max_size_mb: float = 10.0
) -> str:
    """
    업로드된 파일을 로컬에 저장
    
    Args:
        file: FastAPI UploadFile 객체
        user_id: 사용자 ID
        file_type: 파일 타입 ("resume" 또는 "portfolio")
        max_size_mb: 최대 파일 크기 (MB)
    
    Returns:
        str: 저장된 파일의 전체 경로
    
    Raises:
        HTTPException: 파일 검증 실패 시
    """
    # 확장자 검증
    allowed_extensions = ['.pdf', '.docx', '.doc', '.txt']
    if not validate_file_extension(file.filename, allowed_extensions):
        raise HTTPException(
            status_code = 400,
            detail = f"지원하지 않는 파일 형식입니다. 허용된 확장자: {', '.join(allowed_extensions)}"
        )
    
    # 디렉토리 및 파일명 생성
    dir_path, new_filename = generate_file_path(user_id, file_type, file.filename)
    
    # 디렉토리 생성
    Path(dir_path).mkdir(parents = True, exist_ok = True)
    
    # 전체 파일 경로
    full_path = Path(dir_path) / new_filename
    
    # 파일 저장
    try:
        content = await file.read()
        
        # 파일 크기 검증 (저장 전)
        size_mb = len(content) / (1024 * 1024)
        if size_mb > max_size_mb:
            raise HTTPException(
                status_code = 400,
                detail = f"파일 크기가 너무 큽니다. 최대 {max_size_mb}MB까지 허용됩니다."
            )
        
        with open(full_path, 'wb') as f:
            f.write(content)
        
        return str(full_path)
    
    except Exception as e:
        raise HTTPException(
            status_code = 500,
            detail = f"파일 저장 중 오류가 발생했습니다: {str(e)}"
        )


def cleanup_temp_files(directory: str, older_than_days: int = 7):
    """
    지정된 기간보다 오래된 파일 삭제
    
    Args:
        directory: 정리할 디렉토리 경로
        older_than_days: 삭제 기준 일수
    """
    if not os.path.exists(directory):
        return
    
    current_time = datetime.now()
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            if (current_time - file_time).days > older_than_days:
                try:
                    os.remove(file_path)
                    print(f"삭제됨: {file_path}")
                except Exception as e:
                    print(f"삭제 실패: {file_path}, 오류: {e}")
