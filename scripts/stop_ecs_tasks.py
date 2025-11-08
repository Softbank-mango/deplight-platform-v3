#!/usr/bin/env python3
"""
Stop all ECS tasks to force recreation with VPC endpoints
"""
import boto3

def stop_all_tasks():
    """Stop all tasks in the service to force recreation"""

    ecs = boto3.client('ecs', region_name='ap-northeast-2')

    print("Stopping all ECS tasks...")
    print("=" * 80)

    try:
        # List all tasks
        task_arns = ecs.list_tasks(
            cluster='delightful-deploy-cluster',
            serviceName='delightful-deploy-service'
        )

        if task_arns.get('taskArns'):
            print(f"Found {len(task_arns['taskArns'])} tasks to stop")
            print()

            for task_arn in task_arns['taskArns']:
                task_id = task_arn.split('/')[-1]
                print(f"Stopping task: {task_id}")

                ecs.stop_task(
                    cluster='delightful-deploy-cluster',
                    task=task_arn,
                    reason='Forcing recreation with VPC endpoints'
                )

            print()
            print("✅ All tasks stopped")
            print("   ECS service will automatically create new tasks")
            print("   New tasks will use the VPC endpoints for AWS service access")
            print()

        else:
            print("No tasks found to stop")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    stop_all_tasks()
