import boto3
import sys
import argparse
from botocore.exceptions import ClientError

def delete_rules_by_prefix(access_key, secret_key, region, prefix, force=False):
    """
    Delete all EventBridge rules that match the given prefix
    """
    try:
        # Create EventBridge client
        events = boto3.client(
            'events',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        # List all rules
        matching_rules = []
        paginator = events.get_paginator('list_rules')
        
        print("Searching for rules...")
        try:
            for page in paginator.paginate():
                for rule in page['Rules']:
                    if rule['Name'].startswith(prefix):
                        matching_rules.append(rule['Name'])
        except ClientError as e:
            print(f"Error listing rules: {str(e)}")
            sys.exit(1)
        
        if not matching_rules:
            print(f"No rules found with prefix: {prefix}")
            return
            
        print(f"\nFound {len(matching_rules)} rules with prefix '{prefix}':")
        for rule_name in matching_rules:
            print(f"- {rule_name}")
            
        # Confirm deletion unless force flag is set
        if not force:
            confirmation = input("\nWARNING: This will permanently delete these EventBridge rules "
                               "and remove all their targets."
                               "\nAre you sure you want to proceed? (yes/no): ")
            if confirmation.lower() != 'yes':
                print("Operation cancelled")
                return
            
        # Delete each rule
        print("\nDeleting rules...")
        for rule_name in matching_rules:
            try:
                # First, list all targets for the rule
                try:
                    targets_response = events.list_targets_by_rule(Rule=rule_name)
                    targets = targets_response['Targets']
                    
                    if targets:
                        print(f"\nRemoving {len(targets)} targets from rule: {rule_name}")
                        target_ids = [target['Id'] for target in targets]
                        
                        # Remove all targets
                        events.remove_targets(
                            Rule=rule_name,
                            Ids=target_ids,
                            Force=True
                        )
                except ClientError as e:
                    print(f"Error removing targets from rule {rule_name}: {str(e)}")
                    continue
                
                # Then delete the rule
                events.delete_rule(
                    Name=rule_name,
                    Force=True
                )
                print(f"Successfully deleted rule: {rule_name}")
                    
            except ClientError as e:
                print(f"Error deleting rule {rule_name}: {str(e)}")
                
        print("\nRule deletion process complete")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Delete AWS EventBridge rules by prefix')
    parser.add_argument('--access-key', required=True, help='AWS access key')
    parser.add_argument('--secret-key', required=True, help='AWS secret key')
    parser.add_argument('--region', required=True, help='AWS region')
    parser.add_argument('--prefix', required=True, help='Rule name prefix to match')
    parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    delete_rules_by_prefix(
        args.access_key,
        args.secret_key,
        args.region,
        args.prefix,
        args.force
    )

if __name__ == "__main__":
    main()
