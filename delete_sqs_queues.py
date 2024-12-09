import boto3
import sys
import argparse

def delete_queues_by_prefix(access_key, secret_key, region, prefix):
    """
    Delete all SQS queues that match the given prefix
    
    Args:
        access_key (str): AWS access key
        secret_key (str): AWS secret key
        region (str): AWS region
        prefix (str): Prefix to match queue names against
    """
    try:
        # Create SQS client
        sqs = boto3.client(
            'sqs',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        # List all queues with the given prefix
        response = sqs.list_queues(QueueNamePrefix=prefix)
        
        if 'QueueUrls' not in response:
            print(f"No queues found with prefix: {prefix}")
            return
            
        queue_urls = response['QueueUrls']
        
        if not queue_urls:
            print(f"No queues found with prefix: {prefix}")
            return
            
        print(f"Found {len(queue_urls)} queues with prefix '{prefix}':")
        for queue_url in queue_urls:
            print(f"- {queue_url}")
            
        # Confirm deletion
        confirmation = input("\nAre you sure you want to delete these queues? (yes/no): ")
        if confirmation.lower() != 'yes':
            print("Operation cancelled")
            return
            
        # Delete each queue
        for queue_url in queue_urls:
            try:
                sqs.delete_queue(QueueUrl=queue_url)
                print(f"Successfully deleted queue: {queue_url}")
            except Exception as e:
                print(f"Error deleting queue {queue_url}: {str(e)}")
                
        print("\nQueue deletion complete")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Delete AWS SQS queues by prefix')
    parser.add_argument('--access-key', required=True, help='AWS access key')
    parser.add_argument('--secret-key', required=True, help='AWS secret key')
    parser.add_argument('--region', required=True, help='AWS region')
    parser.add_argument('--prefix', required=True, help='Queue name prefix to match')
    
    args = parser.parse_args()
    
    delete_queues_by_prefix(
        args.access_key,
        args.secret_key,
        args.region,
        args.prefix
    )

if __name__ == "__main__":
    main()
