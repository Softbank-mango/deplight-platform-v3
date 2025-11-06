#!/usr/bin/env python3
"""
List all subnets in the VPC with their AZs
"""
import boto3

def list_all_subnets():
    """List all subnets in the VPC"""

    ec2 = boto3.client('ec2', region_name='ap-northeast-2')

    vpc_id = 'vpc-0139379503d38f151'

    print("=" * 80)
    print(f"ALL SUBNETS IN VPC {vpc_id}")
    print("=" * 80)
    print()

    subnets = ec2.describe_subnets(
        Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
    )

    az_groups = {}
    for subnet in subnets['Subnets']:
        az = subnet['AvailabilityZone']
        if az not in az_groups:
            az_groups[az] = []

        az_groups[az].append({
            'id': subnet['SubnetId'],
            'cidr': subnet['CidrBlock'],
            'available_ips': subnet['AvailableIpAddressCount']
        })

    for az in sorted(az_groups.keys()):
        print(f"{az}:")
        for subnet in az_groups[az]:
            print(f"   {subnet['id']} - {subnet['cidr']} ({subnet['available_ips']} IPs available)")
        print()

    print("=" * 80)
    print("RECOMMENDATION:")
    print("=" * 80)
    print()
    print("For ALB and ECS tasks to communicate, they must share AZs.")
    print()
    print("Option 1: Use subnets in the same 2 AZs for both ALB and ECS")
    print("Option 2: Update Terraform to use public subnets for ALB and")
    print("          private subnets in the SAME AZs for ECS tasks")
    print()

if __name__ == '__main__':
    list_all_subnets()
