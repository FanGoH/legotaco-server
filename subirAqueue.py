import boto3
import json
from time import sleep
import example

sqs = boto3.client('sqs')

load = open('tacos.json', 'r')

data = json.load(load)

while True:
    example.generate_tacos()
    for i in data:
        print("UWU")
        sqs.send_message(QueueUrl = 'https://sqs.us-east-1.amazonaws.com/292274580527/sqs_cc106_team_1', MessageBody = json.dumps(i))   