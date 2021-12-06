from logic.order import Order
import boto3
import json
import random
import jsons


class SQSManager:

    def __init__(self, ReadeableQueuesUrl: list, ResponseQueueUrl: list):
        self.queues = ReadeableQueuesUrl
        self.responseQueues = ResponseQueueUrl
        self.client = boto3.client('sqs')
        self.iter = 0

    def getOrder(self):
        for idx, sqs in enumerate(self.queues):
            results = self.client.receive_message(
                QueueUrl=sqs)
            if 'Messages' not in results:
                return None
            raw_order = json.loads(results['Messages'][0]['Body'])
            raw_order['handle'] = results['Messages'][0]['ReceiptHandle']
            print(raw_order)
            keys = raw_order.keys()
            if('request_id' in keys or 'start_datetime' in keys or 'orden' in keys):
                return Order(raw_order, idx)

        return None

    def getOrders(self, numberOfMessages):
        Objects = []
        for _ in range(numberOfMessages):
            order = self.getOrder()
            if (order == None):
                break
            else:
                Objects.append(order)
        return Objects

    def getOrderFromQueue(self, queue: int):
        results = self.client.receive_message(
            QueueUrl=self.queues[queue])
        if 'Messages' not in results:
            return None
        raw_order = json.loads(results['Messages'][0]['Body'])
        raw_order['handle'] = results['Messages'][0]['ReceiptHandle']
        keys = raw_order.keys()
        print(raw_order)
        if('request_id' in keys or 'start_datetime' in keys or 'orden' in keys):
            return Order(raw_order, queue)
        return None

    def getOrdersFromQueue(self, numberOfMessages: int, queue: int):
        Objects = []
        for _ in range(numberOfMessages):
            order = self.getOrderFromQueue(queue)
            if (order == None):
                break
            else:
                Objects.append(order)
        return Objects

    def getRandomOrder(self):
        return self.getOrderFromQueue(random.randint(0, len(self.queues)))

    def getNextOrder(self):
        order = self.getOrderFromQueue(self.iter % len(self.queues))
        self.iter += 1
        return order

    def complete_Order(self, order: Order):
        self.client.delete_message(
            QueueUrl=self.queues[0],
            ReceiptHandle=order.get_handle()
        )
        self.log_action("completed", json.loads(jsons.dumps(order)))
        self.client.send_message(
            QueueUrl=self.responseQueues[0],
            MessageBody=jsons.dumps(order)
        )

    def log_action(self, event_name, action_log):
        filename = f"output/completadas.json"
        with open(filename, 'a+'):
            ""
        with open(filename, 'r+') as filein, open(filename, 'r+') as fileout:
            try:
                logs = json.load(filein)
            except:
                logs = {}
            if not event_name in logs:
                logs[event_name] = []
            logs[event_name].append(action_log)
            fileout.write(json.dumps(logs, indent=4))


if __name__ == "__main__":
    queue = ["https://sqs.us-east-1.amazonaws.com/292274580527/sqs_cc106_team_1"]

    Manager = SQSManager(queue, [])

    order = Manager.getOrder()

    print(order.raw_order)
