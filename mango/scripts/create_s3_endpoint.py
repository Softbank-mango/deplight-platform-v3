#!/usr/bin/env python3
"""
Create S3 Gateway VPC Endpoint for ECR image layer access
"""
import boto3

def create_s3_endpoint():
    """Create S3 gateway endpoint for ECR"""

    ec2 = boto3.client('ec2', region_name='ap-northeast-2')

    print("=" * 80)
    print("CREATING S3 GATEWAY VPC ENDPOINT")
    print("=" * 80)
    print()

    vpc_id = 'vpc-0139379503d38f151'

    # Find route tables associated with private subnets
    print("1. Finding route tables for private subnets...")
    try:
        # Get subnet details
        subnets = ec2.describe_subnets(
            SubnetIds=['subnet-08910097cf5286210', 'subnet-067bccb68d144573b']
        )

        route_table_ids = set()
        for subnet in subnets['Subnets']:
            # Get route table associations
            route_tables = ec2.describe_route_tables(
                Filters=[
                    {'Name': 'association.subnet-id', 'Values': [subnet['SubnetId']]}
                ]
            )

            if route_tables['RouteTables']:
                for rt in route_tables['RouteTables']:
                    route_table_ids.add(rt['RouteTableId'])
                    print(f"   Found route table: {rt['RouteTableId']} for subnet {subnet['SubnetId']}")

        # If no explicit associations, find main route table
        if not route_table_ids:
            print("   No explicit associations found, finding main route table...")
            main_route_tables = ec2.describe_route_tables(
                Filters=[
                    {'Name': 'vpc-id', 'Values': [vpc_id]},
                    {'Name': 'association.main', 'Values': ['true']}
                ]
            )
            if main_route_tables['RouteTables']:
                route_table_ids.add(main_route_tables['RouteTables'][0]['RouteTableId'])
                print(f"   Using main route table: {main_route_tables['RouteTables'][0]['RouteTableId']}")

        print(f"\n2. Creating S3 gateway endpoint...")
        if route_table_ids:
            response = ec2.create_vpc_endpoint(
                VpcId=vpc_id,
                ServiceName='com.amazonaws.ap-northeast-2.s3',
                VpcEndpointType='Gateway',
                RouteTableIds=list(route_table_ids),
                TagSpecifications=[
                    {
                        'ResourceType': 'vpc-endpoint',
                        'Tags': [
                            {'Key': 'Name', 'Value': 'delightful-deploy-s3-endpoint'},
                            {'Key': 'Project', 'Value': 'DelightfulDeploy'},
                            {'Key': 'ManagedBy', 'Value': 'Python Script'}
                        ]
                    }
                ]
            )

            print(f"   ✅ S3 endpoint created: {response['VpcEndpoint']['VpcEndpointId']}")
            print(f"   State: {response['VpcEndpoint']['State']}")
            print()
            print("S3 endpoint is now available for ECR image layer downloads!")
            print()

        else:
            print("   ❌ No route tables found!")

    except ec2.exceptions.ClientError as e:
        if 'RouteAlreadyExists' in str(e):
            print("   ℹ️  S3 endpoint may already exist")
        else:
            print(f"   ❌ Error: {e}")

if __name__ == '__main__':
    create_s3_endpoint()
