"""
파일 업로드 API 테스트 스크립트

사용법:
python scripts/test_upload_api.py
"""
import requests
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1/upload"

def test_jobseeker_resume():
    """구직자 이력서 업로드 테스트"""
    print("\n[TEST] 구직자 이력서 업로드")
    print("=" * 60)
    
    # 테스트 파일 경로 (fixtures 폴더에 있는 샘플 파일)
    test_file = Path("tests/fixtures/sample_resume.txt")
    
    if not test_file.exists():
        print(f"❌ 테스트 파일이 없습니다: {test_file}")
        return
    
    # 파일명을 규칙에 맞게 변경 (ID_Timestamp 형식)
    files = {
        'file': ('jobplz_2512072109.txt', open(test_file, 'rb'), 'text/plain')
    }
    data = {
        'file_type': 'resume'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/jobseeker-docs", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 업로드 성공!")
            print(f"  - File ID: {result['file_id']}")
            print(f"  - NCS Level: {result['ncs_level']}")
            print(f"  - RCS Level: {result['rcs_level']}")
            print(f"  - Created At: {result['created_at']}")
            print(f"\n  - Markdown 미리보기:")
            print(f"    {result['parsed_markdown'][:200]}...")
        else:
            print(f"❌ 업로드 실패: {response.status_code}")
            print(f"  {response.text}")
    
    except Exception as e:
        print(f"❌ 오류 발생: {e}")


def test_company_jd():
    """기업 채용공고 업로드 테스트"""
    print("\n[TEST] 기업 채용공고 업로드")
    print("=" * 60)
    
    # 테스트 파일 경로
    test_file = Path("tests/fixtures/sample_jd.txt")
    
    if not test_file.exists():
        print(f"❌ 테스트 파일이 없습니다: {test_file}")
        return
    
    # 파일명을 규칙에 맞게 변경
    files = {
        'file': ('companyabc_2512072110.txt', open(test_file, 'rb'), 'text/plain')
    }
    
    try:
        response = requests.post(f"{BASE_URL}/company-docs", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 업로드 성공!")
            print(f"  - File ID: {result['file_id']}")
            print(f"  - Min RCS Level: {result['min_rcs_level']}")
            print(f"  - Target RCS Level: {result['target_rcs_level']}")
            print(f"  - Created At: {result['created_at']}")
            print(f"\n  - JRS Markdown 미리보기:")
            print(f"    {result['jrs_markdown'][:200]}...")
        else:
            print(f"❌ 업로드 실패: {response.status_code}")
            print(f"  {response.text}")
    
    except Exception as e:
        print(f"❌ 오류 발생: {e}")


def main():
    print("\n" + "=" * 60)
    print("파일 업로드 API 테스트")
    print("=" * 60)
    print(f"서버 URL: {BASE_URL}")
    print("\n⚠️  서버가 실행 중이어야 합니다:")
    print("    python src/api/endpoints/main.py")
    print("=" * 60)
    
    # 테스트 실행
    test_jobseeker_resume()
    test_company_jd()
    
    print("\n" + "=" * 60)
    print("테스트 완료")
    print("=" * 60)


if __name__ == "__main__":
    main()
