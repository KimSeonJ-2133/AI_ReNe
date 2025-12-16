import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from core.database import SessionLocal
from models.document import Resume, Portfolio
from models.user import Jobseeker

db = SessionLocal()
resume_count = db.query(Resume).count()
portfolio_count = db.query(Portfolio).count()
jobseeker_count = db.query(Jobseeker).count()

print(f"Jobseekers: {jobseeker_count}")
print(f"Resumes: {resume_count}")
print(f"Portfolios: {portfolio_count}")
db.close()
