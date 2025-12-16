import requests
import os
import json
import time

BASE_URL = "http://localhost:8000/api/v1"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "dummy_files")
RESUME_DIR = os.path.join(DATA_DIR, "resumes")
JD_DIR = os.path.join(DATA_DIR, "jds")

RESUME_FILES = [
    "resume_01_python_backend_senior.txt",
    "resume_02_frontend_react_senior.txt",
    "resume_03_ai_engineer_mid.txt",
    "resume_04_java_spring_senior.txt",
    "resume_05_devops_mid.txt",
    "resume_06_fullstack_mid.txt",
    "resume_07_ios_swift_mid.txt",
    "resume_08_android_kotlin_mid.txt",
    "resume_09_pm_senior.txt",
    "resume_10_junior_python_new.txt"
]

JD_FILES = [
    "jd_01_backend_python.txt",
    "jd_02_frontend_react.txt",
    "jd_03_ai_engineer.txt",
    "jd_04_devops.txt",
    "jd_05_data_analyst.txt"
]

def create_jobseeker(index):
    email = f"seeker_{index:02d}_v2@example.com"
    username = f"seeker_{index:02d}_v2"
    payload = {
        "email": email,
        "password": "password123",
        "name": f"Seeker {index:02d}",
        "phone": f"010-0000-{index:04d}",
        "birthdate": "1990-01-01",
        "gender": "M",
        "address": "Seoul",
        "policy_agree_bool": True
    }
    try:
        response = requests.post(f"{BASE_URL}/jobseeker/signup", json=payload)
        response.raise_for_status()
        print(f"[SUCCESS] Created Jobseeker: {email}")
        return username
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to create Jobseeker {email}: {e}")
        if 'response' in locals():
            if response.status_code in [400, 409]:
                print(f"User {email} might already exist. Proceeding.")
                return username
            print(f"Response: {response.text}")
        return None

def upload_resume(username, index):
    # Read from generated file
    file_index = index - 1
    if file_index < len(RESUME_FILES):
        filename = RESUME_FILES[file_index]
        filepath = os.path.join(RESUME_DIR, filename)
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Rename file to match the expected format for username extraction if needed
            # But the API extracts username from filename: {index}_{username}.{ext}
            upload_filename = f"{index:02d}_{username}.txt"
            
            files = {
                'file': (upload_filename, content, 'text/plain')
            }
            data = {
                'file_type': 'resume',
                'email': f"{username}@example.com"
            }
            
            response = requests.post(f"{BASE_URL}/upload/jobseeker-docs", files=files, data=data)
            response.raise_for_status()
            print(f"[SUCCESS] Uploaded Resume for: {username} (Source: {filename})")
        except Exception as e:
            print(f"[ERROR] Failed to upload resume for {username}: {e}")
            if 'response' in locals() and response.text:
                print(f"Response: {response.text}")
    else:
        print(f"[WARNING] No resume file found for index {index}")

def upload_portfolio(username, index):
    # Read from generated file (using RESUME_FILES as per instruction)
    file_index = index - 1
    if file_index < len(RESUME_FILES):
        filename = RESUME_FILES[file_index]
        filepath = os.path.join(RESUME_DIR, filename)
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            upload_filename = f"{index:02d}_{username}_portfolio.txt"
            
            files = {
                'file': (upload_filename, content, 'text/plain')
            }
            data = {
                'file_type': 'portfolio',
                'email': f"{username}@example.com"
            }
            
            response = requests.post(f"{BASE_URL}/upload/jobseeker-docs", files=files, data=data)
            response.raise_for_status()
            print(f"[SUCCESS] Uploaded Portfolio for: {username} (Source: {filename})")
        except Exception as e:
            print(f"[ERROR] Failed to upload portfolio for {username}: {e}")
            if 'response' in locals() and hasattr(response, 'text') and response.text:
                print(f"Response: {response.text}")
    else:
        print(f"[WARNING] No portfolio file found for index {index}")

def create_company(index):
    email = f"company_{index:02d}_v2@example.com"
    payload = {
        "email": email,
        "password": "password123",
        "name": f"Company {index:02d}",
        "company_scale": "Startup",
        "address": "Seoul",
        "business_number": f"123-45-{index:05d}",
        "policy_agree_bool": True
    }
    try:
        response = requests.post(f"{BASE_URL}/company/signup", json=payload)
        response.raise_for_status()
        data = response.json()
        
        company_id = data.get('id') or data.get('company_id')
        if not company_id:
            print(f"[ERROR] No ID in response for {email}: {data}")
            return None
            
        print(f"[SUCCESS] Created Company: {email} (ID: {company_id})")
        return company_id
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to create Company {email}: {e}")
        if response.text:
            print(f"Response: {response.text}")
        return None

def upload_jd(company_id, index):
    # Read from generated file
    file_index = index - 1
    if file_index < len(JD_FILES):
        filename = JD_FILES[file_index]
        filepath = os.path.join(JD_DIR, filename)
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            upload_filename = f"company_{index:02d}_jd.txt"
            
            files = {
                'file': (upload_filename, content, 'text/plain')
            }
            data = {
                'company_id': company_id
            }
            
            response = requests.post(f"{BASE_URL}/upload/company-docs", files=files, data=data)
            response.raise_for_status()
            print(f"[SUCCESS] Uploaded JD for Company ID: {company_id} (Source: {filename})")
        except Exception as e:
            print(f"[ERROR] Failed to upload JD for Company ID {company_id}: {e}")
            if 'response' in locals() and response.text:
                print(f"Response: {response.text}")
    else:
        print(f"[WARNING] No JD file found for index {index}")

def main():
    print("Starting data seeding via API...")
    
    # 1. Create Job Seekers and Upload Portfolios
    for i in range(1, 11): # 1 to 10
        username = create_jobseeker(i)
        if username:
            # Upload as portfolio as requested
            upload_portfolio(username, i)
        
        time.sleep(0.5) # Prevent rate limiting or overwhelming
        
    # 2. Create Companies and Upload JDs
    for i in range(1, 6): # 1 to 5
        company_id = create_company(i)
        if company_id:
            upload_jd(company_id, i)
        time.sleep(0.5)

    print("Data seeding completed.")

if __name__ == "__main__":
    main()
