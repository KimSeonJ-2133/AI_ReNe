import requests
import os
import sys
from sqlalchemy.orm import Session

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from src.core.database import SessionLocal
from src.models.user import Jobseeker
from src.models.document import Resume, Portfolio

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_upload_flow():
    print("="*50)
    print("Starting File Upload Integration Test (Portfolio Mode)")
    print("="*50)

    # 1. Signup (Skipped as per instruction)
    # print(f"[Test] 1. Signing up user: testtemp (Skipped)")

    # 2. Prepare File from Fixture
    fixture_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures", "sample_portfolio.txt"))
    if not os.path.exists(fixture_path):
        print(f"[Error] Fixture file not found: {fixture_path}")
        return

    print(f"\n[Test] 2. Using fixture file: {fixture_path}")

    # 3. Upload File
    # We rename the file in the request to '01_testtemp.txt' so the API can extract the username 'testtemp'
    upload_filename = "01_testtemp.txt"
    print(f"\n[Test] 3. Uploading file as '{upload_filename}' to {BASE_URL}/upload/jobseeker-docs...")
    
    file_id = None
    ncs_level = None
    rcs_level = None

    try:
        with open(fixture_path, "rb") as f:
            # 'file' is the key expected by UploadFile
            files = {"file": (upload_filename, f, "text/plain")}
            # 'file_type' is a Form parameter - CHANGED TO PORTFOLIO
            data = {"file_type": "portfolio"}
            
            resp = requests.post(f"{BASE_URL}/upload/jobseeker-docs", files=files, data=data)
            
            if resp.status_code == 200:
                print("  -> Upload successful!")
                result = resp.json()
                file_id = result.get('file_id')
                ncs_level = result.get('ncs_level')
                rcs_level = result.get('rcs_level')
                
                print("-" * 30)
                print(f"  File ID: {file_id}")
                print(f"  NCS Level: {ncs_level}")
                print(f"  RCS Level: {rcs_level}")
                print("-" * 30)
            else:
                print(f"  -> Upload failed: {resp.status_code}")
                print(f"  -> Response: {resp.text}")
                return # Stop if upload failed
                
    except Exception as e:
        print(f"  -> [Error] Upload request failed: {e}")
        return

    # 4. Verify DB Storage
    print(f"\n[Test] 4. Verifying Database Storage (Portfolio Table)...")
    db: Session = SessionLocal()
    try:
        # 4-1. Check User
        user = db.query(Jobseeker).filter(Jobseeker.email == "testtemp").first()
        if not user:
            print("  -> [Fail] User 'testtemp' not found in DB.")
            return
        print(f"  -> User found: ID {user.id}, Email {user.email}")

        # 4-2. Check Portfolio - CHANGED TO PORTFOLIO
        # We look for the most recent portfolio for this user
        portfolio = db.query(Portfolio).filter(Portfolio.jobseeker_id == user.id).order_by(Portfolio.created_at.desc()).first()
        
        if not portfolio:
            print("  -> [Fail] No Portfolio record found for this user.")
            return
            
        print(f"  -> Portfolio record found: ID {portfolio.id}")
        
        # 4-3. Verify Data
        print(f"  -> DB NCS Level: {portfolio.ncs_level}")
        print(f"  -> DB RCS Level: {portfolio.rcs_level}")
        
        # Check if JSON fields are populated
        print(f"  -> Main Skills (JSON): {len(portfolio.main_skills) if portfolio.main_skills else 0} items")
        print(f"  -> Project Details (JSON): {len(portfolio.project_details) if portfolio.project_details else 0} items")
        
        if portfolio.ncs_level is not None and portfolio.rcs_level is not None:
             print("  -> [Success] DB verification passed! Portfolio saved correctly.")
        else:
             print("  -> [Warning] Levels are None in DB.")

    except Exception as e:
        print(f"  -> [Error] DB verification failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_upload_flow()
