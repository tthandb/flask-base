import os
import faktory


def public_to_faktory(payload, worker_type=None):
    if not worker_type:
        worker_type = os.getenv('FAKTORY_QUEUE_NAME')
    with faktory.connection(faktory=os.getenv('FAKTORY_URL')) as client:
        client.queue(
            worker_type, args=(payload,),
            queue=worker_type
        )
