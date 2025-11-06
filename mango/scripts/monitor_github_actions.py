#!/usr/bin/env python3
"""
GitHub Actions 워크플로우 실시간 모니터링 스크립트
"""
import requests
import time
import json
import sys
from datetime import datetime

# 설정
REPO_OWNER = "Softbank-mango"
REPO_NAME = "arc_test"
GITHUB_API = "https://api.github.com"
LOG_FILE = "/tmp/github_actions_monitor.log"

# 색상 코드
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

def log(message):
    """로그 파일과 콘솔에 동시 출력"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"

    # 콘솔 출력
    print(log_message)

    # 로그 파일 저장
    with open(LOG_FILE, 'a') as f:
        # ANSI 색상 코드 제거하고 저장
        clean_message = log_message
        for code in [GREEN, YELLOW, RED, BLUE, CYAN, RESET, BOLD]:
            clean_message = clean_message.replace(code, '')
        f.write(clean_message + '\n')

def get_latest_workflow_run():
    """가장 최근 워크플로우 실행 정보 가져오기"""
    url = f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs"
    headers = {"Accept": "application/vnd.github.v3+json"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data['workflow_runs']:
            return data['workflow_runs'][0]
        return None
    except Exception as e:
        log(f"{RED}❌ API 호출 실패: {e}{RESET}")
        return None

def get_workflow_jobs(run_id):
    """워크플로우의 모든 job 정보 가져오기"""
    url = f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}/jobs"
    headers = {"Accept": "application/vnd.github.v3+json"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()['jobs']
    except Exception as e:
        log(f"{RED}❌ Job 정보 가져오기 실패: {e}{RESET}")
        return []

def get_job_logs(job_id):
    """특정 job의 로그 가져오기 (최근 50줄)"""
    url = f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/actions/jobs/{job_id}/logs"
    headers = {"Accept": "application/vnd.github.v3+json"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            # 로그를 줄 단위로 나누고 마지막 50줄만 반환
            lines = response.text.split('\n')
            return '\n'.join(lines[-50:])
        return ""
    except Exception as e:
        return f"로그 가져오기 실패: {e}"

def get_status_icon(status, conclusion=None):
    """상태에 따른 아이콘 반환"""
    if status == "completed":
        if conclusion == "success":
            return f"{GREEN}✅{RESET}"
        elif conclusion == "failure":
            return f"{RED}❌{RESET}"
        elif conclusion == "cancelled":
            return f"{YELLOW}🚫{RESET}"
        elif conclusion == "skipped":
            return f"{CYAN}⏭️{RESET}"
        else:
            return f"{YELLOW}⚠️{RESET}"
    elif status == "in_progress":
        return f"{BLUE}🔄{RESET}"
    elif status == "queued":
        return f"{CYAN}⏳{RESET}"
    else:
        return "❓"

def format_duration(start_time, end_time=None):
    """실행 시간 계산"""
    from dateutil import parser
    start = parser.parse(start_time)
    end = parser.parse(end_time) if end_time else datetime.now(start.tzinfo)
    duration = (end - start).total_seconds()

    if duration < 60:
        return f"{int(duration)}초"
    elif duration < 3600:
        return f"{int(duration/60)}분 {int(duration%60)}초"
    else:
        return f"{int(duration/3600)}시간 {int((duration%3600)/60)}분"

def monitor_workflow():
    """워크플로우 실시간 모니터링"""
    log(f"{BOLD}{'='*70}{RESET}")
    log(f"{BOLD}{CYAN}GitHub Actions 워크플로우 모니터링 시작{RESET}")
    log(f"{BOLD}{'='*70}{RESET}")
    log(f"Repository: {REPO_OWNER}/{REPO_NAME}")
    log(f"로그 파일: {LOG_FILE}")
    log("")

    # 초기 워크플로우 실행 정보 가져오기
    run = get_latest_workflow_run()
    if not run:
        log(f"{RED}❌ 워크플로우 실행을 찾을 수 없습니다.{RESET}")
        return

    run_id = run['id']
    workflow_name = run['name']

    log(f"Workflow: {BOLD}{workflow_name}{RESET}")
    log(f"Run ID: {run_id}")
    log(f"Branch: {run['head_branch']}")
    log(f"Commit: {run['head_sha'][:7]} - {run['head_commit']['message'].split(chr(10))[0][:50]}")
    log(f"URL: {BLUE}{run['html_url']}{RESET}")
    log("")

    previous_jobs_status = {}
    iteration = 0

    while True:
        iteration += 1

        # 워크플로우 실행 정보 업데이트
        run = get_latest_workflow_run()
        if not run or run['id'] != run_id:
            log(f"{YELLOW}⚠️  워크플로우 정보를 가져올 수 없습니다. 재시도 중...{RESET}")
            time.sleep(10)
            continue

        status = run['status']
        conclusion = run.get('conclusion')

        # Job 정보 가져오기
        jobs = get_workflow_jobs(run_id)

        # 헤더
        if iteration % 5 == 1:  # 5번마다 헤더 출력
            log("")
            log(f"{BOLD}{'='*70}{RESET}")
            log(f"{BOLD}워크플로우 상태: {status.upper()}{RESET}")
            log(f"{BOLD}{'='*70}{RESET}")

        # 각 Job 상태 출력
        for job in jobs:
            job_name = job['name']
            job_status = job['status']
            job_conclusion = job.get('conclusion')
            job_id = job['id']

            # 상태 변경된 job만 출력
            job_key = f"{job_id}"
            current_state = f"{job_status}:{job_conclusion}"

            if job_key not in previous_jobs_status or previous_jobs_status[job_key] != current_state:
                icon = get_status_icon(job_status, job_conclusion)
                duration = ""

                if job['started_at']:
                    duration = f" ({format_duration(job['started_at'], job['completed_at'])})"

                log(f"{icon} {BOLD}{job_name}{RESET} - {job_status}{duration}")

                # 실패한 job의 경우 마지막 몇 줄 로그 출력
                if job_conclusion == "failure":
                    log(f"   {RED}실패 원인 확인 중...{RESET}")
                    # 로그는 너무 길 수 있으므로 생략하거나 옵션으로 제공

                previous_jobs_status[job_key] = current_state

        # 워크플로우 완료 확인
        if status == "completed":
            log("")
            log(f"{BOLD}{'='*70}{RESET}")
            if conclusion == "success":
                log(f"{GREEN}{BOLD}🎉 워크플로우 성공적으로 완료!{RESET}")
            elif conclusion == "failure":
                log(f"{RED}{BOLD}❌ 워크플로우 실패{RESET}")
            else:
                log(f"{YELLOW}{BOLD}⚠️  워크플로우 완료 (상태: {conclusion}){RESET}")
            log(f"{BOLD}{'='*70}{RESET}")

            # 최종 요약
            log("")
            log(f"{BOLD}최종 요약:{RESET}")
            for job in jobs:
                icon = get_status_icon(job['status'], job.get('conclusion'))
                duration = format_duration(job['started_at'], job['completed_at']) if job['started_at'] else "N/A"
                log(f"  {icon} {job['name']}: {job.get('conclusion', 'unknown')} ({duration})")

            log("")
            log(f"전체 실행 시간: {format_duration(run['created_at'], run['updated_at'])}")
            log(f"상세 로그: {run['html_url']}")
            log("")
            log(f"로그 파일 저장됨: {LOG_FILE}")
            break

        # 10초마다 업데이트
        time.sleep(10)

if __name__ == "__main__":
    try:
        monitor_workflow()
    except KeyboardInterrupt:
        log(f"\n{YELLOW}모니터링이 사용자에 의해 중단되었습니다.{RESET}")
        log(f"로그 파일: {LOG_FILE}")
        sys.exit(0)
    except Exception as e:
        log(f"\n{RED}오류 발생: {e}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
