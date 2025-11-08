#!/usr/bin/env python3
"""
Check recent Lambda function logs
"""
import boto3
from datetime import datetime, timedelta

def check_lambda_logs():
    """Check recent Lambda logs"""

    logs = boto3.client('logs', region_name='ap-northeast-2')
    log_group = '/aws/lambda/delightful-deploy-ai-analyzer'

    print("=" * 80)
    print("LAMBDA FUNCTION LOGS (Last 5 minutes)")
    print("=" * 80)
    print()

    try:
        # Get recent log streams
        start_time = int((datetime.now() - timedelta(minutes=5)).timestamp() * 1000)

        streams = logs.describe_log_streams(
            logGroupName=log_group,
            orderBy='LastEventTime',
            descending=True,
            limit=3
        )

        if not streams.get('logStreams'):
            print("No recent log streams found")
            return

        for stream in streams['logStreams']:
            stream_name = stream['logStreamName']
            print(f"Log Stream: {stream_name}")
            print("-" * 80)

            # Get log events
            events = logs.get_log_events(
                logGroupName=log_group,
                logStreamName=stream_name,
                startTime=start_time,
                limit=50
            )

            for event in events.get('events', []):
                timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
                message = event['message'].strip()
                print(f"[{timestamp.strftime('%H:%M:%S')}] {message}")

            print()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_lambda_logs()
