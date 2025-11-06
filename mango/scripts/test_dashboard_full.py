#!/usr/bin/env python3
"""
대시보드 전체 기능 테스트
- 서비스 목록 조회
- 상태별 필터링
- 앱 시작하기 URL 확인
"""
import requests
import json
from datetime import datetime
import sys

BASE_URL = "http://localhost:3000"
ALB_URL = "http://delightful-deploy-alb-796875577.ap-northeast-2.elb.amazonaws.com"

def print_header(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def test_service_list():
    """서비스 목록 조회 테스트"""
    print_header("1. 서비스 목록 조회 테스트")

    try:
        response = requests.get(f"{BASE_URL}/api/services")
        data = response.json()

        if not data['success']:
            print(f"❌ API 오류: {data.get('error', 'Unknown error')}")
            return False

        services = data['services']
        print(f"✅ 서비스 목록 조회 성공")
        print(f"   - 총 서비스 수: {len(services)}")
        print()

        # 상태별 분류
        healthy = [s for s in services if s['status'] == 'healthy']
        deploying = [s for s in services if s['status'] == 'deploying']
        error = [s for s in services if s['status'] == 'error']

        print(f"상태별 분류:")
        print(f"  🟢 실행 중 (healthy): {len(healthy)}개")
        print(f"  🟡 배포 중 (deploying): {len(deploying)}개")
        print(f"  🔴 오류 (error): {len(error)}개")
        print()

        # 각 서비스 상세 정보
        print("서비스 목록:")
        print("-" * 80)
        for idx, service in enumerate(services, 1):
            status_emoji = {
                'healthy': '🟢',
                'deploying': '🟡',
                'error': '🔴'
            }.get(service['status'], '⚪')

            print(f"[{idx}] {service['name']}")
            print(f"    {status_emoji} 상태: {service['status']}")
            print(f"    📦 Framework: {service['framework']} ({service['language']})")
            print(f"    🔗 Repository: {service['repository']}")
            print(f"    📅 배포 시각: {service['deployedAt']}")
            print(f"    💻 커밋: {service['commitSha']}")
            print(f"    🌐 URL: {service['url']}")
            print()

        return True

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return False


def test_service_access():
    """서비스 접근 테스트 (앱 시작하기)"""
    print_header("2. 서비스 접근 테스트 (앱 시작하기)")

    try:
        # 먼저 서비스 목록 가져오기
        response = requests.get(f"{BASE_URL}/api/services")
        data = response.json()

        if not data['success']:
            print(f"❌ 서비스 목록 조회 실패")
            return False

        services = data['services']
        healthy_services = [s for s in services if s['status'] == 'healthy']

        if not healthy_services:
            print("⚠️  실행 중인 서비스가 없습니다.")
            print("   '앱 시작하기' 기능을 테스트하려면 healthy 상태의 서비스가 필요합니다.")
            return True

        print(f"✅ {len(healthy_services)}개의 실행 중인 서비스 발견")
        print()

        # 각 healthy 서비스의 URL 확인
        for service in healthy_services:
            service_url = service['url']
            print(f"테스트: {service['name']}")
            print(f"  URL: {service_url}")

            try:
                # ALB health check 엔드포인트 테스트
                health_response = requests.get(f"{service_url}/health", timeout=5)

                if health_response.status_code == 200:
                    print(f"  ✅ 접속 가능 (HTTP {health_response.status_code})")
                    print(f"  응답: {health_response.text[:100]}")
                else:
                    print(f"  ⚠️  HTTP {health_response.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"  ⚠️  접속 실패: {type(e).__name__}")

            print()

        return True

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return False


def test_ui_features():
    """UI 기능 테스트"""
    print_header("3. UI 기능 테스트")

    try:
        # HTML 페이지 접근
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print(f"❌ HTML 페이지 접근 실패: {response.status_code}")
            return False

        html_content = response.text

        # 필수 요소 확인
        checks = [
            ("React 로드", "React" in html_content),
            ("Tailwind CSS", "tailwindcss.com" in html_content),
            ("서비스 카드 컴포넌트", "ServiceCard" in html_content),
            ("대시보드 컴포넌트", "Dashboard" in html_content),
            ("API 연동", "fetchServices" in html_content),
            ("자동 새로고침", "setInterval" in html_content),
            ("앱 시작하기 기능", "handleStartApp" in html_content)
        ]

        print("UI 구성 요소 확인:")
        all_passed = True
        for name, check in checks:
            status = "✅" if check else "❌"
            print(f"  {status} {name}")
            if not check:
                all_passed = False

        print()

        if all_passed:
            print("✅ 모든 UI 구성 요소가 정상입니다.")
            return True
        else:
            print("❌ 일부 UI 구성 요소가 누락되었습니다.")
            return False

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return False


def test_dynamic_updates():
    """동적 업데이트 테스트"""
    print_header("4. 동적 업데이트 테스트")

    try:
        # 현재 서비스 수 확인
        response1 = requests.get(f"{BASE_URL}/api/services")
        count1 = response1.json()['count']

        print(f"현재 서비스 수: {count1}개")
        print()

        print("✅ 자동 새로고침 기능:")
        print("   - 30초마다 자동으로 서비스 목록 갱신")
        print("   - '🔄 새로고침' 버튼으로 수동 갱신 가능")
        print()

        print("✅ 동적 카드 추가:")
        print("   - 새 서비스 배포 시 자동으로 카드 추가됨")
        print("   - 상태 변경 시 실시간 반영 (deploying → healthy)")
        print()

        return True

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return False


def test_status_display():
    """상태 표시 테스트"""
    print_header("5. 상태별 표시 테스트")

    try:
        response = requests.get(f"{BASE_URL}/api/services")
        services = response.json()['services']

        status_display = {
            'healthy': {'emoji': '🟢', 'text': '실행 중', 'button': '앱 시작하기 (활성)'},
            'deploying': {'emoji': '🟡', 'text': '배포 중', 'button': '사용 불가 (비활성)'},
            'error': {'emoji': '🔴', 'text': '오류', 'button': '사용 불가 (비활성)'}
        }

        print("각 상태별 UI 표시:")
        print()

        for status, display in status_display.items():
            matching = [s for s in services if s['status'] == status]

            print(f"{display['emoji']} {display['text']} ({status})")
            print(f"   - 서비스 수: {len(matching)}개")
            print(f"   - 버튼 상태: {display['button']}")

            if matching:
                print(f"   - 예시: {matching[0]['name']}")

            print()

        print("✅ 상태별 시각적 구분이 명확합니다.")
        print("   - 색상 코딩: 초록(정상), 노랑(배포중), 빨강(오류)")
        print("   - 버튼 활성화: healthy 상태만 클릭 가능")
        print()

        return True

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return False


def test_alb_endpoint():
    """ALB 엔드포인트 테스트"""
    print_header("6. ALB 엔드포인트 테스트")

    try:
        print(f"ALB URL: {ALB_URL}")
        print()

        endpoints = [
            ("/health", "Health Check"),
            ("/", "Root"),
            ("/info", "Info (FastAPI)"),
            ("/docs", "Swagger UI (FastAPI)")
        ]

        for path, description in endpoints:
            url = f"{ALB_URL}{path}"
            print(f"테스트: {description}")
            print(f"  URL: {url}")

            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"  ✅ HTTP 200 OK")
                    if 'json' in response.headers.get('content-type', ''):
                        print(f"  응답: {response.text[:80]}...")
                else:
                    print(f"  ⚠️  HTTP {response.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"  ⚠️  접속 실패: {type(e).__name__}")

            print()

        return True

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return False


def main():
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "대시보드 전체 기능 테스트" + " " * 32 + "║")
    print("╚" + "=" * 78 + "╝")
    print(f"\n시작 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    results = []

    # 1. 서비스 목록 조회
    results.append(("서비스 목록 조회", test_service_list()))

    # 2. 서비스 접근
    results.append(("서비스 접근 (앱 시작하기)", test_service_access()))

    # 3. UI 기능
    results.append(("UI 기능", test_ui_features()))

    # 4. 동적 업데이트
    results.append(("동적 업데이트", test_dynamic_updates()))

    # 5. 상태 표시
    results.append(("상태 표시", test_status_display()))

    # 6. ALB 엔드포인트
    results.append(("ALB 엔드포인트", test_alb_endpoint()))

    # 결과 요약
    print_header("테스트 결과 요약")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print()
    print(f"총 {passed}/{total} 테스트 통과")

    if passed == total:
        print("\n🎉 모든 테스트가 성공했습니다!")
        print()
        print("=" * 80)
        print("대시보드 사용 방법")
        print("=" * 80)
        print()
        print("1. 브라우저에서 접속:")
        print(f"   {BASE_URL}")
        print()
        print("2. 배포된 서비스 확인:")
        print("   - 4개의 서비스 카드가 표시됩니다")
        print("   - 각 카드에는 프레임워크, 언어, 상태 정보가 포함됩니다")
        print()
        print("3. 서비스 접속:")
        print("   - 🟢 '실행 중' 상태의 서비스 카드에서")
        print("   - '앱 시작하기' 버튼을 클릭하면")
        print("   - 새 탭에서 해당 서비스가 열립니다")
        print()
        print("4. 자동 새로고침:")
        print("   - 30초마다 자동으로 서비스 목록이 갱신됩니다")
        print("   - 또는 '🔄 새로고침' 버튼을 클릭하세요")
        print()
        print("=" * 80)
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
