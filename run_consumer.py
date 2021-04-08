import os
import json
from messaging.consumer import Consumer
from ddtrace import tracer


def run_worker():
    environment = os.getenv('ENVIRONMENT', 'development'),
    consumer = Consumer(
        bootstrap_servers=json.loads(os.getenv('KAFKA_BOOTSTRAP_SERVERS')),
        topics=[os.getenv('KAFKA_AD_INSIGHT_TOPIC')],
        group_id=os.getenv('KAFKA_AD_INSIGHT_GROUP_ID')
    )
    consumer.run()


if __name__ == '__main__':
    run_worker()
