import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import Column, Integer, String, ForeignKey, text
from sqlalchemy.orm import relationship
from src.core.database import Base, engine, SessionLocal

# ==========================================
# [모델 정의] JPA Entity와 매핑되는 부분
# ==========================================

class StudyUser(Base):
    __tablename__ = "study_users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    
    # 1:N 관계 설정 (JPA의 @OneToMany(mappedBy="owner"))
    # back_populates는 양방향 관계를 맺어줌
    posts = relationship("StudyPost", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(name='{self.name}')>"

class StudyPost(Base):
    __tablename__ = "study_posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    content = Column(String(200))
    
    # FK 설정 (JPA의 @ManyToOne @JoinColumn)
    owner_id = Column(Integer, ForeignKey("study_users.id"))
    
    # 객체 관계 설정
    owner = relationship("StudyUser", back_populates="posts")

    def __repr__(self):
        return f"<Post(title='{self.title}')>"

# ==========================================
# [테스트 시나리오]
# ==========================================

def study_sqlalchemy():
    print("\nSQLAlchemy 심화 학습 시작...\n")
    
    # 0. 테이블 초기화 (기존 거 지우고 새로 만듦)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()

    try:
        # ---------------------------------------------------
        # TEST 1: Dirty Checking (변경 감지) & Update
        # ---------------------------------------------------
        print("--- [TEST 1] Update (Dirty Checking) ---")
        user1 = StudyUser(name="김코딩")
        db.add(user1)
        db.commit() # 일단 저장
        db.refresh(user1)

        print(f"변경 전 이름: {user1.name}")
        
        # JPA처럼 값만 바꾸고 다시 add() 안 함!
        user1.name = "이파이썬" 
        
        # commit() 시점에 변경사항 감지하여 UPDATE 쿼리 날라감
        db.commit() 
        
        # 확인
        updated_user = db.query(StudyUser).filter_by(id=user1.id).first()
        print(f"변경 후 이름: {updated_user.name} (DB 반영 완료)\n")


        # ---------------------------------------------------
        # TEST 2: Transaction Rollback (원자성)
        # ---------------------------------------------------
        print("--- [TEST 2] Rollback 테스트 ---")
        try:
            user2 = StudyUser(name="트랜잭션_실험맨")
            db.add(user2)
            
            # 일부러 에러 발생시킴!
            print("강제로 에러를 발생시킵니다!")
            raise Exception("DB 저장 도중 펑!")
            
            db.commit() # 이 코드는 실행 안 됨
        except Exception as e:
            print(f"에러 잡힘: {e}")
            db.rollback() # 롤백! (없던 일로 만들기)
            print("롤백 완료")

        # 진짜 저장이 안 됐는지 확인
        check_user = db.query(StudyUser).filter_by(name="트랜잭션_실험맨").first()
        if check_user is None:
            print("확인: 데이터가 DB에 저장되지 않았습니다. (성공)\n")


        # ---------------------------------------------------
        # TEST 3: 1:N 관계 저장 (Cascade)
        # ---------------------------------------------------
        print("--- [TEST 3] 1:N 관계 및 Cascade ---")
        # 유저 생성
        parent = StudyUser(name="게시판주인장")
        
        # 글 생성 (부모와 연결)
        post1 = StudyPost(title="첫번째 글", content="안녕", owner=parent)
        post2 = StudyPost(title="두번째 글", content="SQLAlchemy 재밌네", owner=parent)
        
        # 부모(parent)만 저장해도 자식(post1, post2)이 같이 저장되는지?
        db.add(parent)
        db.commit()

        # 확인
        saved_parent = db.query(StudyUser).filter_by(name="게시판주인장").first()
        print(f"저장된 부모: {saved_parent}")
        print(f"자동 저장된 자식 글 개수: {len(saved_parent.posts)}개")
        for p in saved_parent.posts:
            print(f" - 글 제목: {p.title}")

    except Exception as e:
        print(f"치명적 에러: {e}")
    finally:
        db.close()
        print("\n모든 학습 테스트 종료")

if __name__ == "__main__":
    study_sqlalchemy()