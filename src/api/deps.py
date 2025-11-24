# 데이터 베이스 세션 생성

from typing import Generator
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from src.core.database import SessionLocal

# DB 세션 생성 (Dependency)
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


    
