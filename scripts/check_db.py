import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from core.database import SessionLocal
from models.user import Jobseeker
from models.document import Resume, Portfolio

def check_db():
    db = SessionLocal()
    try:
        seekers = db.query(Jobseeker).all()
        print(f"Jobseekers: {len(seekers)}")
        for s in seekers:
            print(f"  ID: {s.id}, Name: {s.name}")

        resumes = db.query(Resume).all()
        print(f"Resumes: {len(resumes)}")
        for r in resumes:
            print(f"  ID: {r.id}, JobseekerID: {r.jobseeker_id}")

        portfolios = db.query(Portfolio).all()
        print(f"Portfolios: {len(portfolios)}")
        for p in portfolios:
            print(f"  ID: {p.id}, JobseekerID: {p.jobseeker_id}")

    finally:
        db.close()

if __name__ == "__main__":
    check_db()
