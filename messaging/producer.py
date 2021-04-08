import os
import json
from kafka import KafkaProducer
from common.errors import UKafkaProduceError


class KafkaPythonProducer(object):
    def __init__(self, bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS')):
        self.producer = KafkaProducer(
            bootstrap_servers=json.loads(bootstrap_servers),
            key_serializer=lambda k: str.encode(k) if k else k,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            retries=5
        )

    def send(self, topic=None, key=None, value=None):
        def on_send_error(excp):
            raise UKafkaProduceError

        self.producer.send(
            topic=topic,
            key=key,
            value=value
        ).add_errback(on_send_error)

    def flush(self):
        self.producer.flush()
