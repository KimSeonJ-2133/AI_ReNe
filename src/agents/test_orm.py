import sys
import os

# 프로젝트 루트 경로 잡기 (src 모듈 import 위해)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import Column, Integer, String, text
from src.core.database import Base, engine, SessionLocal

# 1. 테스트용 임시 모델(Entity) 정의
# 실제로는 src/models/user.py 같은 곳에 있어야 하지만, 테스트를 위해 여기 작성함
class UserTest(Base):
    __tablename__ = "test_users"  # DB에 생성될 테이블 이름

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    email = Column(String(50))

    # 객체를 출력할 때 예쁘게 보이게 하는 함수 (JPA의 toString 같은 것)
    def __repr__(self):
        return f"<UserTest(id={self.id}, name='{self.name}', email='{self.email}')>"

def run_orm_test():
    print("---ORM 테스트 시작---\n")

    # 2. 테이블 생성 (JPA의 ddl-auto: update 와 비슷)
    # Base를 상속받은 모든 클래스를 찾아서 DB에 테이블을 만듭니다.
    print("1. 테이블 생성 중...")
    Base.metadata.create_all(bind=engine)
    print("'test_users' 테이블 생성 완료!\n")

    # 3. 세션(EntityManager) 열기
    db = SessionLocal()

    try:
        # 4. 데이터 삽입 (INSERT)
        print("2. 데이터 삽입 중...")
        new_user = UserTest(name="테스트유저", email="test@example.com")
        db.add(new_user)  # 영속성 컨텍스트에 저장 (아직 DB엔 안 감)
        db.commit()       # 실제 DB에 저장 (Commit)
        db.refresh(new_user) # DB에서 생성된 ID 등을 다시 가져옴
        print(f"데이터 저장 완료: {new_user}\n")

        # 5. 데이터 조회 (SELECT)
        print("3. 데이터 조회 중...")
        # JPA: userRepository.findByName("테스트유저")
        fetched_user = db.query(UserTest).filter(UserTest.name == "테스트유저").first()
        
        if fetched_user:
            print(f"조회 성공! 가져온 데이터: {fetched_user}\n")
        else:
            print("데이터 조회 실패...\n")

    except Exception as e:
        print(f"에러 발생: {e}")
        db.rollback() # 에러 나면 되돌리기
    finally:
        db.close() # 세션 닫기
        print("테스트 종료")

if __name__ == "__main__":
    run_orm_test()