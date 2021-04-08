import os
import faktory
from enum import Enum
import json
from kafka import KafkaConsumer
from common.errors import UTimeoutError
from kafka.structs import OffsetAndMetadata, TopicPartition
from common.helpers.time_helper import timeout


class ConsumerAction(Enum):
    AdInsightUpdate = 'AdInsightUpdate'
    GadUpdate = 'GadUpdate'
    AdAccountUpdate = 'AdAccountUpdate'
    UserAdAccountUpdate = 'UserAdAccountUpdate'


class Consumer:
    def __init__(self, bootstrap_servers, group_id, topics, auto_commit=True):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.topics = topics
        self.auto_commit = auto_commit
        self.consumer = KafkaConsumer(
            group_id=group_id,
            enable_auto_commit=auto_commit,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            bootstrap_servers=bootstrap_servers
        )
        self.consumer.subscribe(topics)

    def run(self):
        for message in self.consumer:
            print('%s:%d:%d: received' % (
                message.topic, message.partition, message.offset))
            try:
                print(message.value)
                self.__handle_action(message)
            except KeyboardInterrupt:
                print('Stopped')
            except UTimeoutError:
                print('timeout')
            except Exception as error:
                print(error)

            if not self.auto_commit:
                meta = self.consumer.partitions_for_topic(message.topic)
                partition = TopicPartition(message.topic, message.partition)
                offset = OffsetAndMetadata(message.offset + 1, meta)
                options = {partition: offset}
                self.consumer.commit(options)

            print('%s:%d:%d: committed\n' % (
                message.topic, message.partition, message.offset))

    @timeout(max_timeout=10)
    def __handle_action(self, message):
        action = message.value['action']
        if action not in list(ConsumerAction.__members__.keys()):
            return
        if action == ConsumerAction.AdInsightUpdate.value:
            worker_type = 'update_ad_insight'
        else:
            worker_type = 'update_gad'

        with faktory.connection(faktory=os.getenv('FAKTORY_URL')) as client:
            datas = message.value['payload']['data']
            for data in datas:
                new_args = dict(message.value)
                new_args['payload']['data'] = data
                client.queue(
                    worker_type, args=(new_args,),
                    queue=worker_type
                )
