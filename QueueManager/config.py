import boto3

sqs = boto3.client('sqs')


sqs.purge_queue(QueueUrl ='https://sqs.us-east-1.amazonaws.com/292274580527/sqs_cc106_team_1')

