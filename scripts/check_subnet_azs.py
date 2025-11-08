#!/usr/bin/env python3
"""
Check Availability Zones for subnets
"""
import boto3

def check_subnet_azs():
    """Check which AZs the subnets are in"""

    ec2 = boto3.client('ec2', region_name='ap-northeast-2')

    print("=" * 80)
    print("SUBNET AVAILABILITY ZONE CHECK")
    print("=" * 80)
    print()

    public_subnets = ['subnet-01d96ab205a724bcb', 'subnet-0411c23348df162ec']
    private_subnets = ['subnet-08910097cf5286210', 'subnet-067bccb68d144573b']

    print("Public Subnets (ALB):")
    subnets = ec2.describe_subnets(SubnetIds=public_subnets)
    for subnet in subnets['Subnets']:
        print(f"   {subnet['SubnetId']} -> {subnet['AvailabilityZone']}")

    print()
    print("Private Subnets (ECS Tasks):")
    subnets = ec2.describe_subnets(SubnetIds=private_subnets)
    for subnet in subnets['Subnets']:
        print(f"   {subnet['SubnetId']} -> {subnet['AvailabilityZone']}")

    print()
    print("=" * 80)
    print("ISSUE: ALB and ECS tasks must be in the SAME Availability Zones")
    print("=" * 80)

if __name__ == '__main__':
    check_subnet_azs()
