#!/usr/bin/env python3
"""
대시보드 테스트 스크립트
"""
import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:3000"

def test_health():
    """헬스 체크 테스트"""
    print("=" * 80)
    print("1. Health Check 테스트")
    print("=" * 80)

    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"상태 코드: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check 성공")
            print(f"   - Status: {data['status']}")
            print(f"   - Service: {data['service']}")
            print(f"   - Timestamp: {data['timestamp']}")
            return True
        else:
            print(f"❌ Health Check 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False


def test_services():
    """서비스 목록 조회 테스트"""
    print("\n" + "=" * 80)
    print("2. Services API 테스트")
    print("=" * 80)

    try:
        response = requests.get(f"{BASE_URL}/api/services")
        print(f"상태 코드: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Services API 성공")
            print(f"   - Success: {data['success']}")
            print(f"   - Count: {data['count']}")

            if data['count'] > 0:
                print(f"\n   서비스 목록:")
                for idx, service in enumerate(data['services'], 1):
                    print(f"\n   [{idx}] {service['name']}")
                    print(f"       - Framework: {service['framework']}")
                    print(f"       - Language: {service['language']}")
                    print(f"       - Status: {service['status']}")
                    print(f"       - Commit: {service['commitSha']}")
                    print(f"       - URL: {service['url']}")
            else:
                print(f"   ⚠️  배포된 서비스가 없습니다.")

            return True
        else:
            print(f"❌ Services API 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False


def test_html():
    """HTML 페이지 접근 테스트"""
    print("\n" + "=" * 80)
    print("3. HTML 페이지 접근 테스트")
    print("=" * 80)

    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"상태 코드: {response.status_code}")

        if response.status_code == 200:
            print(f"✅ HTML 페이지 접근 성공")
            print(f"   - Content-Type: {response.headers.get('content-type', 'N/A')}")
            print(f"   - Content Length: {len(response.text)} bytes")

            # HTML 내용 확인
            if "Delightful Deploy" in response.text:
                print(f"   ✅ 페이지 제목 확인됨")
            if "React" in response.text:
                print(f"   ✅ React 스크립트 확인됨")

            return True
        else:
            print(f"❌ HTML 페이지 접근 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False


def test_dynamodb():
    """DynamoDB 연결 테스트"""
    print("\n" + "=" * 80)
    print("4. DynamoDB 연결 테스트")
    print("=" * 80)

    try:
        import boto3
        from botocore.exceptions import ClientError

        dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')

        # deployment-history 테이블 확인
        try:
            table = dynamodb.Table('delightful-deploy-deployment-history')
            response = table.scan(Limit=1)
            print(f"✅ deployment-history 테이블 접근 성공")
            print(f"   - Item Count: {response.get('Count', 0)}")
        except ClientError as e:
            print(f"⚠️  deployment-history 테이블 접근 실패: {e.response['Error']['Code']}")

        # ai-analysis 테이블 확인
        try:
            table = dynamodb.Table('delightful-deploy-ai-analysis')
            response = table.scan(Limit=1)
            print(f"✅ ai-analysis 테이블 접근 성공")
            print(f"   - Item Count: {response.get('Count', 0)}")
        except ClientError as e:
            print(f"⚠️  ai-analysis 테이블 접근 실패: {e.response['Error']['Code']}")

        return True
    except Exception as e:
        print(f"❌ DynamoDB 연결 오류: {e}")
        return False


def main():
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "대시보드 테스트 스위트" + " " * 35 + "║")
    print("╚" + "=" * 78 + "╝")
    print(f"\n시작 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    results = []

    # 1. Health Check
    results.append(("Health Check", test_health()))

    # 2. Services API
    results.append(("Services API", test_services()))

    # 3. HTML 페이지
    results.append(("HTML Page", test_html()))

    # 4. DynamoDB
    results.append(("DynamoDB", test_dynamodb()))

    # 결과 요약
    print("\n" + "=" * 80)
    print("테스트 결과 요약")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print(f"\n총 {passed}/{total} 테스트 통과")

    if passed == total:
        print("\n🎉 모든 테스트가 성공했습니다!")
        print("\n브라우저에서 접속하세요:")
        print(f"   {BASE_URL}")
        return 0
    else:
        print(f"\n⚠️  {total - passed}개의 테스트가 실패했습니다.")
        return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n테스트가 중단되었습니다.")
        sys.exit(1)
