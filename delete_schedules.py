import boto3
import sys
import argparse
from botocore.exceptions import ClientError

def delete_schedules_by_prefix(access_key, secret_key, region, prefix, force=False):
    """
    Delete all EventBridge schedules that match the given prefix
    """
    try:
        # Create EventBridge Scheduler client
        scheduler = boto3.client(
            'scheduler',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        # List all schedules
        matching_schedules = []
        paginator = scheduler.get_paginator('list_schedules')
        
        print("Searching for schedules...")
        try:
            for page in paginator.paginate():
                for schedule in page['Schedules']:
                    if schedule['Name'].startswith(prefix):
                        matching_schedules.append({
                            'name': schedule['Name'],
                            'group': schedule.get('GroupName', 'default')  # default group if not specified
                        })
        except ClientError as e:
            print(f"Error listing schedules: {str(e)}")
            sys.exit(1)
        
        if not matching_schedules:
            print(f"No schedules found with prefix: {prefix}")
            return
            
        print(f"\nFound {len(matching_schedules)} schedules with prefix '{prefix}':")
        for schedule in matching_schedules:
            print(f"- {schedule['name']} (Group: {schedule['group']})")
            
        # Confirm deletion unless force flag is set
        if not force:
            confirmation = input("\nWARNING: This will permanently delete these EventBridge schedules."
                               "\nAre you sure you want to proceed? (yes/no): ")
            if confirmation.lower() != 'yes':
                print("Operation cancelled")
                return
            
        # Delete each schedule
        print("\nDeleting schedules...")
        for schedule in matching_schedules:
            try:
                scheduler.delete_schedule(
                    Name=schedule['name'],
                    GroupName=schedule['group']
                )
                print(f"Successfully deleted schedule: {schedule['name']} (Group: {schedule['group']})")
                    
            except ClientError as e:
                print(f"Error deleting schedule {schedule['name']}: {str(e)}")
                
        print("\nSchedule deletion process complete")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Delete AWS EventBridge schedules by prefix')
    parser.add_argument('--access-key', required=True, help='AWS access key')
    parser.add_argument('--secret-key', required=True, help='AWS secret key')
    parser.add_argument('--region', required=True, help='AWS region')
    parser.add_argument('--prefix', required=True, help='Schedule name prefix to match')
    parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    delete_schedules_by_prefix(
        args.access_key,
        args.secret_key,
        args.region,
        args.prefix,
        args.force
    )

if __name__ == "__main__":
    main()
