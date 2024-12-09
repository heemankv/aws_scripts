import boto3
import sys
import argparse
from botocore.exceptions import ClientError

def empty_bucket(s3_client, bucket_name):
    """
    Empty an S3 bucket using direct client calls
    """
    try:
        # Delete all object versions (including delete markers)
        print(f"Listing object versions in {bucket_name}...")
        paginator = s3_client.get_paginator('list_object_versions')
        
        try:
            for page in paginator.paginate(Bucket=bucket_name):
                version_ids = []
                if 'Versions' in page:
                    version_ids.extend(
                        {'Key': obj['Key'], 'VersionId': obj['VersionId']}
                        for obj in page['Versions']
                    )
                if 'DeleteMarkers' in page:
                    version_ids.extend(
                        {'Key': obj['Key'], 'VersionId': obj['VersionId']}
                        for obj in page['DeleteMarkers']
                    )
                
                if version_ids:
                    s3_client.delete_objects(
                        Bucket=bucket_name,
                        Delete={'Objects': version_ids}
                    )
                    print(f"Deleted {len(version_ids)} objects/versions")
        except ClientError as e:
            print(f"Error handling versions: {str(e)}")
            
        # Delete remaining objects (if any)
        print(f"Checking for remaining objects in {bucket_name}...")
        paginator = s3_client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name):
            if 'Contents' in page:
                objects_to_delete = [{'Key': obj['Key']} for obj in page['Contents']]
                if objects_to_delete:
                    s3_client.delete_objects(
                        Bucket=bucket_name,
                        Delete={'Objects': objects_to_delete}
                    )
                    print(f"Deleted {len(objects_to_delete)} remaining objects")
        
        return True
        
    except ClientError as e:
        print(f"Error emptying bucket {bucket_name}: {str(e)}")
        return False

def delete_buckets_by_prefix(access_key, secret_key, region, prefix, force=False):
    """
    Delete all S3 buckets that match the given prefix
    """
    try:
        # Create S3 client
        s3 = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        # List all buckets
        response = s3.list_buckets()
        
        # Filter buckets by prefix
        matching_buckets = [
            bucket['Name'] for bucket in response['Buckets']
            if bucket['Name'].startswith(prefix)
        ]
        
        if not matching_buckets:
            print(f"No buckets found with prefix: {prefix}")
            return
            
        print(f"Found {len(matching_buckets)} buckets with prefix '{prefix}':")
        for bucket_name in matching_buckets:
            print(f"- {bucket_name}")
            
        # Confirm deletion unless force flag is set
        if not force:
            confirmation = input("\nWARNING: This will permanently delete all objects in these buckets."
                               "\nAre you sure you want to delete these buckets and their contents? (yes/no): ")
            if confirmation.lower() != 'yes':
                print("Operation cancelled")
                return
            
        # Delete each bucket
        for bucket_name in matching_buckets:
            print(f"\nProcessing bucket: {bucket_name}")
            try:
                # First empty the bucket
                print(f"Emptying bucket {bucket_name}...")
                if empty_bucket(s3, bucket_name):
                    # Then delete the bucket
                    try:
                        s3.delete_bucket(Bucket=bucket_name)
                        print(f"Successfully deleted bucket: {bucket_name}")
                    except ClientError as e:
                        print(f"Error deleting bucket {bucket_name}: {str(e)}")
                else:
                    print(f"Failed to empty bucket {bucket_name}, skipping deletion")
                    
            except ClientError as e:
                print(f"Error processing bucket {bucket_name}: {str(e)}")
                
        print("\nBucket deletion process complete")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Delete AWS S3 buckets by prefix')
    parser.add_argument('--access-key', required=True, help='AWS access key')
    parser.add_argument('--secret-key', required=True, help='AWS secret key')
    parser.add_argument('--region', required=True, help='AWS region')
    parser.add_argument('--prefix', required=True, help='Bucket name prefix to match')
    parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    delete_buckets_by_prefix(
        args.access_key,
        args.secret_key,
        args.region,
        args.prefix,
        args.force
    )

if __name__ == "__main__":
    main()
