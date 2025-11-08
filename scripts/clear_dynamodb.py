#!/usr/bin/env python3
"""
DynamoDB 테이블 데이터 초기화
"""
import boto3

dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
deployment_table = dynamodb.Table('delightful-deploy-deployment-history')
ai_analysis_table = dynamodb.Table('delightful-deploy-ai-analysis')

def clear_table(table, key_names):
    """테이블의 모든 항목 삭제"""
    print(f"테이블 초기화: {table.table_name}")

    # 모든 항목 스캔
    response = table.scan()
    items = response.get('Items', [])

    if not items:
        print(f"  ⚠️  테이블이 이미 비어있습니다.")
        return 0

    # 각 항목 삭제
    deleted_count = 0
    for item in items:
        key = {k: item[k] for k in key_names if k in item}
        table.delete_item(Key=key)
        deleted_count += 1

    print(f"  ✅ {deleted_count}개 항목 삭제 완료")
    return deleted_count

def main():
    print("=" * 80)
    print("DynamoDB 데이터 초기화")
    print("=" * 80)
    print()

    # deployment-history 초기화
    count1 = clear_table(deployment_table, ['id'])

    # ai-analysis 초기화
    count2 = clear_table(ai_analysis_table, ['analysis_id', 'timestamp'])

    print()
    print("=" * 80)
    print(f"총 {count1 + count2}개 항목 삭제 완료")
    print("=" * 80)
    print()
    print("대시보드를 새로고침하면 빈 화면이 표시됩니다.")

if __name__ == '__main__':
    main()
