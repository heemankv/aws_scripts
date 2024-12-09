# AWS Resource Deletion Scripts

A collection of Python scripts to help you delete AWS resources by prefix. These scripts provide a safe way to bulk delete various AWS resources that match a specified prefix.

## Available Scripts

1. `delete_rules.py` - Delete EventBridge rules
2. `delete_schedules.py` - Delete EventBridge schedules
3. `delete_queues.py` - Delete SQS queues
4. `delete_buckets.py` - Delete S3 buckets
5. `delete_topics.py` - Delete SNS topics

## Prerequisites

- Python 3.6+
- AWS credentials with appropriate permissions
- Boto3 library

## Installation

1. Clone or download the scripts to your local machine

2. Create a virtual environment and activate it:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install required dependencies:
```bash
pip install boto3
```

## Required IAM Permissions

For each script, you'll need the following permissions:

### EventBridge Rules
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "events:ListRules",
                "events:ListTargetsByRule",
                "events:RemoveTargets",
                "events:DeleteRule"
            ],
            "Resource": "*"
        }
    ]
}
```

### EventBridge Schedules
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "scheduler:ListSchedules",
                "scheduler:DeleteSchedule"
            ],
            "Resource": "*"
        }
    ]
}
```

### SQS Queues
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sqs:ListQueues",
                "sqs:DeleteQueue"
            ],
            "Resource": "*"
        }
    ]
}
```

### S3 Buckets
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBuckets",
                "s3:ListBucketVersions",
                "s3:DeleteObject",
                "s3:DeleteObjectVersion",
                "s3:DeleteBucket"
            ],
            "Resource": "*"
        }
    ]
}
```

### SNS Topics
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sns:ListTopics",
                "sns:ListSubscriptionsByTopic",
                "sns:DeleteTopic"
            ],
            "Resource": "*"
        }
    ]
}
```

## Usage

All scripts follow the same command-line interface pattern:

```bash
python <script_name>.py --access-key YOUR_ACCESS_KEY --secret-key YOUR_SECRET_KEY --region YOUR_REGION --prefix YOUR_PREFIX [--force]
```

### Common Arguments:
- `--access-key`: Your AWS access key
- `--secret-key`: Your AWS secret key
- `--region`: AWS region (e.g., us-east-1)
- `--prefix`: Resource name prefix to match
- `--force`: (Optional) Skip confirmation prompt

### Examples:

Delete EventBridge rules starting with "test-":
```bash
python delete_rules.py --access-key AKIA... --secret-key xxxx... --region us-east-1 --prefix test-
```

Delete EventBridge schedules starting with "dev-":
```bash
python delete_schedules.py --access-key AKIA... --secret-key xxxx... --region us-east-1 --prefix dev-
```

Delete SQS queues starting with "temp-":
```bash
python delete_queues.py --access-key AKIA... --secret-key xxxx... --region us-east-1 --prefix temp-
```

Delete S3 buckets starting with "backup-":
```bash
python delete_buckets.py --access-key AKIA... --secret-key xxxx... --region us-east-1 --prefix backup-
```

Delete SNS topics starting with "notify-":
```bash
python delete_topics.py --access-key AKIA... --secret-key xxxx... --region us-east-1 --prefix notify-
```

## Safety Features

Each script includes several safety features:

1. Lists all resources that will be deleted before proceeding
2. Requires confirmation before deletion (unless --force is used)
3. Handles errors gracefully for each resource
4. Provides detailed feedback during the deletion process
5. Validates AWS credentials before attempting deletions

## Important Notes

1. **S3 Buckets**: The script will attempt to empty buckets before deletion, including versioned objects
2. **EventBridge Rules**: Targets will be removed before deleting rules
3. **SNS Topics**: All subscriptions will be deleted along with the topics
4. **Deletion is permanent**: Use these scripts with caution as deletion cannot be undone
5. **Resource Limits**: Scripts handle pagination for large numbers of resources

## Error Handling

- Scripts will display specific error messages for each failed operation
- The process continues even if individual deletions fail
- A summary of successful and failed deletions is provided at the end

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - Feel free to use and modify these scripts for your needs.
