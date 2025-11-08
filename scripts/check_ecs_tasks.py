#!/usr/bin/env python3
"""
Check ECS task status and troubleshoot issues
"""
import boto3
import json
from datetime import datetime

def check_ecs_tasks():
    """Check ECS task status and display detailed information"""

    ecs = boto3.client('ecs', region_name='ap-northeast-2')

    print("=" * 80)
    print("ECS TASK STATUS CHECK")
    print("=" * 80)
    print()

    # List tasks in the cluster
    print("1. Listing tasks in cluster...")
    print("-" * 80)
    try:
        task_arns = ecs.list_tasks(
            cluster='delightful-deploy-cluster',
            serviceName='delightful-deploy-service'
        )

        if task_arns.get('taskArns'):
            print(f"   Found {len(task_arns['taskArns'])} tasks")
            print()

            # Describe tasks
            tasks = ecs.describe_tasks(
                cluster='delightful-deploy-cluster',
                tasks=task_arns['taskArns']
            )

            for idx, task in enumerate(tasks.get('tasks', []), 1):
                print(f"Task {idx}:")
                print(f"   Task ARN: {task['taskArn'].split('/')[-1]}")
                print(f"   Status: {task.get('lastStatus', 'UNKNOWN')}")
                print(f"   Desired Status: {task.get('desiredStatus', 'UNKNOWN')}")
                print(f"   Health Status: {task.get('healthStatus', 'UNKNOWN')}")
                print(f"   Created: {task.get('createdAt', 'N/A')}")

                # Check for stop reason
                if 'stoppedReason' in task:
                    print(f"   ⚠️  Stopped Reason: {task['stoppedReason']}")

                # Check containers
                if 'containers' in task:
                    print(f"   Containers:")
                    for container in task['containers']:
                        print(f"      - {container['name']}: {container.get('lastStatus', 'UNKNOWN')}")
                        if 'reason' in container:
                            print(f"        Reason: {container['reason']}")

                # Check for failures
                if task.get('lastStatus') == 'STOPPED' and 'stoppedReason' in task:
                    print(f"   ❌ Task failed: {task['stoppedReason']}")
                elif task.get('lastStatus') == 'RUNNING':
                    print(f"   ✅ Task is running")
                elif task.get('lastStatus') in ['PENDING', 'PROVISIONING']:
                    print(f"   ⏳ Task is starting...")

                print()

        else:
            print("   No tasks found. Checking service events...")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    print()

    # Check service events
    print("2. Service Events (last 10)")
    print("-" * 80)
    try:
        service = ecs.describe_services(
            cluster='delightful-deploy-cluster',
            services=['delightful-deploy-service']
        )

        if service.get('services'):
            events = service['services'][0].get('events', [])[:10]

            for event in events:
                timestamp = event['createdAt'].strftime('%Y-%m-%d %H:%M:%S')
                print(f"   [{timestamp}] {event['message']}")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    print()

    # Check task definition
    print("3. Task Definition Details")
    print("-" * 80)
    try:
        service = ecs.describe_services(
            cluster='delightful-deploy-cluster',
            services=['delightful-deploy-service']
        )

        if service.get('services'):
            task_def_arn = service['services'][0]['taskDefinition']
            print(f"   Task Definition: {task_def_arn.split('/')[-1]}")

            task_def = ecs.describe_task_definition(taskDefinition=task_def_arn)

            container_defs = task_def['taskDefinition']['containerDefinitions']
            for container in container_defs:
                print(f"   Container: {container['name']}")
                print(f"      Image: {container['image']}")
                print(f"      CPU: {task_def['taskDefinition'].get('cpu', 'N/A')}")
                print(f"      Memory: {task_def['taskDefinition'].get('memory', 'N/A')}")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    print()
    print("=" * 80)

if __name__ == '__main__':
    check_ecs_tasks()
