import boto3

sqs = "https://sqs.us-east-1.amazonaws.com/292274580527/sqs_cc106_team_1_response"

client=boto3.client('sqs')

res = client.receive_message(QueueUrl=sqs)
print(res)
client.delete_message(QueueUrl=sqs, ReceiptHandle=res["Messages"][0]["ReceiptHandle"])