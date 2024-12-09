import boto3
import sys
import argparse
from botocore.exceptions import ClientError

def delete_topics_by_prefix(access_key, secret_key, region, prefix, force=False):
    """
    Delete all SNS topics that match the given prefix
    """
    try:
        # Create SNS client
        sns = boto3.client(
            'sns',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        # List all topics
        matching_topics = []
        paginator = sns.get_paginator('list_topics')
        
        print("Searching for topics...")
        for page in paginator.paginate():
            for topic in page['Topics']:
                topic_arn = topic['TopicArn']
                topic_name = topic_arn.split(':')[-1]
                if topic_name.startswith(prefix):
                    matching_topics.append(topic_arn)
        
        if not matching_topics:
            print(f"No topics found with prefix: {prefix}")
            return
            
        print(f"\nFound {len(matching_topics)} topics with prefix '{prefix}':")
        for topic_arn in matching_topics:
            print(f"- {topic_arn}")
            
        # Confirm deletion unless force flag is set
        if not force:
            confirmation = input("\nWARNING: This will permanently delete these SNS topics "
                               "and all their subscriptions."
                               "\nAre you sure you want to proceed? (yes/no): ")
            if confirmation.lower() != 'yes':
                print("Operation cancelled")
                return
            
        # Delete each topic
        print("\nDeleting topics...")
        for topic_arn in matching_topics:
            try:
                # Get topic subscriptions
                try:
                    subscriptions_paginator = sns.get_paginator('list_subscriptions_by_topic')
                    subscription_count = 0
                    for sub_page in subscriptions_paginator.paginate(TopicArn=topic_arn):
                        subscription_count += len(sub_page['Subscriptions'])
                    print(f"\nTopic {topic_arn} has {subscription_count} subscriptions")
                except ClientError as e:
                    print(f"Could not fetch subscriptions for {topic_arn}: {str(e)}")
                
                # Delete the topic
                sns.delete_topic(TopicArn=topic_arn)
                print(f"Successfully deleted topic: {topic_arn}")
                    
            except ClientError as e:
                print(f"Error deleting topic {topic_arn}: {str(e)}")
                
        print("\nTopic deletion process complete")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Delete AWS SNS topics by prefix')
    parser.add_argument('--access-key', required=True, help='AWS access key')
    parser.add_argument('--secret-key', required=True, help='AWS secret key')
    parser.add_argument('--region', required=True, help='AWS region')
    parser.add_argument('--prefix', required=True, help='Topic name prefix to match')
    parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    delete_topics_by_prefix(
        args.access_key,
        args.secret_key,
        args.region,
        args.prefix,
        args.force
    )

if __name__ == "__main__":
    main()
